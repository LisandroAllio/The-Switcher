from unittest.mock import MagicMock, patch
import pytest
from core.messages import send_message, get_game_messages, get_game_logs, send_logs
from models.tables import Messages, Logs
from schemas.messages import MessageList

def test_send_message_success():
    # Datos de prueba
    user_id = 1
    game_id = 1
    message_content = "Test message"
    
    # Mock de la sesión de SQLAlchemy
    mock_session = MagicMock()
    
    # Mock del modelo de mensaje
    mock_message = MagicMock()
    
    # Configuramos los mocks con la ruta correcta
    with patch("core.messages.Session", return_value=mock_session), \
         patch("core.messages.Messages", return_value=mock_message):
        
        # Llamamos a la función
        result = send_message(user_id, game_id, message_content)
        
        # Verificamos que el mensaje se haya creado con los datos correctos
        mock_session.add.assert_called_once_with(mock_message)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_message)
        
        # Verificamos el resultado
        assert result == 1

def test_get_game_messages():
    # Datos de prueba
    game_id = 1
    mock_message = MagicMock(spec=Messages)
    mock_message.id = 1
    mock_message.content = "Test message content"
    mock_message.user_id = 1
    mock_message.game_id = game_id
    mock_message_list = [mock_message]

    # Mock para el método de la sesión de SQLAlchemy y MessageList.from_db
    with patch("core.messages.Session") as MockSession, \
         patch("core.messages.MessageList.from_db", return_value={"id": 1, "content": "Test message content", "user_id": 1, "game_id": game_id}):

        mock_session = MockSession.return_value
        mock_session.query.return_value.filter_by.return_value.all.return_value = mock_message_list

        # Llamamos a la función que estamos probando
        result = get_game_messages(game_id)

        # Verificamos el resultado y que se llamaron los métodos correctos
        mock_session.query.assert_called_once_with(Messages)
        mock_session.query.return_value.filter_by.assert_called_once_with(game_id=game_id)
        
        # Comprobamos que el resultado es una lista con el mensaje formateado
        assert result == [{"id": 1, "content": "Test message content", "user_id": 1, "game_id": game_id}]

def test_send_logs_success():
    # Datos de prueba
    game_id = 1
    log_content = "Test log message"
    
    # Mock de la sesión de SQLAlchemy
    mock_session = MagicMock()
    
    # Mock del modelo de log
    mock_log = MagicMock()
    
    # Configuramos los mocks con la ruta correcta
    with patch("core.messages.Session", return_value=mock_session), \
         patch("core.messages.Logs", return_value=mock_log):
        
        # Llamamos a la función
        send_logs(game_id, log_content)
        
        # Verificamos que el log se haya creado con los datos correctos
        mock_session.add.assert_called_once_with(mock_log)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_log)

# Test para la función get_game_logs
def test_get_game_logs():
    # Datos de prueba
    game_id = 1
    mock_log = MagicMock(spec=Logs)
    mock_log.id = 1
    mock_log.content = "Test log message content"
    mock_log.game_id = game_id
    mock_log_list = [mock_log]

    # Mock para el método de la sesión de SQLAlchemy y GameLog.from_db
    with patch("core.messages.Session") as MockSession, \
         patch("core.messages.GameLog.from_db", return_value={"id": 1, "content": "Test log message content", "game_id": game_id}):

        mock_session = MockSession.return_value
        mock_session.query.return_value.filter_by.return_value.all.return_value = mock_log_list

        # Llamamos a la función que estamos probando
        result = get_game_logs(game_id)

        # Verificamos que se hizo la consulta y el filtrado
        mock_session.query.assert_called_once_with(Logs)
        mock_session.query.return_value.filter_by.assert_called_once_with(game_id=game_id)
        
        # Verificamos el resultado formateado
        assert result == [{"id": 1, "content": "Test log message content", "game_id": game_id}]