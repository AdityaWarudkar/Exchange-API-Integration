from src.paper_engine.pnl import calculate_roi, calculate_unrealized_pnl, estimate_liquidation_price, mark_position


def test_unrealized_pnl_for_long_position():
    assert calculate_unrealized_pnl(100, 125, 2) == 50


def test_roi_uses_margin():
    assert calculate_roi(50, 500) == 10


def test_liquidation_estimate_for_leveraged_long():
    assert estimate_liquidation_price(100, 5, 1) == 80


def test_mark_position_returns_all_metrics():
    result = mark_position(entry_price=100, current_price=110, quantity=2, leverage=2)
    assert result.unrealized_pnl == 20
    assert result.roi == 20
    assert result.liquidation_price == 50

