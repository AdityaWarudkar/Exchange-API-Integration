# Architecture

The project follows clean architecture boundaries:

- API routes own HTTP/WebSocket contracts.
- Services own use cases and transaction orchestration.
- Repositories own database reads and writes.
- Exchange adapters own third-party API normalization.
- The paper engine owns deterministic execution and PnL math.

The application depends inward: routes call services, services call repositories and adapters, and domain calculations stay independent of FastAPI and SQLAlchemy where practical.

## Reliability

- Circuit breaker protects outbound exchange calls.
- Background market stream reconnects with exponential backoff.
- Redis alert publishing records latency and logs failures.
- Rate limiter protects public endpoints.
- Graceful shutdown signals background workers through an `asyncio.Event`.

## Monitoring

Prometheus metrics include API calls, orders by status, failed orders, reconnect count, latency, DB response timing, Redis publish timing, and open positions gauge.

