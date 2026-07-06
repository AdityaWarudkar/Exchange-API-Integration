from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.enums import PositionStatus
from src.models.position import Position


class PositionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_open(self, user_id: int, symbol: str) -> Position | None:
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.symbol == symbol.upper(),
                Position.status == PositionStatus.open,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: int, include_closed: bool = True) -> list[Position]:
        query = select(Position).where(Position.user_id == user_id)
        if not include_closed:
            query = query.where(Position.status == PositionStatus.open)
        result = await self.db.execute(query.order_by(Position.updated_at.desc()))
        return list(result.scalars().all())

    async def add(self, position: Position) -> Position:
        self.db.add(position)
        await self.db.flush()
        await self.db.refresh(position)
        return position

