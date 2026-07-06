from fastapi import APIRouter, Query

from src.schemas.market import Orderbook, Ticker
from src.services.market_service import MarketService

router = APIRouter(tags=["Market"])


@router.get("/ticker", response_model=Ticker)
async def ticker(exchange: str = "binance", symbol: str = "BTCUSDT"):
    return await MarketService().get_ticker(exchange, symbol)


@router.get("/orderbook", response_model=Orderbook)
async def orderbook(exchange: str = "binance", symbol: str = "BTCUSDT", limit: int = Query(20, ge=1, le=200)):
    return await MarketService().get_orderbook(exchange, symbol, limit)

