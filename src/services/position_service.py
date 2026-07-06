from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.positions import PositionRepository


class PositionService:
    def __init__(self, db: AsyncSession) -> None:
        self.positions = PositionRepository(db)

    async def list_positions(self, user_id: int, include_closed: bool = True):
        return await self.positions.list_for_user(user_id, include_closed)

