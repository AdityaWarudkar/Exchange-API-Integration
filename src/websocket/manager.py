import json
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, topic: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[topic].add(websocket)

    def disconnect(self, topic: str, websocket: WebSocket) -> None:
        self._connections[topic].discard(websocket)

    async def broadcast(self, topic: str, payload: dict) -> None:
        dead: list[WebSocket] = []
        for websocket in self._connections[topic]:
            try:
                await websocket.send_text(json.dumps(payload))
            except RuntimeError:
                dead.append(websocket)
        for websocket in dead:
            self.disconnect(topic, websocket)


manager = ConnectionManager()

