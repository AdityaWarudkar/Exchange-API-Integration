from pydantic import BaseModel

from src.models.enums import PositionStatus


class PositionRead(BaseModel):
    id: int
    symbol: str
    status: PositionStatus
    entry_price: float
    current_price: float
    quantity: float
    leverage: float
    margin: float
    liquidation_price: float | None
    realized_pnl: float
    unrealized_pnl: float
    roi: float

    model_config = {"from_attributes": True}

