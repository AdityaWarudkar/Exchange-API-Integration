from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.enums import OrderStatus
from src.models.order import Order


class OrderRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, order: Order) -> Order:
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def get_for_user(self, order_id: int, user_id: int) -> Order | None:
        result = await self.db.execute(select(Order).where(Order.id == order_id, Order.user_id == user_id))
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: int,
        status: OrderStatus | None = None,
        symbol: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Order]:
        query = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        if status:
            query = query.where(Order.status == status)
        if symbol:
            query = query.where(Order.symbol == symbol.upper())
        result = await self.db.execute(query.limit(limit).offset(offset))
        return list(result.scalars().all())

