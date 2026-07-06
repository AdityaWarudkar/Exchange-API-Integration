from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.order import Order
from src.models.trade import Trade


class TradeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, trade: Trade) -> Trade:
        self.db.add(trade)
        await self.db.flush()
        await self.db.refresh(trade)
        return trade

    async def stats_for_user(self, user_id: int) -> tuple[int, float, float]:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        query = (
            select(func.count(Trade.id), func.coalesce(func.sum(Trade.realized_pnl), 0.0))
            .join(Order, Order.id == Trade.order_id)
            .where(Order.user_id == user_id)
        )
        result = await self.db.execute(query)
        total_trades, total_realized = result.one()
        today_result = await self.db.execute(
            select(func.coalesce(func.sum(Trade.realized_pnl), 0.0))
            .join(Order, Order.id == Trade.order_id)
            .where(Order.user_id == user_id, Trade.created_at >= today)
        )
        today_pnl = float(today_result.scalar_one())
        return int(total_trades), float(total_realized), today_pnl
