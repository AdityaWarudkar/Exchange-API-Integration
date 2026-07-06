from pydantic import BaseModel


class Ticker(BaseModel):
    exchange: str
    symbol: str
    price: float
    bid: float | None = None
    ask: float | None = None
    latency_ms: float = 0.0


class Orderbook(BaseModel):
    exchange: str
    symbol: str
    bids: list[list[float]]
    asks: list[list[float]]
    latency_ms: float = 0.0

