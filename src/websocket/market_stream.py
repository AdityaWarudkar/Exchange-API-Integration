import asyncio
import time

import structlog

from src.alerts.service import AlertService
from src.config.settings import get_settings
from src.core.metrics import RECONNECTS
from src.exchange.factory import get_exchange_client
from src.models.enums import AlertSeverity
from src.websocket.manager import manager

logger = structlog.get_logger(__name__)


async def stream_market_data(stop_event: asyncio.Event) -> None:
    settings = get_settings()
    alerts = AlertService()
    tasks = [
        asyncio.create_task(_stream_symbol("binance", symbol, stop_event, alerts))
        for symbol in settings.market_symbols
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


async def _stream_symbol(exchange: str, symbol: str, stop_event: asyncio.Event, alerts: AlertService) -> None:
    topic = f"{exchange}:{symbol}"
    reconnect_delay = 1.0
    previous_price = 0.0
    while not stop_event.is_set():
        client = get_exchange_client(exchange)
        try:
            async for event in client.subscribe_market(symbol):
                start = time.perf_counter()
                price = float(event["price"])
                if previous_price:
                    change_pct = abs(price - previous_price) / previous_price * 100
                    if change_pct >= 2:
                        await alerts.publish(
                            "large_price_movement",
                            AlertSeverity.warning,
                            f"{symbol} moved {change_pct:.2f}%",
                            {"symbol": symbol, "change_pct": change_pct},
                        )
                previous_price = price
                event["heartbeat_ts"] = time.time()
                event["server_latency_ms"] = (time.perf_counter() - start) * 1000
                await manager.broadcast(topic, event)
                if stop_event.is_set():
                    break
            reconnect_delay = 1.0
        except Exception as exc:
            logger.warning("market_stream_error", exchange=exchange, symbol=symbol, error=str(exc))
            RECONNECTS.labels(exchange=exchange, symbol=symbol).inc()
            await alerts.publish(
                "connection_lost",
                AlertSeverity.critical,
                f"{exchange} stream lost for {symbol}",
                {"error": str(exc)},
            )
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 30)
        finally:
            await client.disconnect()

