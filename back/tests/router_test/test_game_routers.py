import pytest
from unittest.mock import MagicMock, patch
from fastapi import status
from fastapi.testclient import TestClient
from src.main import app
from src.schemas.card import UserMovementCardsModel, MoveType 

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.tables import Base


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_database.db"  

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture para configurar la base de datos de prueba
@pytest.fixture(scope="module")
def test_db():
    # Crear las tablas
    Base.metadata.create_all(bind=engine)

    yield  # Aquí se ejecutan las pruebas

    # Limpiar después de las pruebas
    Base.metadata.drop_all(bind=engine)

# Fixture para proporcionar una sesión de base de datos
@pytest.fixture
def db_session(test_db):
    db = SessionLocal()
    yield db
    db.close()


client = TestClient(app)

# ======================= Tests create_game =======================


@patch('core.games.create_game')
def test_create_game_success(mock_create_game):
    mock_create_game.return_value = 1
    game_data = {
        "name": "Test Game",
        "minPlayers": 2,
        "maxPlayers": 4,
        "password": "1234"
    }
    player_data = {
        "name": "Test Player",
        "session_id" : 1
    }
    
    response = client.post("/games/new", json={"game_model_data": game_data, "player_model_data": player_data})
    
    assert response.status_code == 201
    response_data = response.json()
    assert "id" in response_data
    assert response_data["id"] == 1 
    mock_create_game.assert_called_once_with("Test Game", "Test Player", 1, 2, 4, "1234") 
    response = client.put

@patch('core.games.create_game')  
def test_new_game_name_too_long(mock_create_game):
    long_name = "a" * 33  
    game_data = {
        "name": long_name,  
        "minPlayers": 2,
        "maxPlayers": 4,
        "password": "secret"
    }
    player_data = {
        "name": "player1"  
    }

    response = client.post("/games/new", json={
        "game_model_data": game_data,  
        "player_model_data": player_data
    })

    assert response.status_code == 422
    assert "detail" in response.json()

    mock_create_game.assert_not_called()

@patch('core.games.create_game') 
def test_create_game_invalid_player_count(mock_create_game):

    mock_create_game.side_effect = ValueError("Minimum users must be less than maximum users")
    game_data = {
        "name": "Test Game",
        "minPlayers": 2,
        "maxPlayers": 4,
        "password": "1234"
    }
    player_data = {
        "name": "Test Player",
        "session_id" : 1
    }
    
    response = client.post("/games/new", json={"game_model_data": game_data, "player_model_data": player_data})
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "Minimum users must be less than maximum users"

# ======================= Tests list_game =======================


# Ejemplo de datos que se espera que retorne el endpoint
mock_games_data = [
    {"id": 1, "name": "Test Game 1", "host_id": 1, "in_game": False, "is_private": False,
        "users": {"min": 2, "max": 4, "players": [{'1': "user1"}]}},
    {"id": 2, "name": "Test Game 2", "host_id": 2, "in_game": True, "is_private": True, "users": {
        "min": 3, "max": 3, "players": [{'2': "user1"}, {'3': "user2"}]}},
]


@patch('core.games.get_games')
def test_list_games(mock_list_games):
    mock_list_games.return_value = mock_games_data

    response = client.get("/games/list")

    assert response.status_code == 200
    assert response.json() 

# ======================= Tests list_game_by_name =======================


# Ejemplo de datos que se espera que retorne el endpoint
mock_games_data = [
    {"id": 1, "name": "Test Game 1", "host_id": 1, "in_game": False, "is_private": False,
        "users": {"min": 2, "max": 4, "players": [{'1': "user1"}]}},
    {"id": 2, "name": "Test Game 2", "host_id": 2, "in_game": True, "is_private": True, "users": {
        "min": 3, "max": 3, "players": [{'2': "user1"}, {'3': "user2"}]}},
    {"id": 2, "name": "Another Game ", "host_id": 2, "in_game": True, "is_private": True, "users": {
        "min": 3, "max": 3, "players": [{'2': "user1"}, {'3': "user2"}]}},
]

@patch('core.games.get_games_by_name')
def test_list_games(mock_list_games):
    mock_list_games.return_value = mock_games_data

    response = client.get("/games/list/name/Test Game")

    assert response.status_code == 200
    assert response.json() 

