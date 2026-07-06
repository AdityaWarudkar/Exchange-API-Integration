from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import require_roles
from src.core.security import Role
from src.database.session import get_db
from src.models.user import User
from src.schemas.order import OrderCreate, OrderRead
from src.services.order_service import OrderService

router = APIRouter(tags=["Orders"])


@router.post("/order", response_model=OrderRead)
async def place_order_alias(
    payload: OrderCreate,
    user: User = Depends(require_roles([Role.admin, Role.trader])),
    db: AsyncSession = Depends(get_db),
):
    return await OrderService(db).place_order(user.id, payload)


@router.delete("/order/{order_id}", response_model=OrderRead)
async def cancel_order_alias(
    order_id: int,
    user: User = Depends(require_roles([Role.admin, Role.trader])),
    db: AsyncSession = Depends(get_db),
):
    return await OrderService(db).cancel_order(user.id, order_id)

