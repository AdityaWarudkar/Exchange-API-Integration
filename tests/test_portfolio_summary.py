from src.schemas.portfolio import PortfolioSummary


def test_portfolio_summary_schema():
    summary = PortfolioSummary(
        total_balance=1000,
        available_balance=900,
        locked_balance=100,
        today_profit=50,
        today_loss=0,
        total_trades=10,
        winning_percentage=60,
        open_positions=2,
        closed_positions=8,
    )
    assert summary.total_balance == 1000
    assert summary.winning_percentage == 60