# ======================= Tests list_game_by_players =======================


# Ejemplo de datos que se espera que retorne el endpoint
mock_games_data = [
    {"id": 2, "name": "Test Game 2", "host_id": 2, "in_game": True, "is_private": True, "users": {
        "min": 3, "max": 3, "players": [{'2': "user1"}, {'3': "user2"}]}},
    {"id": 2, "name": "Another Game ", "host_id": 2, "in_game": True, "is_private": True, "users": {
        "min": 3, "max": 3, "players": [{'2': "user1"}, {'3': "user2"}]}},
]

@patch('core.games.get_games_by_players')
def list_game_by_players(mock_list_games):
    mock_list_games.return_value = mock_games_data

    response = client.get("/games/list/players/2")

    assert response.status_code == 200
    assert response.json() 

# ======================= Tests join_game =======================

# Juego no encontrado (404).


@patch('core.games.join_game')
def test_join_game_not_found(mock_join_game):

    mock_join_game.side_effect = ValueError("Game not found")
    response = client.put("/games/join", json={
        "game_id": 1,
        "user_name": "string",
        "password": "",
        "session_id" : 1
    })
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}

# Juego lleno (403).
@patch('core.games.join_game')
def test_game_full(mock_join_game):

    mock_join_game.side_effect = ValueError("Game is full")
    response = client.put("/games/join", json={
        "game_id": 1,
        "user_name": "string",
        "password": "",
        "session_id" : 1
    })
    assert response.status_code == 403
    assert response.json() == {"detail": "Game is full"}

# Contraseña incorrecta (401)
@patch('core.games.join_game')
def test_join_game_incorrect_password(mock_join_game):

    mock_join_game.side_effect = ValueError("Incorrect Password")
    response = client.put("/games/join", json={
        "game_id": 1,
        "user_name": "player1",
        "password": "incorrect_password",
        "session_id" : 1
    })
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect Password"}

#Unión exitosa (200).
mock_join_game_data = {
    "id": 1,
        "name": "Mocked Game",
        "host_id": 1,
        "in_game": False,
        "is_private": False,
        "users": {
            "min": 2,
            "max": 4,
            "players": [
                {"1": "Player1"},
                {"2": "Player2"}
            ]
        }
    }

#Union a partida publica
@patch('core.games.join_game')
@patch('core.connections.ConnectionManager.broadcast')
@patch('core.games.create_game_message')
def test_join_game_endpoint(mock_create_game_message ,mock_broadcast, mock_join_game):
    mock_join_game.return_value = mock_join_game_data

    response = client.put("/games/join", json={
        "game_id": 1,
        "user_name": "Player3",
        "password": "",
        "session_id" : 1
    })

    assert response.status_code == 200
    assert response.json() == mock_join_game_data
    mock_create_game_message.assert_called_once_with("status_join", 1)
    mock_broadcast.assert_called_once_with(1, mock_create_game_message.return_value)


#Union a partida privada
mock_join_game_data_password = {
    "id": 2,
        "name": "Mocked Game with password",
        "host_id": 1,
        "in_game": False,
        "is_private": True,
        "users": {
            "min": 2,
            "max": 4,
            "players": [
                {"1": "Player1"},
                {"2": "Player2"}
            ]
        }
    }
@patch('core.games.join_game')
@patch('core.connections.ConnectionManager.broadcast')
@patch('core.games.create_game_message')
def test_join_game_endpoint_with_password(mock_create_game_message ,mock_broadcast, mock_join_game):
    mock_join_game.return_value = mock_join_game_data_password

    response = client.put("/games/join", json={
        "game_id": 2,
        "user_name": "Player3",
        "password": "test_password",
        "session_id" : 1
    })

    assert response.status_code == 200
    assert response.json() == mock_join_game_data_password
    mock_create_game_message.assert_called_once_with("status_join", 2)
    mock_broadcast.assert_called_once_with(2, mock_create_game_message.return_value)


# ======================= Tests start_game =======================

# #Juego no encontrado (404).


