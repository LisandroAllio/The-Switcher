from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.connections import ConnectionManager, ConnectionManagerList
from schemas.socket import ErrorMessage, GameEventTypes
import core.games as games

ws = APIRouter(tags=["websocket"])

game_manager = ConnectionManagerList()
connection_manager = ConnectionManager()

#Web socket para ver el listado de partidas
@ws.websocket("/ws/")
async def websocket_endpoint(websocket_games: WebSocket):
    await game_manager.connect(websocket_games)
    try:
        await game_manager.send_message("info") 
        while True:
            try:
                await websocket_games.receive_json() #nothing to do
            
            except ValueError as error:
                await game_manager.send_message( websocket_games, ErrorMessage.create(str(error)))  
    except WebSocketDisconnect as e:
        if e.code == 1000: #DEBUGGIN
            print(f"WebSocket closed normally")
        else:
            print(f"WebSocket disconnected with error code: {e.code}")
        await game_manager.disconnect(websocket_games)


#Web socket para dentro de la partida
@ws.websocket("/ws/{game_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, user_id: int):
    await connection_manager.connect(websocket, game_id, user_id)
    try:
        game_info = games.create_game_message("info", game_id)
        await connection_manager.send_message(websocket, game_info)    
        while True:
                try: 
                    data = await websocket.receive_json()
                    if GameEventTypes.is_valid_event_type(data["type"]):
                        if data["type"] == "start":
                            games.start_game(game_id)      
                            await connection_manager.broadcast(
                                game_id,
                                games.create_game_message("status_start", game_id, user_id)
                            )
                            
                            await game_manager.send_message("status_update_games")

                        if data["type"] == "join":
                            await connection_manager.broadcast(
                                game_id,
                                games.create_game_message("status_join", game_id, user_id)
                            )

                            await game_manager.send_message("status_update_games")

                        if data["type"] == "leave":
                            message = games.leave_game(game_id, user_id)
                            await connection_manager.broadcast(
                                        game_id,
                                        games.create_game_message(message, game_id, user_id)
                            )  

                            if message == "status_cancel_game" or message == "status_winner":
                                await connection_manager.disconnect_all(game_id) 
                                games.end_game(game_id)
                            else:
                                await connection_manager.disconnect(websocket, game_id, user_id)    

                            await game_manager.send_message("status_update_games")
                            break 
                        if data["type"] == "endturn":
                            message = games.end_turn(game_id, user_id)
                            await connection_manager.broadcast(
                                game_id,
                                games.create_game_message(message, game_id, user_id)
                            )             
                    else:
                        await connection_manager.send_message(
                            websocket,
                            ErrorMessage.create("DEBUGGING: Invalid game event"),
                        )   
                except ValueError as error:
                    await connection_manager.send_message(
                        websocket, 
                        ErrorMessage.create(str(error)),
                    )      
    except WebSocketDisconnect as e:
        if e.code == 1000: #DEBUGGIN
            print(f"WebSocket closed normally for user {user_id}")
        else:
            print(f"WebSocket disconnected with error code: {e.code}")
        try:
            if user_id in games.get_players(game_id):
                await connection_manager.disconnect(websocket, game_id, user_id)
        except ValueError as error:
            pass #There is a winner, nothig to do



