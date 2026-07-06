from enum import StrEnum


class OrderSide(StrEnum):
    buy = "buy"
    sell = "sell"


class OrderType(StrEnum):
    market = "market"
    limit = "limit"


class OrderStatus(StrEnum):
    pending = "pending"
    filled = "filled"
    cancelled = "cancelled"
    rejected = "rejected"
    expired = "expired"


class PositionStatus(StrEnum):
    open = "open"
    closed = "closed"


class AlertSeverity(StrEnum):
    info = "info"
    warning = "warning"
    critical = "critical"

