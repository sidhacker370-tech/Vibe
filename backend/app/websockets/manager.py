from typing import Dict, List, Any
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        # We store connections as dict of vibe_id mapped to list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, vibe_id: str):
        await websocket.accept()
        if vibe_id not in self.active_connections:
            self.active_connections[vibe_id] = []
        self.active_connections[vibe_id].append(websocket)

    def disconnect(self, websocket: WebSocket, vibe_id: str):
        if vibe_id in self.active_connections:
            if websocket in self.active_connections[vibe_id]:
                self.active_connections[vibe_id].remove(websocket)
            if not self.active_connections[vibe_id]:
                del self.active_connections[vibe_id]

    async def broadcast(self, message: str, vibe_id: str):
        """
        Broadcast a message string to all connected sockets in a specific vibe room
        """
        if vibe_id in self.active_connections:
            for connection in self.active_connections[vibe_id]:
                try:
                    await connection.send_text(message)
                except RuntimeError:
                    pass

    async def broadcast_json(self, message: dict, vibe_id: str):
        """
        Broadcast JSON dict to all connected sockets in a specific vibe room
        """
        await self.broadcast(json.dumps(message), vibe_id)

manager = ConnectionManager()
