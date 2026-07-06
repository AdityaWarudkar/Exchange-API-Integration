from src.exchange.factory import get_exchange_client


class MarketService:
    async def get_ticker(self, exchange: str, symbol: str) -> dict:
        client = get_exchange_client(exchange)
        try:
            return await client.get_ticker(symbol)
        finally:
            await client.disconnect()

    async def get_orderbook(self, exchange: str, symbol: str, limit: int = 20) -> dict:
        client = get_exchange_client(exchange)
        try:
            return await client.get_orderbook(symbol, limit)
        finally:
            await client.disconnect()

