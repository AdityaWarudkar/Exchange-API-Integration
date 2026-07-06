import asyncio
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from src.core.circuit_breaker import CircuitBreaker
from src.core.metrics import LATENCY
from src.models.enums import OrderSide, OrderType


class PublicHttpExchangeClient:
    name = "base"

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.client: httpx.AsyncClient | None = None
        self.breaker = CircuitBreaker()

    async def connect(self) -> None:
        if not self.client:
            self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10)

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            self.client = None

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        await self.connect()
        assert self.client is not None
        start = time.perf_counter()

        async def request() -> dict[str, Any]:
            response = await self.client.get(path, params=params)
            response.raise_for_status()
            return response.json()

        try:
            return await self.breaker.call(request)
        finally:
            LATENCY.labels(operation=f"{self.name}.http").observe(time.perf_counter() - start)

    async def get_balance(self) -> dict[str, Any]:
        return {"exchange": self.name, "mode": "public-data-only", "balances": []}

    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: float | None = None,
    ) -> dict[str, Any]:
        return {
            "exchange": self.name,
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "price": price,
            "status": "rejected",
            "reason": "live order placement is disabled in sandbox",
        }

    async def cancel_order(self, order_id: str, symbol: str) -> dict[str, Any]:
        return {"exchange": self.name, "order_id": order_id, "symbol": symbol, "status": "cancelled"}

    async def get_positions(self) -> list[dict[str, Any]]:
        return []

    async def subscribe_market(self, symbol: str) -> AsyncIterator[dict[str, Any]]:
        previous_price = 0.0
        while True:
            ticker = await self.get_ticker(symbol)
            price = float(ticker["price"])
            yield {
                "exchange": self.name,
                "symbol": symbol,
                "event": "ticker",
                "price": price,
                "latency_ms": ticker.get("latency_ms", 0.0),
                "price_change": price - previous_price if previous_price else 0.0,
            }
            previous_price = price
            await asyncio.sleep(1)

