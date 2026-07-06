import time
from typing import Any

from src.exchange.http_client import PublicHttpExchangeClient


class BinanceClient(PublicHttpExchangeClient):
    name = "binance"

    async def get_ticker(self, symbol: str) -> dict[str, Any]:
        start = time.perf_counter()
        data = await self._get("/api/v3/ticker/bookTicker", {"symbol": symbol.upper()})
        return {
            "exchange": self.name,
            "symbol": symbol.upper(),
            "price": (float(data["bidPrice"]) + float(data["askPrice"])) / 2,
            "bid": float(data["bidPrice"]),
            "ask": float(data["askPrice"]),
            "latency_ms": (time.perf_counter() - start) * 1000,
        }

    async def get_orderbook(self, symbol: str, limit: int = 20) -> dict[str, Any]:
        start = time.perf_counter()
        data = await self._get("/api/v3/depth", {"symbol": symbol.upper(), "limit": limit})
        return {
            "exchange": self.name,
            "symbol": symbol.upper(),
            "bids": [[float(price), float(qty)] for price, qty in data["bids"]],
            "asks": [[float(price), float(qty)] for price, qty in data["asks"]],
            "latency_ms": (time.perf_counter() - start) * 1000,
        }

