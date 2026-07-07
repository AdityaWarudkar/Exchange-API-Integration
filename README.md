# exchange-api-order-execution-sandbox

A production-style cryptocurrency trading backend sandbox built with FastAPI, PostgreSQL, Redis, WebSocket streaming, Prometheus, Grafana, SQLAlchemy, Alembic, JWT auth, and an exchange-neutral client layer for Binance and Bybit.

The service is intentionally paper-only for order execution. It reads public market data, normalizes exchange responses, simulates fills, stores every order/trade/position, calculates PnL and portfolio metrics, publishes Redis alerts, and exposes REST/WebSocket APIs.

## Architecture Diagram

```text
Client / Swagger / Bot
        |
        v
FastAPI REST + WebSocket Gateway
        |
        +-- Auth Service -------- JWT, roles: admin/trader/viewer
        +-- Market Service ------ Unified ExchangeClient
        |                         +-- Binance public adapter
        |                         +-- Bybit public adapter
        +-- Order Service ------- PaperExecutionEngine
        +-- Portfolio Service --- Balances, trades, PnL, positions
        +-- Alert Service ------- Redis Pub/Sub
        |
        +-- SQLAlchemy Repositories
        |       |
        |       v
        |   PostgreSQL
        |
        +-- Prometheus Metrics --> Grafana Dashboard
```

## Folder Structure

```text
src/
  api/routes/       REST and WebSocket routes
  alerts/           Redis alert publisher
  core/             security, metrics, logging, rate limiter, circuit breaker
  config/           Pydantic settings
  database/         async SQLAlchemy engine/session/base
  exchange/         ExchangeClient interface plus Binance and Bybit adapters
  models/           SQLAlchemy ORM models
  paper_engine/     paper fills, fees, PnL, ROI, liquidation estimate
  repositories/     persistence layer
  schemas/          Pydantic request/response contracts
  services/         application use cases
  websocket/        connection manager and market broadcaster
  workers/          Redis subscriber/background tasks
tests/              focused unit and API tests
alembic/            database migrations
prometheus/         scrape config
grafana/            dashboard JSON
```

## Database ER Diagram

```text
users 1--* orders 1--* trades
users 1--* positions
users 1--* balances
users 1--* portfolio

alerts
exchange_logs
```

Core tables:

- `users`: email, password hash, role, created timestamp.
- `orders`: client order id, exchange, symbol, side, type, status, fill price, fee, errors.
- `trades`: immutable execution records tied to orders.
- `positions`: entry/current price, quantity, leverage, margin, liquidation estimate, PnL, ROI.
- `balances`: total, available, and locked wallet balances.
- `portfolio`: point-in-time portfolio snapshots.
- `alerts`: persisted alert events.
- `exchange_logs`: exchange operation diagnostics.

## API Documentation

Swagger UI is available at:

```text
http://localhost:8000/docs
```

Important endpoints:

```text
POST   /register
POST   /login
POST   /refresh
GET    /portfolio
POST   /order
POST   /orders
GET    /orders
DELETE /order/{id}
DELETE /orders/{id}
GET    /positions
GET    /ticker?exchange=binance&symbol=BTCUSDT
GET    /orderbook?exchange=bybit&symbol=ETHUSDT
WS     /ws/market?exchange=binance&symbol=BTCUSDT
GET    /health
GET    /metrics
```

## Request Flow

1. The client authenticates with `/login` and receives access and refresh tokens.
2. Protected routes decode JWT claims and enforce role-based access.
3. A paper order enters `OrderService`, is persisted as pending, and asks `MarketService` for a live public ticker.
4. `PaperExecutionEngine` decides whether the order fills, computes fee, realized/unrealized PnL, ROI, and position state.
5. Repositories persist order, trade, balance, position, and alert changes in PostgreSQL.
6. `AlertService` publishes order events to Redis and records metrics for Prometheus.
7. Background market workers broadcast normalized ticker events to `/ws/market`.





## Future Improvements

- Add real authenticated exchange trading behind explicit feature flags and signed API-key vaulting.
- Use Kafka or Redpanda for durable event streams.
- Add partial fills, maker/taker fees, stop orders, and isolated/cross margin modes.
- Add a reconciliation worker comparing internal state against exchange state.
- Add Grafana provisioning files for automatic dashboard loading.
- Add OpenTelemetry tracing across API, DB, Redis, and exchange calls.
