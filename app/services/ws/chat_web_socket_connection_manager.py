from collections import defaultdict
from typing import Dict, List

from starlette.websockets import WebSocket



class ChatWebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: int, websocket: WebSocket):
        self.active_connections[user_id].append(websocket)

    async def disconnect(self, user_id: int, websocket: WebSocket):
        self.active_connections[user_id].remove(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_message_to_user(self, message: dict):
        for client_ws in self.active_connections[message['user_id']]:
            await client_ws.send_json(message)

