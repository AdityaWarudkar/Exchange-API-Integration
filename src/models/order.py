from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.models.enums import OrderSide, OrderStatus, OrderType


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_order_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    exchange: Mapped[str] = mapped_column(String(32), default="paper")
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    side: Mapped[OrderSide] = mapped_column(Enum(OrderSide))
    type: Mapped[OrderType] = mapped_column(Enum(OrderType))
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.pending)
    quantity: Mapped[float] = mapped_column(Float)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    filled_quantity: Mapped[float] = mapped_column(Float, default=0.0)
    average_fill_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    fee: Mapped[float] = mapped_column(Float, default=0.0)
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    trades = relationship("Trade", back_populates="order")

