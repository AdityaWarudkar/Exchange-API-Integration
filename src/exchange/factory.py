from src.config.settings import get_settings
from src.exchange.base import ExchangeClient
from src.exchange.binance.client import BinanceClient
from src.exchange.bybit.client import BybitClient


def get_exchange_client(exchange: str) -> ExchangeClient:
    settings = get_settings()
    normalized = exchange.lower()
    if normalized == "binance":
        return BinanceClient(settings.binance_base_url)
    if normalized == "bybit":
        return BybitClient(settings.bybit_base_url)
    raise ValueError(f"unsupported exchange: {exchange}")

