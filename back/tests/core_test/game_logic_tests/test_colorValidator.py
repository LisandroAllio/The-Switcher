from unittest.mock import MagicMock
import pytest
from models.tables import Game, gameToken
from core.game_logic.aux.colorValidator import validate_forbidden_color, update_forbidden_color

# =============== Tests validate_forbidden_color =================

def test_validate_forbidden_color_success():
    # Mock de la sesión
    mock_session = MagicMock()

    # Mock del objeto game
    mock_game = Game(id=1, forbiddenColor='red')
    mock_game_query = MagicMock()
    mock_game_query.filter_by.return_value.first.return_value = mock_game

    # Mock del objeto token
    mock_token = gameToken(id=1, color='blue')
    mock_token_query = MagicMock()
    mock_token_query.filter_by.return_value.first.return_value = mock_token

    # Configura la sesión para devolver los mocks de las consultas
    def query_side_effect(model):
        if model == Game:
            return mock_game_query
        elif model == gameToken:
            return mock_token_query
        else:
            return None

    mock_session.query.side_effect = query_side_effect

    # Llamamos a la función con el mock de la sesión
    result = validate_forbidden_color(1, 1, mock_session)

    # Comprobamos que el resultado sea True
    assert result is True  # Porque el color del token ('blue') es diferente del forbiddenColor ('red')



def test_validate_forbidden_color_game_not_found():
    mock_session = MagicMock()
    
    # Simulamos que no se encuentra el juego
    mock_session.query(Game).filter_by(id=1).first.return_value = None

    with pytest.raises(ValueError, match="Game not found"):
        validate_forbidden_color(1, 1, mock_session)


def test_validate_forbidden_color_token_not_found():
    mock_session = MagicMock()
    
    # Simulamos que se encuentra el juego
    mock_game = Game(id=1, forbiddenColor='red')
    mock_game_query = MagicMock()
    mock_game_query.filter_by.return_value.first.return_value = mock_game

    # Simulamos que no se encuentra el token
    mock_token_query = MagicMock()
    mock_token_query.filter_by.return_value.first.return_value = None

    # Configura la sesión para devolver los mocks de las consultas
    def query_side_effect(model):
        if model == Game:
            return mock_game_query
        elif model == gameToken:
            return mock_token_query
        else:
            return None
    
    mock_session.query.side_effect = query_side_effect

    with pytest.raises(ValueError, match="Token not found"):
        validate_forbidden_color(1, 1, mock_session)

# =============== Tests update_forbidden_color =================

def test_update_forbidden_color_success():
    # Mock de la sesión
    mock_session = MagicMock()

    # Mock del objeto game
    mock_game = Game(id=1, forbiddenColor='red')
    mock_game_query = MagicMock()
    mock_game_query.filter_by.return_value.first.return_value = mock_game

    # Mock del objeto token
    mock_token = gameToken(id=1, color='blue')
    mock_token_query = MagicMock()
    mock_token_query.filter_by.return_value.first.return_value = mock_token

    # Configura la sesión para devolver los mocks de las consultas
    def query_side_effect(model):
        if model == Game:
            return mock_game_query
        elif model == gameToken:
            return mock_token_query
        else:
            return None

    mock_session.query.side_effect = query_side_effect

    # Llamamos a la función con el mock de la sesión
    update_forbidden_color(1, 1, mock_session)

    # Verificar que se haya actualizado el forbiddenColor correctamente
    assert mock_game.forbiddenColor == 'blue'

    # Verificar que se haya llamado a session.commit()
    mock_session.commit.assert_called_once()

def test_update_forbidden_color_game_not_found():
    # Mock de la sesión
    mock_session = MagicMock()

    # Mock de la consulta de game que devuelve None
    mock_game_query = MagicMock()
    mock_game_query.filter_by.return_value.first.return_value = None
    mock_session.query.return_value = mock_game_query

    # Llamar a la función y esperar una excepción ValueError
    with pytest.raises(ValueError, match="Game not found"):
        update_forbidden_color(1, 1, mock_session)

    # Verificar que no se haya llamado a session.commit()
    mock_session.commit.assert_not_called()

def test_update_forbidden_color_token_not_found():
    # Mock de la sesión
    mock_session = MagicMock()

    # Mock del objeto game
    mock_game = Game(id=1, forbiddenColor='red')
    mock_game_query = MagicMock()
    mock_game_query.filter_by.return_value.first.return_value = mock_game

    # Mock de la consulta de token que devuelve None
    mock_token_query = MagicMock()
    mock_token_query.filter_by.return_value.first.return_value = None

    # Configura la sesión para devolver los mocks de las consultas
    def query_side_effect(model):
        if model == Game:
            return mock_game_query
        elif model == gameToken:
            return mock_token_query
        else:
            return None

    mock_session.query.side_effect = query_side_effect

    # Llamar a la función y esperar una excepción ValueError
    with pytest.raises(ValueError, match="Token not found"):
        update_forbidden_color(1, 1, mock_session)

    # Verificar que no se haya llamado a session.commit()
    mock_session.commit.assert_not_called()
