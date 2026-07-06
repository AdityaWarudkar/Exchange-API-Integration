from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.models.enums import PositionStatus


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[PositionStatus] = mapped_column(Enum(PositionStatus), default=PositionStatus.open)
    entry_price: Mapped[float] = mapped_column(Float)
    current_price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[float] = mapped_column(Float)
    leverage: Mapped[float] = mapped_column(Float, default=1.0)
    margin: Mapped[float] = mapped_column(Float, default=0.0)
    liquidation_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    realized_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    unrealized_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    roi: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="positions")
