from unittest.mock import MagicMock, AsyncMock
import pytest
from fastapi import WebSocket
from core.connections import ConnectionManager

# ===================== test connections methods =====================
@pytest.mark.asyncio
async def test_connect_success():
    manager = ConnectionManager()

    # Mock del WebSocket
    mock_websocket = AsyncMock(spec=WebSocket)

    # Llamar a la función connect
    await manager.connect(mock_websocket, game_id=1, user_id=123)

    # Verificar que se haya llamado a websocket.accept()
    mock_websocket.accept.assert_awaited_once()

    # Verificar que la conexión esté registrada correctamente
    assert 1 in manager.active_connections
    assert mock_websocket in manager.active_connections[1]

    # Verificar que el usuario esté asociado al juego y socket
    assert manager.user_games[123] == 1
    assert manager.user_sockets[123] == mock_websocket

@pytest.mark.asyncio
async def test_disconnect_success():
    manager = ConnectionManager()

    class NewAsyncMock(AsyncMock):
        def __bool__(self):
            return True

    # Mock del WebSocket
    mock_websocket = NewAsyncMock(spec=WebSocket)
    
    assert mock_websocket is not None

    # Simular una conexión
    await manager.connect(mock_websocket, game_id=1, user_id=123)

    # Llamar a la función disconnect
    await manager.disconnect(mock_websocket, game_id=1, user_id=123)

    # Verificar que la conexión se haya eliminado correctamente
    assert mock_websocket not in manager.active_connections[1]
    assert 123 not in manager.user_games
    assert 123 not in manager.user_sockets

    # Verificar que se haya llamado a websocket.close()
    mock_websocket.close.assert_awaited_once()

@pytest.mark.asyncio
async def test_disconnect_all_success():
    manager = ConnectionManager()

    # Mock de varios WebSocket
    mock_websocket_1 = AsyncMock(spec=WebSocket)
    mock_websocket_2 = AsyncMock(spec=WebSocket)

    # Simular varias conexiones
    await manager.connect(mock_websocket_1, game_id=1, user_id=123)
    await manager.connect(mock_websocket_2, game_id=1, user_id=456)

    # Llamar a la función disconnect_all
    await manager.disconnect_all(game_id=1)

    # Verificar que todas las conexiones y asociaciones se eliminaron
    assert 1 not in manager.active_connections
    assert 123 not in manager.user_games
    assert 456 not in manager.user_games
    assert 123 not in manager.user_sockets
    assert 456 not in manager.user_sockets

    # Verificar que todos los websockets fueron cerrados
    mock_websocket_1.close.assert_awaited_once()
    mock_websocket_2.close.assert_awaited_once()

# ===================== test send methods =====================

@pytest.mark.asyncio
async def test_send_message_success():
    manager = ConnectionManager()

    # Mock del WebSocket
    mock_websocket = AsyncMock(spec=WebSocket)

    # Mensaje simulado
    message = {"type": "test", "content": "message"}

    # Llamar a la función send_message
    await manager.send_message(mock_websocket, message)

    # Verificar que se haya llamado a websocket.send_json()
    mock_websocket.send_json.assert_awaited_once_with(message)

@pytest.mark.asyncio
async def test_broadcast_success():
    manager = ConnectionManager()

    # Mock de varios WebSocket
    mock_websocket_1 = AsyncMock(spec=WebSocket)
    mock_websocket_2 = AsyncMock(spec=WebSocket)

    # Simular conexiones
    await manager.connect(mock_websocket_1, game_id=1, user_id=123)
    await manager.connect(mock_websocket_2, game_id=1, user_id=456)

    # Mensaje simulado
    message = {"type": "broadcast", "content": "message"}

    # Llamar a la función broadcast
    await manager.broadcast(game_id=1, message=message)

    # Verificar que ambos websockets recibieron el mensaje
    mock_websocket_1.send_json.assert_awaited_once_with(message)
    mock_websocket_2.send_json.assert_awaited_once_with(message)
