from pydantic import BaseModel


class PortfolioSummary(BaseModel):
    total_balance: float
    available_balance: float
    locked_balance: float
    today_profit: float
    today_loss: float
    total_trades: int
    winning_percentage: float
    open_positions: int
    closed_positions: int

