from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    total_balance: Mapped[float] = mapped_column(Float)
    available_balance: Mapped[float] = mapped_column(Float)
    locked_balance: Mapped[float] = mapped_column(Float)
    today_profit: Mapped[float] = mapped_column(Float, default=0.0)
    today_loss: Mapped[float] = mapped_column(Float, default=0.0)
    total_trades: Mapped[int] = mapped_column(Integer, default=0)
    winning_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    open_positions: Mapped[int] = mapped_column(Integer, default=0)
    closed_positions: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

