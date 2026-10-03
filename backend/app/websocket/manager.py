import json
from typing import Any

from fastapi import WebSocket


class WebSocketManager:
    """
    Manages active WebSocket connections for live vehicle telemetry and tactical alerts.
    Supports channel subscriptions ('telemetry', 'alerts', 'all').
    """

    def __init__(self):
        self.active_connections: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "all"):
        await websocket.accept()
        if websocket not in self.active_connections:
            self.active_connections[websocket] = set()
        self.active_connections[websocket].add(channel)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]

    async def subscribe(self, websocket: WebSocket, channel: str):
        if websocket in self.active_connections:
            self.active_connections[websocket].add(channel)

    async def broadcast(self, message: dict[str, Any], channel: str = "all"):
        """Broadcast message to all subscribers of the channel or 'all'."""
        data_str = json.dumps(message)
        disconnected = []
        for ws, channels in self.active_connections.items():
            if "all" in channels or channel in channels:
                try:
                    await ws.send_text(data_str)
                except Exception:  # noqa: BLE001
                    disconnected.append(ws)

        for ws in disconnected:
            self.disconnect(ws)


ws_manager = WebSocketManager()
