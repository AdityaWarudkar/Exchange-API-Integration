from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.models.enums import OrderSide, OrderStatus, OrderType


class OrderCreate(BaseModel):
    exchange: str = Field(default="paper", examples=["paper", "binance", "bybit"])
    symbol: str = Field(examples=["BTCUSDT"])
    side: OrderSide
    type: OrderType
    quantity: float = Field(gt=0)
    price: float | None = Field(default=None, gt=0)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.upper()


class OrderRead(BaseModel):
    id: int
    client_order_id: str
    exchange: str
    symbol: str
    side: OrderSide
    type: OrderType
    status: OrderStatus
    quantity: float
    price: float | None
    filled_quantity: float
    average_fill_price: float | None
    fee: float
    error: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