@patch('core.games.start_game')
def test_start_game_not_found(mock_start_game):

    mock_start_game.side_effect = ValueError("Game not found")
    response = client.patch("/games/1/start")
    assert response.status_code == 404
    assert response.json() == {"detail": "Could not start the game"}

# Juego iniciado (200).


@patch('core.games.start_game')
def test_start_game(mock_start_game):

    mock_start_game.side_effect = None
    response = client.patch("/games/1/start")
    assert response.status_code == 200
    assert response.json() == {"message": "Game started"}

# ======================= Test get_movement_cards =======================

mock_mov_data = [
    {"card_id": 1, "mov_type": 'NO_SKIP_LINE'},
    {"card_id": 2, "mov_type": 'SKIP_ONE_LINE'},
    {"card_id": 3, "mov_type": "SHORT_DIAG"}
]


@patch('core.game_logic.cards.get_player_movement_cards')
def test_get_player_movement_card(mock_get_mov_cards):

    mock_get_mov_cards.return_value = [
        UserMovementCardsModel(**card).model_dump() for card in mock_mov_data]

    response = client.get("/game/1/1/movements")

    assert response.status_code == 200
    assert response.json() == {"cards": mock_mov_data}

@patch('core.game_logic.cards.get_player_movement_cards')
def test_get_player_movement_card_not_found(mock_get_mov_cards):

        mock_get_mov_cards.return_value = []
        mock_get_mov_cards.side_effect = ValueError("No Movement Cards Found")
        response = client.get("/game/1/1/movements")
        print(response.json())
    
        assert response.status_code == 400
        assert response.json() == {"detail": "No Movement Cards Found"}


# ======================= Tests get_game_turn =======================
# Test get_game_turn
mock_get_game_turn_data = {
    "turnActive": 1,
    "actualPlayer_id": 1,
    "actualPlayer_name": "Player1",
    "nextPlayer_id": 2,
    "nextPlayer_name": "Player2",
    "forbiddenColor": "red",
    "amountPlayers": 4
}

# Juego no encontrado (404).
@patch('core.games.get_game_turn')
def test_get_game_turn(mock_get_game_turn):
    mock_get_game_turn.side_effect = ValueError("Game not found")

    response = client.get("/game/7/turn")

    assert response.status_code == 404
    assert response.json() == {'detail': 'Game not found'}

# Juego encontrado (200).
@patch('core.games.get_game_turn')
def test_get_game_turn_found(mock_get_game_turn):
    mock_get_game_turn.return_value = mock_get_game_turn_data
    mock_get_game_turn.side_effect = None

    response = client.get("/game/1/turn")

    assert response.status_code == 200
    assert response.json() == mock_get_game_turn_data

# ======================= Test moveToken =======================
@patch('core.game_logic.cards.play_movement_card')
@patch('core.games.create_game_message')
@patch('core.connections.ConnectionManager.broadcast')
def test_move_token_success(mock_broadcast, mock_create_game_message, mock_play_movemnt_card):
    # Configuración del mock
    mock_play_movemnt_card.side_effect = None
    mock_broadcast.return_value = None
    mock_create_game_message.return_value = "status_move"

    move_token_data = {
        "game_id": 1,
        "player_id": 10,
        "move_id": 2,
        "token1_id": 5,
        "token2_id": 6
    }

    response = client.put("/game/1/move", json=move_token_data)

    assert response.status_code == 200
    assert response.json() == {"message": "Token moved"}
    mock_broadcast.assert_called_once_with(
        1, "status_move"
    )

