from dataclasses import dataclass


@dataclass(frozen=True)
class PnLResult:
    unrealized_pnl: float
    roi: float
    liquidation_price: float | None


def calculate_unrealized_pnl(entry_price: float, current_price: float, quantity: float) -> float:
    return (current_price - entry_price) * quantity


def calculate_roi(pnl: float, margin: float) -> float:
    return 0.0 if margin == 0 else (pnl / margin) * 100


def estimate_liquidation_price(entry_price: float, leverage: float, side_quantity: float) -> float | None:
    if leverage <= 1 or side_quantity == 0:
        return None
    risk_move = entry_price / leverage
    return max(0.0, entry_price - risk_move) if side_quantity > 0 else entry_price + risk_move


def mark_position(entry_price: float, current_price: float, quantity: float, leverage: float) -> PnLResult:
    margin = abs(entry_price * quantity) / max(leverage, 1)
    pnl = calculate_unrealized_pnl(entry_price, current_price, quantity)
    return PnLResult(
        unrealized_pnl=pnl,
        roi=calculate_roi(pnl, margin),
        liquidation_price=estimate_liquidation_price(entry_price, leverage, quantity),
    )

