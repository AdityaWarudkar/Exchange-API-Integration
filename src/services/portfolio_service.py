from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import get_settings
from src.models.enums import PositionStatus
from src.repositories.balances import BalanceRepository
from src.repositories.positions import PositionRepository
from src.repositories.trades import TradeRepository
from src.schemas.portfolio import PortfolioSummary


class PortfolioService:
    def __init__(self, db: AsyncSession) -> None:
        self.balances = BalanceRepository(db)
        self.positions = PositionRepository(db)
        self.trades = TradeRepository(db)

    async def summary(self, user_id: int) -> PortfolioSummary:
        balance = await self.balances.get_or_create_usdt(user_id, get_settings().paper_starting_balance)
        positions = await self.positions.list_for_user(user_id)
        total_trades, _, today_pnl = await self.trades.stats_for_user(user_id)
        winners = [p for p in positions if p.realized_pnl > 0]
        closed = [p for p in positions if p.status == PositionStatus.closed]
        open_positions = [p for p in positions if p.status == PositionStatus.open]
        winning_percentage = (len(winners) / len(closed) * 100) if closed else 0.0
        unrealized = sum(p.unrealized_pnl for p in open_positions)
        open_market_value = sum(max(p.quantity, 0) * p.current_price for p in open_positions)
        return PortfolioSummary(
            total_balance=balance.total + open_market_value + unrealized,
            available_balance=balance.available,
            locked_balance=balance.locked,
            today_profit=max(today_pnl, 0.0),
            today_loss=abs(min(today_pnl, 0.0)),
            total_trades=total_trades,
            winning_percentage=winning_percentage,
            open_positions=len(open_positions),
            closed_positions=len(closed),
        )
