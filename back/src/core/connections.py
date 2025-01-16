from typing import Dict, List
from fastapi import WebSocket
import json

# WEBSOCKET MENU 
class ConnectionManagerList:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    # ===================== CONNECTION METHODS =====================
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        if websocket:
            try:
                await websocket.close()
            except RuntimeError:
                pass
    
    # ===================== SEND METHODS =====================
    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_json({"type": message}) 
    

# WEBSOCKET IN GAMES
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.user_games: Dict[int, int] = {}
        self.user_sockets: Dict[int, WebSocket] = {}
    
    # ===================== CONNECTION METHODS =====================

    async def connect(self, websocket: WebSocket, game_id: int, user_id: int):
        await websocket.accept()
        
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

        # Associate the user with the current room
        self.user_games[user_id] = game_id

        # Associate the user with the current socket
        self.user_sockets[user_id] = websocket
    
    async def disconnect(self, websocket: WebSocket, game_id: int, user_id: int):
        if game_id in self.active_connections:
            self.active_connections[game_id].remove(websocket)
        
        if user_id in self.user_games:
            del self.user_games[user_id]

        if user_id in self.user_sockets:
            del self.user_sockets[user_id]

        if websocket:
            try:
                await websocket.close()
            except RuntimeError:
                pass

    async def disconnect_all(self, game_id: int):
        # Delete all user-room associations for the room
        users_to_remove = [
            user_id
            for user_id, game in self.user_games.items()
            if game == game_id
        ]

        for user_id in users_to_remove:
            del self.user_games[user_id]

        # Delete all user-socekt associations for the room
        for user_id in users_to_remove:
            del self.user_sockets[user_id]

        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                await connection.close()
            del self.active_connections[game_id]

   # ===================== SEND METHODS =====================

    async def send_message(self, websocket: WebSocket, message: json):
        await websocket.send_json(message)


    async def broadcast(self, game_id: int, message: json):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                await connection.send_json(message) 
    