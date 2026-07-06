from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.websocket.manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/market")
async def market_socket(websocket: WebSocket, exchange: str = "binance", symbol: str = "BTCUSDT"):
    topic = f"{exchange}:{symbol.upper()}"
    await manager.connect(topic, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(topic, websocket)

