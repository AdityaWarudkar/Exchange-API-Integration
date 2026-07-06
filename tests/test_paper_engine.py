from src.models.enums import OrderSide, OrderStatus, OrderType, PositionStatus
from src.models.order import Order
from src.models.position import Position
from src.paper_engine.engine import PaperExecutionEngine


def make_order(side=OrderSide.buy, order_type=OrderType.market, price=None, quantity=1):
    return Order(
        client_order_id="test-order",
        user_id=1,
        exchange="paper",
        symbol="BTCUSDT",
        side=side,
        type=order_type,
        quantity=quantity,
        price=price,
    )


def test_market_order_fills():
    order = make_order()
    result = PaperExecutionEngine(fee_rate=0.001).execute(order, market_price=100, existing_position=None)
    assert result.order.status == OrderStatus.filled
    assert result.trade is not None
    assert result.position.quantity == 1
    assert result.order.fee == 0.1


def test_limit_buy_waits_when_market_is_above_limit():
    order = make_order(order_type=OrderType.limit, price=90)
    result = PaperExecutionEngine().execute(order, market_price=100, existing_position=None)
    assert result.order.status == OrderStatus.pending
    assert result.trade is None


def test_sell_closes_long_and_records_realized_pnl():
    existing = Position(
        user_id=1,
        symbol="BTCUSDT",
        entry_price=100,
        current_price=100,
        quantity=1,
        leverage=1,
        margin=100,
    )
    order = make_order(side=OrderSide.sell)
    result = PaperExecutionEngine(fee_rate=0).execute(order, market_price=120, existing_position=existing)
    assert result.position.status == PositionStatus.closed
    assert result.trade.realized_pnl == 20

