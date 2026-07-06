from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base
from src.models.enums import AlertSeverity


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), default=AlertSeverity.info)
    message: Mapped[str] = mapped_column(String(500))
    payload: Mapped[str] = mapped_column(String(2000), default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

