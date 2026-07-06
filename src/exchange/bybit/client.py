import time
from typing import Any

from src.exchange.http_client import PublicHttpExchangeClient


class BybitClient(PublicHttpExchangeClient):
    name = "bybit"

    async def get_ticker(self, symbol: str) -> dict[str, Any]:
        start = time.perf_counter()
        data = await self._get("/v5/market/tickers", {"category": "linear", "symbol": symbol.upper()})
        item = data["result"]["list"][0]
        bid = float(item["bid1Price"])
        ask = float(item["ask1Price"])
        return {
            "exchange": self.name,
            "symbol": symbol.upper(),
            "price": (bid + ask) / 2,
            "bid": bid,
            "ask": ask,
            "latency_ms": (time.perf_counter() - start) * 1000,
        }

    async def get_orderbook(self, symbol: str, limit: int = 20) -> dict[str, Any]:
        start = time.perf_counter()
        data = await self._get(
            "/v5/market/orderbook",
            {"category": "linear", "symbol": symbol.upper(), "limit": limit},
        )
        book = data["result"]
        return {
            "exchange": self.name,
            "symbol": symbol.upper(),
            "bids": [[float(price), float(qty)] for price, qty in book["b"]],
            "asks": [[float(price), float(qty)] for price, qty in book["a"]],
            "latency_ms": (time.perf_counter() - start) * 1000,
        }

