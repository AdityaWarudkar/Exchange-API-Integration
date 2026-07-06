from dataclasses import dataclass

from src.config.settings import get_settings
from src.models.enums import OrderSide, OrderStatus, OrderType, PositionStatus
from src.models.order import Order
from src.models.position import Position
from src.models.trade import Trade
from src.paper_engine.pnl import mark_position


@dataclass(frozen=True)
class ExecutionResult:
    order: Order
    trade: Trade | None
    position: Position | None


class PaperExecutionEngine:
    def __init__(self, fee_rate: float | None = None) -> None:
        self.fee_rate = fee_rate if fee_rate is not None else get_settings().fee_rate

    def should_fill(self, order: Order, market_price: float) -> bool:
        if order.type == OrderType.market:
            return True
        if order.price is None:
            return False
        if order.side == OrderSide.buy:
            return market_price <= order.price
        return market_price >= order.price

    def execute(self, order: Order, market_price: float, existing_position: Position | None) -> ExecutionResult:
        if not self.should_fill(order, market_price):
            order.status = OrderStatus.pending
            return ExecutionResult(order=order, trade=None, position=existing_position)

        signed_quantity = order.quantity if order.side == OrderSide.buy else -order.quantity
        notional = abs(order.quantity * market_price)
        fee = notional * self.fee_rate
        order.status = OrderStatus.filled
        order.filled_quantity = order.quantity
        order.average_fill_price = market_price
        order.fee = fee

        realized_pnl = 0.0
        position = existing_position
        if position is None:
            position = Position(
                user_id=order.user_id,
                symbol=order.symbol,
                entry_price=market_price,
                current_price=market_price,
                quantity=signed_quantity,
                leverage=1.0,
                margin=notional,
            )
        else:
            position.realized_pnl = position.realized_pnl or 0.0
            position.unrealized_pnl = position.unrealized_pnl or 0.0
            position.roi = position.roi or 0.0
            position.leverage = position.leverage or 1.0
            if position.quantity == 0 or (position.quantity > 0) == (signed_quantity > 0):
                new_qty = position.quantity + signed_quantity
                position.entry_price = (
                    (position.entry_price * abs(position.quantity)) + (market_price * abs(signed_quantity))
                ) / abs(new_qty)
                position.quantity = new_qty
            else:
                closing_qty = min(abs(position.quantity), abs(signed_quantity))
                direction = 1 if position.quantity > 0 else -1
                realized_pnl = (market_price - position.entry_price) * closing_qty * direction
                position.realized_pnl += realized_pnl - fee
                position.quantity += signed_quantity
                if position.quantity == 0:
                    position.status = PositionStatus.closed

        position.current_price = market_price
        position.margin = abs(position.entry_price * position.quantity) / max(position.leverage, 1)
        marks = mark_position(position.entry_price, market_price, position.quantity, position.leverage)
        position.unrealized_pnl = marks.unrealized_pnl
        position.roi = marks.roi
        position.liquidation_price = marks.liquidation_price

        trade = Trade(
            order=order,
            symbol=order.symbol,
            side=order.side.value,
            quantity=order.quantity,
            price=market_price,
            fee=fee,
            realized_pnl=realized_pnl - fee,
        )
        return ExecutionResult(order=order, trade=trade, position=position)
