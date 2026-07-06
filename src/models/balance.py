from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class Balance(Base):
    __tablename__ = "balances"
    __table_args__ = (UniqueConstraint("user_id", "asset", name="uq_balance_user_asset"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    asset: Mapped[str] = mapped_column(String(16), default="USDT")
    total: Mapped[float] = mapped_column(Float, default=0.0)
    available: Mapped[float] = mapped_column(Float, default=0.0)
    locked: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

