from prometheus_client import Counter, Gauge, Histogram, generate_latest

API_CALLS = Counter("exchange_api_calls_total", "Total API calls", ["route", "method", "status"])
ORDER_EVENTS = Counter("exchange_orders_total", "Orders by status", ["status", "side", "symbol"])
FAILED_ORDERS = Counter("exchange_failed_orders_total", "Failed order attempts", ["reason"])
RECONNECTS = Counter("exchange_reconnects_total", "Market stream reconnects", ["exchange", "symbol"])
LATENCY = Histogram("exchange_latency_seconds", "External and internal operation latency", ["operation"])
DB_RESPONSE = Histogram("exchange_db_response_seconds", "Database operation latency", ["operation"])
REDIS_PUBLISH = Histogram("exchange_redis_publish_seconds", "Redis publish latency", ["channel"])
OPEN_POSITIONS = Gauge("exchange_open_positions", "Open positions", ["symbol"])


def metrics_response() -> bytes:
    return generate_latest()

