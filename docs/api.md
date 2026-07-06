# API Notes

Use `/docs` for the live Swagger UI.

## Auth

Register:

```json
{
  "email": "trader@example.com",
  "password": "StrongPass123",
  "role": "trader"
}
```

Login:

```json
{
  "email": "trader@example.com",
  "password": "StrongPass123"
}
```

## Paper Order

```json
{
  "exchange": "paper",
  "symbol": "BTCUSDT",
  "side": "buy",
  "type": "market",
  "quantity": 0.01
}
```

Limit orders remain `pending` until the simulated market price crosses the limit.

## WebSocket

Connect to:

```text
ws://localhost:8000/ws/market?exchange=binance&symbol=BTCUSDT
```

Market workers broadcast ticker events with exchange, symbol, price, heartbeat timestamp, and latency fields.

