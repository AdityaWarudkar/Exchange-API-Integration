from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import require_roles
from src.core.security import Role
from src.database.session import get_db
from src.models.user import User
from src.schemas.portfolio import PortfolioSummary
from src.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.get("", response_model=PortfolioSummary)
async def get_portfolio(
    user: User = Depends(require_roles([Role.admin, Role.trader, Role.viewer])),
    db: AsyncSession = Depends(get_db),
):
    return await PortfolioService(db).summary(user.id)

