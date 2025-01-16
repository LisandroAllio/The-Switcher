import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import WebSocket, WebSocketDisconnect
from routers.websocket import websocket_endpoint, connection_manager

@pytest.mark.asyncio
async def test_websocket_endpoint():
    # Mock WebSocket
    mock_websocket = MagicMock(spec=WebSocket)
    mock_websocket.receive_json = AsyncMock(side_effect=[
        {"type": "start"},
        {"type": "join"},
        {"type": "endturn"},
        {"type": "leave"}
    ])

    # Mock ConnectionManager methods
    with patch.object(connection_manager, 'connect', new_callable=AsyncMock) as mock_connect, \
         patch.object(connection_manager, 'send_message', new_callable=AsyncMock) as mock_send_message, \
         patch.object(connection_manager, 'broadcast', new_callable=AsyncMock) as mock_broadcast, \
         patch.object(connection_manager, 'disconnect', new_callable=AsyncMock) as mock_disconnect, \
         patch.object(connection_manager, 'disconnect_all', new_callable=AsyncMock) as mock_disconnect_all, \
         patch('routers.websocket.games.create_game_message', return_value="game_info") as mock_create_game_message, \
         patch('routers.websocket.games.leave_game', return_value="status_cancel_game") as mock_leave_game, \
         patch('routers.websocket.games.start_game') as mock_start_game, \
         patch('routers.websocket.games.end_turn', return_value="status_endturn") as mock_end_turn, \
         patch('routers.websocket.games.end_game') as mock_end_game:

        # Call the WebSocket endpoint
        await websocket_endpoint(mock_websocket, game_id=1, user_id=1)

        # Assertions
        mock_connect.assert_called_once_with(mock_websocket, 1, 1)
        
        # Verificaciones generales
        mock_send_message.assert_called_with(mock_websocket, "game_info")
        assert mock_create_game_message.call_count == 5
        assert mock_broadcast.call_count == 4

        # Verifica que se recibio un start
        mock_create_game_message.assert_any_call("status_start",1, 1) 

        # Verifica se recibio un join
        mock_create_game_message.assert_any_call("status_join",1, 1)    
        
        # Verifica que se recibio un endturn
        mock_end_turn.assert_called_once_with(1, 1)
        mock_create_game_message.assert_any_call("status_endturn",1) 

        # Verifica que se recibio un leave
        mock_create_game_message.assert_any_call("status_cancel_game",1, 1)    


        mock_broadcast.assert_any_call(1, "game_info")
        
        # Verifica que el segundo mensaje fue un "leave"
        mock_leave_game.assert_called_once_with(1, 1)
        mock_disconnect_all.assert_called_once_with(1)


        # Verifica que se haya desconectado y terminado el juego
        mock_end_game.assert_called_once_with(1)
