import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.alerts.service import AlertService
from src.config.settings import get_settings
from src.core.metrics import FAILED_ORDERS, ORDER_EVENTS
from src.models.enums import AlertSeverity, OrderStatus
from src.models.order import Order
from src.paper_engine.engine import PaperExecutionEngine
from src.repositories.balances import BalanceRepository
from src.repositories.orders import OrderRepository
from src.repositories.positions import PositionRepository
from src.repositories.trades import TradeRepository
from src.schemas.order import OrderCreate
from src.services.market_service import MarketService


class OrderService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.orders = OrderRepository(db)
        self.positions = PositionRepository(db)
        self.trades = TradeRepository(db)
        self.balances = BalanceRepository(db)
        self.engine = PaperExecutionEngine()
        self.market = MarketService()
        self.alerts = AlertService(db)

    async def place_order(self, user_id: int, payload: OrderCreate) -> Order:
        if payload.exchange != "paper":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="only paper orders are enabled")

        order = Order(
            client_order_id=str(uuid.uuid4()),
            user_id=user_id,
            exchange=payload.exchange,
            symbol=payload.symbol,
            side=payload.side,
            type=payload.type,
            quantity=payload.quantity,
            price=payload.price,
        )
        await self.orders.add(order)
        balance = await self.balances.get_or_create_usdt(user_id, get_settings().paper_starting_balance)
        ticker = await self.market.get_ticker("binance", payload.symbol)
        market_price = float(ticker["price"])
        notional = payload.quantity * market_price
        if payload.side.value == "buy" and balance.available < notional:
            order.status = OrderStatus.rejected
            order.error = "insufficient paper balance"
            FAILED_ORDERS.labels(reason="insufficient_balance").inc()
            await self.db.commit()
            return order

        existing_position = await self.positions.get_open(user_id, payload.symbol)
        execution = self.engine.execute(order, market_price, existing_position)
        if execution.trade:
            await self.trades.add(execution.trade)
            if execution.position and execution.position.id is None:
                await self.positions.add(execution.position)
            if payload.side.value == "buy":
                balance.available -= notional + order.fee
            else:
                balance.available += notional - order.fee
            balance.total = balance.available + balance.locked
            await self.alerts.publish(
                "order_filled",
                AlertSeverity.info,
                f"{payload.side.value} {payload.quantity} {payload.symbol} filled at {market_price}",
                {"order_id": order.id, "symbol": payload.symbol, "price": market_price},
            )
        ORDER_EVENTS.labels(status=order.status.value, side=order.side.value, symbol=order.symbol).inc()
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def cancel_order(self, user_id: int, order_id: int) -> Order:
        order = await self.orders.get_for_user(order_id, user_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
        if order.status != OrderStatus.pending:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="only pending orders can be cancelled")
        order.status = OrderStatus.cancelled
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def list_orders(self, user_id: int, status_filter=None, symbol=None, limit: int = 100, offset: int = 0):
        return await self.orders.list_for_user(user_id, status_filter, symbol, limit, offset)
