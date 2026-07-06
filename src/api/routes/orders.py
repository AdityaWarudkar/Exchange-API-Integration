from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import require_roles
from src.core.security import Role
from src.database.session import get_db
from src.models.enums import OrderStatus
from src.models.user import User
from src.schemas.order import OrderCreate, OrderRead
from src.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderRead)
async def place_order(
    payload: OrderCreate,
    user: User = Depends(require_roles([Role.admin, Role.trader])),
    db: AsyncSession = Depends(get_db),
):
    return await OrderService(db).place_order(user.id, payload)


@router.get("", response_model=list[OrderRead])
async def list_orders(
    status: OrderStatus | None = None,
    symbol: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user: User = Depends(require_roles([Role.admin, Role.trader, Role.viewer])),
    db: AsyncSession = Depends(get_db),
):
    return await OrderService(db).list_orders(user.id, status, symbol, limit, offset)


@router.delete("/{order_id}", response_model=OrderRead)
async def cancel_order(
    order_id: int,
    user: User = Depends(require_roles([Role.admin, Role.trader])),
    db: AsyncSession = Depends(get_db),
):
    return await OrderService(db).cancel_order(user.id, order_id)

