from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.balance import Balance


class BalanceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_or_create_usdt(self, user_id: int, starting_balance: float) -> Balance:
        result = await self.db.execute(
            select(Balance).where(Balance.user_id == user_id, Balance.asset == "USDT")
        )
        balance = result.scalar_one_or_none()
        if balance:
            return balance
        balance = Balance(user_id=user_id, asset="USDT", total=starting_balance, available=starting_balance, locked=0.0)
        self.db.add(balance)
        await self.db.flush()
        await self.db.refresh(balance)
        return balance

