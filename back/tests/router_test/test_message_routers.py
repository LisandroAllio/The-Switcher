import pytest
from unittest.mock import MagicMock, patch
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from src.main import app
from src.schemas.messages import GameLog

client = TestClient(app)

# ===================Mensajes=======================
@patch('src.routers.messages.send_message')
def test_send_message_database_error(mock_send_message):
    # Simular error de base de datos
    mock_send_message.side_effect = SQLAlchemyError("Database connection failed")
    
    message_data = {
        "user_id": 1,
        "game_id": 1,
        "content": "Hello"
    }
    
    response = client.post(
        "/game/1/user/1/message",
        json=message_data
    )
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database Error" in response.json()["detail"]

@pytest.mark.parametrize("invalid_data", [
    {},  # datos vacíos
    {"user_id": 1},  # falta game_id y content
    {"user_id": 1, "game_id": 1},  # falta content
    {"user_id": "no-number", "game_id": 1, "content": "Hello"},  # user_id inválido
])
def test_send_message_invalid_data(invalid_data):
    response = client.post(
        "/game/1/user/1/message",
        json=invalid_data
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# ===================Logs=======================

# Test para cuando hay un error de base de datos (500)
@patch('src.routers.messages.get_game_logs')  # Mockea la función que obtiene los logs
def test_get_logs_database_error(mock_get_game_logs):
    # Simulamos que se lanza un error de base de datos
    mock_get_game_logs.side_effect = SQLAlchemyError("Database error")
    
    # Simulamos la respuesta del cliente al endpoint
    response = client.get("/game/1/logs")
    
    # Verificamos que el error se maneje correctamente (500)
    assert response.status_code == 500
    # assert response.json() == {"detail": "Database Error: Database error"}
    

# Test para cuando ocurre un error general inesperado (500)
@patch('src.routers.messages.get_game_logs')  # Mockea la función que obtiene los logs
def test_get_logs_internal_server_error(mock_get_game_logs):
    # Simulamos un error general
    mock_get_game_logs.side_effect = Exception("Something went wrong")
    
    # Simulamos la respuesta del cliente al endpoint
    response = client.get("/game/1/logs")
    
    # Verificamos que el error se maneje correctamente (500)
    assert response.status_code == 500