@patch('core.game_logic.cards.play_movement_card')
@patch('core.games.create_game_message')
@patch('core.connections.ConnectionManager.broadcast')
def test_move_token_invalid_movement(mock_broadcast, mock_create_game_message, mock_play_movemnt_card):
    mock_broadcast.return_value = None
    mock_play_movemnt_card.side_effect = ValueError("Invalid movement")
    
    move_token_data = {
        "game_id": 1,
        "player_id": 10,
        "move_id": 2,
        "token1_id": 5,
        "token2_id": 6,
    }

    response = client.put("/game/1/move", json=move_token_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid movement"}
    mock_broadcast.assert_not_called()  

# ======================= Test undo_last_move_retrieved ============================

# Movimiento deshecho exitosamente (200).
@patch('core.games.create_game_message')
@patch('core.connections.ConnectionManager.broadcast')
@patch('core.game_logic.cards.revert_last_play')
def test_undo_last_movement_success(mock_revert_last_play ,mock_broadcast, mock_create_game_message):
    mock_revert_last_play.return_value = None
    mock_broadcast.return_value = None
    mock_broadcast.side_effect = None
    mock_create_game_message.return_value = "status_last_movement_undone"

    last_move_form = {
        "game_id": 1,
        "player_id": 1
    }
    response = client.post("/game/1/undo_last_movement", json=last_move_form)

    # Aseguramos que el código de estado sea 200
    assert response.status_code == 200
    assert response.json() == {"message": "Last movement undone"}
    assert mock_create_game_message.called_with("status_last_movement_undone", 1, 1)
    assert mock_broadcast.called


# Último movimiento no encontrado (404).
@patch('core.games.create_game_message')
@patch('core.connections.ConnectionManager.broadcast')
@patch('core.game_logic.cards.revert_last_play')
def test_undo_last_movement_last_move_not_found(mock_revert_last_play, mock_broadcast, mock_create_game_message):
    # Simular que se lanza una excepción "Last movement not found"
    mock_broadcast.return_value = None
    mock_create_game_message.return_value = None
    mock_revert_last_play.side_effect = ValueError("Last movement not found")

    last_move_form = {
        "game_id": 1,
        "player_id": 1
    }
    
    response = client.post("/game/1/undo_last_movement", json=last_move_form)

    assert response.status_code == 404
    assert response.json() == {"detail": "Last movement not found"}
    assert mock_broadcast.not_called


# ======================= Test update_figure_card ============================
# Carta figura usada exitosamente (200).
@patch('core.games.create_game_message')
@patch('core.connections.ConnectionManager.broadcast')
@patch('core.game_logic.cards.play_figure_card')
def test_update_figure_card_success(mock_play_figure ,mock_broadcast, mock_create_game_message):
    mock_play_figure.return_value = None
    mock_broadcast.return_value = None
    mock_broadcast.side_effect = None
    mock_create_game_message.return_value = "status_used_figure"

    used_figure_form = {
        "game_id": 1,
        "player_id": 1,
        "figure_id": 1,
        "token_id": 1
    }
    response = client.post("/game/1/use_figure", json=used_figure_form)

    assert response.status_code == 200
    assert response.json() == {"message": "Figure card used successfully"}
    assert mock_play_figure.called_with(1, 1, 1, 1)
    assert mock_create_game_message.called_with("status_used_figure", 1)
    assert mock_broadcast.called

# Carta figura no encontrada (404).
@patch('core.games.create_game_message')
@patch('core.connections.ConnectionManager.broadcast')
@patch('core.game_logic.cards.play_figure_card')
def test_update_figure_card_card_not_found(mock_play_figure, mock_broadcast, mock_create_game_message):
    mock_play_figure.return_value = None
    mock_play_figure.side_effect = ValueError("Card not found")
    mock_broadcast.return_value = None
    mock_create_game_message.return_value = None

    used_figure_form = {
        "game_id": 1,
        "player_id": 1,
        "figure_id": 1,
        "token_id": 1
    }
    
    response = client.post("/game/1/use_figure", json=used_figure_form)

    assert response.status_code == 404
    assert mock_broadcast.not_called
    assert response.json() == {"detail": "Card not found"}

# Ficha no pertenece a la figura (404).
@patch('core.games.create_game_message')
@patch('core.connections.ConnectionManager.broadcast')
@patch('core.game_logic.cards.play_figure_card')
def test_update_figure_card_token_not_belong_to_figure(mock_play_figure, mock_broadcast, mock_create_game_message):
    mock_play_figure.return_value = None
    mock_play_figure.side_effect = ValueError("Token doesn't belong in figure")
    mock_broadcast.return_value = None
    mock_create_game_message.return_value = None

    used_figure_form = {
        "game_id": 1,
        "player_id": 1,
        "figure_id": 1,
        "token_id": 1
    }
    
    response = client.post("/game/1/use_figure", json=used_figure_form)

    assert response.status_code == 404
    assert mock_broadcast.not_called
    assert response.json() == {"detail": "Token doesn't belong in figure"}


# ======================= Test show_all_figures ============================

mock_figures_data = {
  "figures": [
    {
      "figure": {
        "id": 51,
        "type": "F11",
        "blocked": False
      },
      "tokens": [
        [
          {
            "id": 59,
            "x_coordinate": 4,
            "y_coordinate": 5,
            "color": "RED"
          },
          {
            "id": 60,
            "x_coordinate": 4,
            "y_coordinate": 6,
            "color": "RED"
          },
          {
            "id": 58,
            "x_coordinate": 4,
            "y_coordinate": 4,
            "color": "RED"
          },
          {
            "id": 54,
            "x_coordinate": 3,
            "y_coordinate": 6,
            "color": "RED"
          },
          {
            "id": 65,
            "x_coordinate": 5,
            "y_coordinate": 5,
            "color": "RED"
          }
        ]
      ]
    }
  ]
}

@patch('routers.in_game.tokens.get_all_board_figures')
def test_show_all_figures_success(mock_get_all_board_figures):
    mock_get_all_board_figures.return_value = mock_figures_data["figures"]

    response = client.get("game/1/show_all_figures",)

    assert response.status_code == 200
    assert response.json() == mock_figures_data


@patch('routers.in_game.tokens.get_all_board_figures')
def test_show_all_figures_error(mock_get_all_board_figures):
    mock_get_all_board_figures.side_effect = ValueError('Figures not found')
    
    response = client.get("/game/1/show_all_figures")
    assert response.status_code == 404
    assert response.json() == {"detail": "Figures not found"}


# ======================= Test list_games_by_session_id ============================

mock_games_data = [
    {"id": 1, "name": "Game 1", "host_id": 1, "in_game": True, "is_private": False, "users": {
        "min": 2, "max": 4, "players": [{'2': "user2"}, {'1': "user1"}]}},
    {"id": 2, "name": "Game 2", "host_id": 2, "in_game": False, "is_private": True, "users": {
        "min": 2, "max": 4, "players": [{'3': "user3"}, {'4': "user4"}]}},
]

@patch('core.games.get_games_by_session_id')
def test_get_active_games_by_session_id(mock_get_games_by_session_id):
    mock_get_games_by_session_id.return_value = mock_games_data

    response = client.get("/get_session_id_games/2")

    assert response.status_code == 200
    assert response.json() == mock_games_data
    mock_get_games_by_session_id.assert_called_once_with(2)

# ======================= Test get_session_id ============================

@patch('core.games.new_session_id')
def test_get_session_id(mock_new_session_id):
    mock_new_session_id.return_value = 1

    response = client.get("/get_session_id")

    assert response.status_code == 200
    assert response.json() == {"session_id": 1}

@patch('core.games.new_session_id')
def test_get_session_id_error(mock_new_session_id):
    mock_new_session_id.side_effect = ValueError("Could not create a new id")
    response = client.get("/get_session_id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Could not create a new  id"}

@patch('core.games.new_session_id')
def test_get_session_id_notOne(mock_new_session_id):
    mock_new_session_id.return_value = 2

    response = client.get("/get_session_id")

    assert response.status_code == 200
    assert response.json() == {"session_id": 2}

# ======================= Test get_player_id ============================
@patch('core.games.create_game_message')
@patch('core.connections.ConnectionManager.broadcast')
@patch('core.games.get_player_id')
def test_get_player_id(mock_get_player_id, mock_broadcast, mock_create_game_message):
    mock_get_player_id.return_value = 1
    mock_broadcast.return_value = None
    mock_create_game_message.return_value = None


    response = client.get("/games/1/1/get_player_id")

    assert response.status_code == 200
    assert response.json() == {"player_id": 1}

@patch('core.games.get_player_id')
def test_get_player_id_no_game(mock_get_player_id):
    mock_get_player_id.side_effect = ValueError("Game not found")

    response = client.get("/games/1/1/get_player_id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


@patch('core.games.get_player_id')
def test_get_player_id_no_player(mock_get_player_id):
    mock_get_player_id.side_effect = ValueError("Player not found")

    response = client.get("/games/1/1/get_player_id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Player not found"}

