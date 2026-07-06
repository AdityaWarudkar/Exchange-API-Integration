from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import require_roles
from src.core.security import Role
from src.database.session import get_db
from src.models.user import User
from src.schemas.position import PositionRead
from src.services.position_service import PositionService

router = APIRouter(prefix="/positions", tags=["Positions"])


@router.get("", response_model=list[PositionRead])
async def get_positions(
    include_closed: bool = True,
    user: User = Depends(require_roles([Role.admin, Role.trader, Role.viewer])),
    db: AsyncSession = Depends(get_db),
):
    return await PositionService(db).list_positions(user.id, include_closed)

