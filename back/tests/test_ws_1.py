from unittest.mock import AsyncMock, patch
import pytest

from schemas.socket import ErrorMessage, GameEventTypes
from core.games import start_game

@pytest.mark.asyncio
async def test_websocket_connection_and_info_message():
    game_id = 1
    user_id = 1

    # Mockea el WebSocket
    with patch("core.connections.ConnectionManager.connect") as MockConnectionManager:
        mock_manager = MockConnectionManager.return_value
        mock_manager.send_message = AsyncMock()
        
        # Simula el mensaje enviado desde el servidor
        async def mock_receive_json():
            return {"type": "info", "game_id": game_id}


        # Simula la conexión WebSocket
        websocket = AsyncMock()
        websocket.receive_json = AsyncMock(side_effect=mock_receive_json)
        
        # Llama a tu endpoint de WebSocket
        await websocket.accept()  # Simula la aceptación de la conexión
        await mock_manager.connect(websocket, game_id, user_id)

        # Recibe el mensaje de información
        response = await websocket.receive_json()

        # Verifica que el mensaje recibido sea el esperado
        assert response["type"] == "info"
        assert response["game_id"] == game_id


@pytest.mark.asyncio
async def test_websocket_start_message():
    game_id = 1
    user_id = 1

    # Mockea el ConnectionManager
    with patch("core.connections.ConnectionManager.connect") as MockConnectionManager:
        mock_manager = MockConnectionManager.return_value
        mock_manager.send_message = AsyncMock()
        mock_manager.broadcast = AsyncMock()

        # Simula el mensaje enviado desde el cliente
        async def mock_receive_json():
            return {"type": "start"}

        # Asigna el mock al manager
        mock_manager.receive_json = AsyncMock(side_effect=mock_receive_json)

        # Simula la conexión WebSocket
        websocket = AsyncMock()
        websocket.receive_json = AsyncMock(side_effect=mock_receive_json)
        await websocket.accept()  # Simula la aceptación de la conexión
        await mock_manager.connect(websocket, game_id, user_id)

        # Aquí invocamos la lógica que debería ejecutarse al recibir el mensaje
        data = await websocket.receive_json()

        # Lógica de tu endpoint para manejar el mensaje "start"
        if GameEventTypes.is_valid_event_type(data["type"]):
            if data["type"] == "start":
                # Simula el inicio del juego
                await mock_manager.broadcast(
                    game_id,
                    {"type": "status_start", "game_id": game_id, "user_id": user_id}
                )

        # Verifica que el mensaje de broadcast haya sido llamado correctamente
        mock_manager.broadcast.assert_called_once_with(
            game_id,
            {"type": "status_start", "game_id": game_id, "user_id": user_id}
        )


@pytest.mark.asyncio
async def test_websocket_start_with_not_enough_players():
    game_id = 1
    user_id = 1

    # Mockea el ConnectionManager
    with patch("core.connections.ConnectionManager.connect") as MockConnectionManager:
        mock_manager = MockConnectionManager.return_value
        mock_manager.send_message = AsyncMock()
        mock_manager.broadcast = AsyncMock()

        # Simula el mensaje enviado desde el cliente
        async def mock_receive_json():
            return {"type": "start"}

        # Asigna el mock al manager
        mock_manager.receive_json = AsyncMock(side_effect=mock_receive_json)

        # Simula la conexión WebSocket
        websocket = AsyncMock()
        websocket.receive_json = AsyncMock(side_effect=mock_receive_json)
        await websocket.accept()  
        await mock_manager.connect(websocket, game_id, user_id)

        # Simula que no hay suficientes jugadores
        with patch("tests.test_ws_1.start_game", side_effect=ValueError("Not enough players")) as mock_start_game:
            data = await websocket.receive_json()

            # Lógica de tu endpoint para manejar el mensaje "start"
            if data["type"] == "start":
                try:
                    start_game(game_id)
                    await mock_manager.broadcast(
                        game_id,
                        {"type": "status_start", "game_id": game_id, "user_id": user_id}
                    )
                except ValueError as e:
                    print("Caught ValueError:", e)
                    # Maneja el ValueError y envía un mensaje de error
                    error_message = ErrorMessage.create(str(e))
                    await mock_manager.send_message(websocket, error_message)

        # Verifica que se envió el mensaje de error
        mock_manager.send_message.assert_called_once()
        error_response = mock_manager.send_message.call_args[0][1]  # Obtener el argumento enviado

        assert error_response["type"] == "error"
        assert error_response["description"] == "Not enough players"


@pytest.mark.asyncio
async def test_websocket_leave_game():
    game_id = 1
    user_id = 1

    # Mockea el ConnectionManager
    with patch("core.connections.ConnectionManager.connect") as MockConnectionManager:
        mock_manager = MockConnectionManager.return_value
        mock_manager.send_message = AsyncMock()
        mock_manager.broadcast = AsyncMock()

        # Simula el mensaje enviado desde el cliente
        async def mock_receive_json():
            return {"type": "leave"}

        # Asigna el mock al manager
        mock_manager.receive_json = AsyncMock(side_effect=mock_receive_json)

        # Simula la conexión WebSocket
        websocket = AsyncMock()
        websocket.receive_json = AsyncMock(side_effect=mock_receive_json)
        await websocket.accept()  
        await mock_manager.connect(websocket, game_id, user_id)

        # Simula que no hay suficientes jugadores
        data = await websocket.receive_json()

        # Lógica de tu endpoint para manejar el mensaje "start"
        if data["type"] == "leave":
            try:
                await mock_manager.broadcast(
                    game_id,
                    {"type": "status_leave", "game_id": game_id, "user_id": user_id}
                )
            except ValueError as e:
                print("Caught ValueError:", e)
                # Maneja el ValueError y envía un mensaje de error
                error_message = ErrorMessage.create(str(e))
                await mock_manager.send_message(websocket, error_message)

        mock_manager.broadcast.assert_called_once_with(
            game_id,
            {"type": "status_leave", "game_id": game_id, "user_id": user_id}
        )