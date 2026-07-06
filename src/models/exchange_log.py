from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class ExchangeLog(Base):
    __tablename__ = "exchange_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange: Mapped[str] = mapped_column(String(32), index=True)
    operation: Mapped[str] = mapped_column(String(64))
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float)
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

