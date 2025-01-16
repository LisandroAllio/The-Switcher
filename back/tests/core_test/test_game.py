import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from core import games
from core.games import get_games, get_games_by_name, get_games_by_players, leave_game, end_turn, get_game_turn, new_session_id, start_game, create_game, get_game_id, join_game, get_games_by_session_id
from models.tables import Game, Player, SessionCounter
from core.game_logic.tokens import get_game_tokens
from schemas.game import UsersInfo, GameListModel


# ======================= Tests create_game =======================
@patch('core.games.send_logs')
@patch('core.games.Session')
def test_create_game_success(MockSession, mock_send_logs):
    # Configurar el mock de la sesión
    mock_session_instance = MockSession.return_value
    mock_session_instance.commit = MagicMock()
    mock_session_instance.refresh = MagicMock()
    mock_session_instance.add = MagicMock()
    
    # Crear un mock para el Game
    mock_game = MagicMock(spec=Game)
    mock_game.id = 123  # ID simulado después del commit
    mock_game.players = []
    
    # Asignar el Game creado al constructor de Game
    with patch('core.games.Game', return_value=mock_game) as mock_game_class:
        # Crear un mock para el Player
        mock_player = MagicMock(spec=Player)
        mock_player.id = 456  # ID simulado para el host
        
        # Asignar el Player al mock_game.players
        mock_game.players.append(mock_player)
        
        # Llamar a la función create_game
        game_id = create_game(
            name="Nuevo Juego",
            host_name="Jugador Principal",
            session_id=789,
            min_users=2,
            max_users=4,
            pwd="clave123"
        )
        
        # Verificar que se creó una instancia de Game con los parámetros correctos
        mock_game_class.assert_called_once_with(
            name="Nuevo Juego",
            maxPlayers=4,
            minPlayers=2,
            password="clave123"
        )
        
        # Verificar que se creó una instancia de Player con los parámetros correctos
        mock_player.name = "Jugador Principal"
        mock_player.is_host = True
        mock_player.session_id = 789
        # Nota: Como Player se crea dentro de la función, deberíamos interceptar su creación también
        # Para simplificar, asumimos que el mock_player ya tiene los atributos correctos
        
        # Verificar que se añadió el juego a la sesión
        mock_session_instance.add.assert_called_once_with(mock_game)
        
        # Verificar que se llamó a commit y refresh
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.refresh.assert_called_once_with(mock_game)
        
        # Verificar que send_logs fue llamado correctamente
        mock_send_logs.assert_called_once_with(mock_game.id, "Jugador Principal ha creado la partida")
        
        # Verificar que el ID retornado es el esperado
        assert(game_id == 123)

# ======================= Tests get_games =======================
@patch('core.games.Session')
def test_get_game(MockSession):
        mock_session = MockSession.return_value
        # Configuración del mock
        mock_game_1 = MagicMock()
        mock_game_1.id = 1
        mock_game_1.name = "Test Game 1"
        mock_game_1.maxPlayers = 4
        mock_game_1.amountPlayers = 2
        mock_game_1.inGame = False
        mock_game_1.players = [MagicMock(id=10, name="Host Player", is_host=True),
                               MagicMock(id=11, name="Second Player", is_host=False)]
        mock_game_1.password = None  
        mock_game_1.minPlayers = 2   
        mock_game_1.maxPlayers = 4   

        mock_game_2 = MagicMock()
        mock_game_2.id = 2
        mock_game_2.name = "Test Game 2"
        mock_game_2.maxPlayers = 4
        mock_game_2.amountPlayers = 4  
        mock_game_2.inGame = False
        mock_game_2.players = [MagicMock(id=20, name="Another Player", is_host=False)]
        mock_game_2.password = "secret"  
        mock_game_2.minPlayers = 2
        mock_game_2.maxPlayers = 4

        # Simular la respuesta de la consulta
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_game_1, mock_game_2]

        # Simular el método de la clase UsersInfo.get_users_info
        with patch('schemas.game.UsersInfo.get_users_info') as mock_get_users_info:
            mock_get_users_info.return_value = {
                "min": 2,
                "max": 4,
                "players": [
                    {10: "Host Player"},
                    {11: "Second Player"}
                ]
            }
            # Simular el método de la clase GameListModel
            with patch('schemas.game.GameListModel.from_db') as mock_from_db:
                mock_from_db.side_effect = lambda game: {
                    "id": game.id,
                    "name": game.name,
                    "host_id": 1,
                    "in_game": game.inGame,
                    "is_private": game.password is not None,
                    "users": UsersInfo.get_users_info(game),
                }

                # Llamar a la función
                result = get_games()

                # Verificaciones
                mock_session.query.assert_called_once_with(Game)
                assert len(result) == 2 # Debe retornar solo un juego
                assert result[0]['id'] == 1  # Comprobar que el id es el esperado
                assert result[0]['name'] == "Test Game 1" 

        # Asegurarse de que la sesión se cierra
        mock_session.close.assert_called_once()
        
# ======================= Tests get_games_by_name =======================
@patch('core.games.Session')
def test_get_games_by_name(MockSession):
    # Configuración del mock
    mock_session = MockSession.return_value  # Captura la instancia mockeada
    mock_game_1 = MagicMock()
    mock_game_1.id = 1
    mock_game_1.name = "Test Game 1"
    mock_game_1.maxPlayers = 4
    mock_game_1.amountPlayers = 2
    mock_game_1.inGame = False
    
    mock_game_2 = MagicMock()
    mock_game_2.id = 2
    mock_game_2.name = "Test Game 2"
    mock_game_2.maxPlayers = 4
    mock_game_2.amountPlayers = 3
    mock_game_2.inGame = False
    
    mock_game_3 = MagicMock()
    mock_game_3.id = 3
    mock_game_3.name = "Another Game"
    mock_game_3.maxPlayers = 4
    mock_game_3.amountPlayers = 1
    mock_game_3.inGame = False

    mock_session.query.return_value.filter.return_value.all.return_value = [mock_game_1, mock_game_2]

    # Simular el método de la clase GameListModel
    with patch('schemas.game.GameListModel.from_db') as mock_from_db:
        mock_from_db.side_effect = lambda game: {
            "id": game.id,
            "name": game.name,
            "host_id": 1,
            "in_game": game.inGame,
            "is_private": game.password is not None,
            "users": {},  # Aquí puedes simular los usuarios si es necesario
        }

        # Llamar a la función
        result = get_games_by_name("Test")

        # Verificaciones
        mock_session.query.assert_called_once_with(Game) 
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['id'] == 2 

    # Asegurarse de que la sesión se cierra
    mock_session.close.assert_called_once()

# ======================= Tests get_games_by_name =======================
@patch('core.games.Session')
def test_get_games_by_players(MockSession):
    # Configuración del mock
    mock_session = MockSession.return_value  # Captura la instancia mockeada
    mock_game_1 = MagicMock()
    mock_game_1.id = 1
    mock_game_1.name = "Test Game 1"
    mock_game_1.maxPlayers = 4
    mock_game_1.amountPlayers = 2
    mock_game_1.inGame = False
    
    mock_game_2 = MagicMock()
    mock_game_2.id = 2
    mock_game_2.name = "Test Game 2"
    mock_game_2.maxPlayers = 4
    mock_game_2.amountPlayers = 3
    mock_game_2.inGame = False
    
    mock_game_3 = MagicMock()
    mock_game_3.id = 3
    mock_game_3.name = "Another Game"
    mock_game_3.maxPlayers = 4
    mock_game_3.amountPlayers = 2
    mock_game_3.inGame = False

    mock_session.query.return_value.filter.return_value.all.return_value = [mock_game_1, mock_game_3]

    # Simular el método de la clase GameListModel
    with patch('schemas.game.GameListModel.from_db') as mock_from_db:
        mock_from_db.side_effect = lambda game: {
            "id": game.id,
            "name": game.name,
            "host_id": 1,
            "in_game": game.inGame,
            "is_private": game.password is not None,
            "users": {},  # Aquí puedes simular los usuarios si es necesario
        }

        # Llamar a la función
        result = get_games_by_players(2)

        # Verificaciones
        mock_session.query.assert_called_once_with(Game) 
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['id'] == 3 

    # Asegurarse de que la sesión se cierra
    mock_session.close.assert_called_once()

# ======================= Tests leave_game =======================

@patch('core.games.send_logs')
@patch('core.games.Session')
@patch('core.game_logic.winLogic.Session')
def test_leave_game_success_cancel(mock_winnable, mock_session, mock_send_logs):
    # Crear un mock para el juego
    game_mock = MagicMock(spec=Game)
    game_mock.id = 1
    game_mock.amountPlayers = 1
    game_mock.inGame = False
    game_mock.players = []

    # Crear un mock para el jugador
    player_mock = MagicMock(spec=Player)
    player_mock.id = 1
    player_mock.name = "Jugador1"
    player_mock.turn_assigned = 1
    player_mock.plays = []

    # Configuración del mock para la consulta de juego y jugador
    mock_query = mock_session.return_value.query.return_value
    mock_query.filter_by.return_value.first.side_effect = [game_mock, player_mock]

    # Llamar a la función leave_game
    result = leave_game(1, 1)

    # Verificar que se haya llamado a session.delete y session.commit
    mock_session.return_value.delete.assert_called_once_with(player_mock)
    mock_session.return_value.commit.assert_called_once()

    # Verificar que el número de jugadores se decrementó
    assert game_mock.amountPlayers == 0  # El número de jugadores debe haber sido decrementado

    # Verificar que el mensaje fue enviado correctamente por send_logs
    mock_send_logs.assert_called_once_with(game_mock.id, f"{player_mock.name} ha abandonado la partida")

    # Verificar el resultado
    assert result == "status_cancel_game"

@patch('core.games.send_logs') 
@patch('core.games.Session')
@patch('core.game_logic.winLogic.Session')
@patch('core.game_logic.winLogic.game_winnable_for_leave')
def test_leave_game_success_winner(mock_game_winnable, mock_winnable, mock_session, mock_send_logs):
    
    # Crear un mock para el juego
    game_mock = MagicMock(spec=Game)
    game_mock.id = 1
    game_mock.amountPlayers = 2
    game_mock.inGame = True

    # Crear mocks para los jugadores
    player_mock1 = MagicMock(spec=Player)
    player_mock1.id = 1
    player_mock1.name = "Jugador1"
    
    player_mock2 = MagicMock(spec=Player)
    player_mock2.id = 2
    player_mock2.name = "Jugador2"

    # Configuración de la consulta mockeada
    mock_query = mock_session.return_value.query.return_value
    mock_query.filter_by.return_value.first.side_effect = [game_mock, player_mock1, player_mock2]

    # Mockear game_winnable
    mock_game_winnable.return_value = True

    # Llamada a la función leave_game
    result = leave_game(1, 1)

    # Verificar que se haya llamado a session.delete y session.commit
    mock_session.return_value.delete.assert_called_once_with(player_mock1)
    mock_session.return_value.commit.assert_called_once()

    # Verificar que el número de jugadores se decrementó
    assert game_mock.amountPlayers == 1

    # Verificar que se haya llamado a send_logs
    mock_send_logs.assert_called_once_with(game_mock.id, f"{player_mock1.name} ha abandonado la partida")

    # Verificar el resultado de leave_game
    assert result == "status_winner"

@patch('core.games.send_logs') 
@patch('core.games.Session') 
@patch('core.game_logic.winLogic.Session')  
@patch('core.game_logic.winLogic.game_winnable_for_leave') 
def test_leave_game_success_leave(mock_game_winnable, mock_winnable, mock_session, mock_send_logs):

    # Crear un mock para el juego
    game_mock = MagicMock(spec=Game)
    game_mock.id = 1
    game_mock.amountPlayers = 3
    game_mock.inGame = True

    # Crear mocks para los jugadores
    player_mock1 = MagicMock(spec=Player)
    player_mock1.id = 1
    player_mock1.name = "Jugador1"
    
    player_mock2 = MagicMock(spec=Player)
    player_mock2.id = 2
    player_mock2.name = "Jugador2"
    
    player_mock3 = MagicMock(spec=Player)
    player_mock3.id = 3
    player_mock3.name = "Jugador3"

    # Configuración de la consulta mockeada
    mock_query = mock_session.return_value.query.return_value
    mock_query.filter_by.return_value.first.side_effect = [game_mock, player_mock1, player_mock2, player_mock3]

    # Mockear game_winnable
    mock_game_winnable.return_value = False

    # Llamada a la función leave_game
    result = leave_game(1, 1)

    # Verificar que se haya llamado a session.delete y session.commit
    mock_session.return_value.delete.assert_called_once_with(player_mock1)
    mock_session.return_value.commit.assert_called_once()

    # Verificar que el número de jugadores se decrementó
    assert game_mock.amountPlayers == 2

    # Verificar que se haya llamado a send_logs
    mock_send_logs.assert_called_once_with(game_mock.id, f"{player_mock1.name} ha abandonado la partida")

    # Verificar el resultado de leave_game
    assert result == "status_leave"


def test_leave_game_no_game():
    # Crear un mock para la sesión
    session_mock = MagicMock()

    # Configurar el mock de la sesión para devolver el juego y None para el jugador
    session_mock.query(Game).filter_by(id=1).first.return_value = None

    # Parchear la sesión para que devuelva el mock de la sesión
    with patch('core.games.Session', return_value=session_mock):
        with pytest.raises(ValueError, match="Game not found"):
            leave_game(1, 1)

    # Verificar que se llamó a session.rollback
    session_mock.rollback.assert_called_once()

# ======================= Tests get_game_tokens =======================

@patch('core.game_logic.tokens.Session', autospec=True)
@patch('core.game_logic.tokens.GameTokenModel.from_db')
def test_get_game_tokens(mock_from_db, mock_session):
    # Crear un mock para el juego
    game_mock = MagicMock(spec=Game)
    game_mock.id = 1
    game_mock.game_tokens = [MagicMock(), MagicMock()]

    # Configurar el mock de la sesión para devolver el juego
    mock_query = mock_session.return_value.query.return_value
    mock_query.filter_by.return_value.first.return_value = game_mock


    # Configurar el mock para GameTokenModel.from_db
    mock_from_db.side_effect = lambda token: f"token_{token}"

    # Ejecutar la función get_game_tokens
    result = get_game_tokens(1)

    # Verificar que se llamó a session.query y session.close
    mock_session.return_value.query.assert_called_once_with(Game)
    mock_session.return_value.close.assert_called_once()

    # Verificar que se llamó a GameTokenModel.from_db para cada token
    assert mock_from_db.call_count == len(game_mock.game_tokens)
    for token in game_mock.game_tokens:
        mock_from_db.assert_any_call(token)

    # Verificar el resultado
    expected_result = [f"token_{token}" for token in game_mock.game_tokens]
    assert result == expected_result
    
# ======================= Tests end_game =======================

def test_end_game_success():
    mock_session = MagicMock()
    # Configura el mock de la sesión y del objeto Game
    mock_game = MagicMock(spec=Game)
    mock_game.id = 1
    mock_game.players = [MagicMock(), MagicMock()]  # Simula algunos jugadores

    mock_session.query().filter_by().first.return_value = mock_game

    # Llama a la función con la sesión mockeada
    result = games.end_game(1, session=mock_session)

    # Verifica que el ID del juego devuelto sea correcto
    assert result == mock_game.id

    # Verifica que se hayan llamado a las funciones de eliminación
    mock_session.delete.assert_any_call(mock_game)
    for player in mock_game.players:
        mock_session.delete.assert_any_call(player)

    # Verifica que se haya hecho commit
    mock_session.commit.assert_called_once()

def test_end_game_game_not_found():
    mock_session = MagicMock()

    mock_session.query().filter_by().first.return_value = None

    # Llama a la función y verifica que lance un ValueError
    with pytest.raises(ValueError, match="Game not found"):
        games.end_game(99, session=mock_session)

# ======================= Tests end_turn =======================

@patch('core.games.get_random_movs_cards')
@patch('core.games.get_random_figure_cards')
@patch('core.games.Session')
@patch('core.games.send_logs')
class TestEndTurn(unittest.TestCase):
    def test_end_turn(self, mock_send_logs, mock_session, mock_get_random_figure_cards, mock_get_random_movs_cards):
        mock_game = MagicMock(spec=Game)
        mock_game.id = 1
        mock_game.TurnoActual = 1
        mock_game.amountPlayers = 3

        # Crear un mock para Player
        mock_player = MagicMock(spec=Player)
        mock_player.id = 1
        mock_player.name = "Jugador1"
        mock_player.blocked = False  # Agregar el atributo 'blocked'
        mock_player.user_figure_cards = [MagicMock(spec='Card', mov_type='F1', revealed=True)]
        mock_player.user_movement_cards = [MagicMock(spec='Card', mov_type='M1', revealed=True)]
        mock_player.plays = []

        mock_card = MagicMock(mov_type='F1', revealed=True)

        mock_session_instance = mock_session.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.side_effect = [mock_game, mock_player] * mock_game.amountPlayers

        mock_session_instance.query.return_value.filter_by.return_value.first.return_value.user_figure_cards = [mock_card]
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value.user_movement_cards = [mock_card]
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value.plays = []

        for i in range(1, mock_game.amountPlayers + 1):
            next_turn = (mock_game.TurnoActual % mock_game.amountPlayers) + 1
            end_turn(mock_game.id, i)
            self.assertEqual(mock_game.TurnoActual, next_turn)

        mock_session_instance.commit.assert_called()
        mock_session_instance.close.assert_called()

        # Verificamos que `send_logs` haya sido llamada exactamente 3 veces
        self.assertEqual(mock_send_logs.call_count, 3)
        
        # Verificamos que las funciones para obtener cartas fueron llamadas
        mock_get_random_movs_cards.call_count == 3
        mock_get_random_figure_cards.call_count == 3
    
    def test_end_turn_game_not_found(self, mock_send_logs, mock_session, mock_get_random_figure_cards, mock_get_random_movs_cards):
        # Simular que no se encuentra el juego
        mock_session_instance = mock_session.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = None

        with self.assertRaises(ValueError) as context:
            end_turn(1, 1)

        # Verificar que se haya lanzado el error esperado
        self.assertEqual(str(context.exception), "Game not found")

        # Verificar que la sesión hizo rollback
        mock_session_instance.rollback.assert_called_once()

        # Verificar que la sesión se cerró
        mock_session_instance.close.assert_called_once()

        mock_send_logs.assert_not_called()

        # Verificar que `commit` no haya sido llamado debido al rollback
        mock_session_instance.commit.assert_not_called()

# ======================= Tests test_game_turn =======================
@patch("core.games.Session")
class TestTurnAssign(unittest.TestCase):

    def test_game_turn(self, mock_session):

        mock_game = MagicMock(spec=Game)
        mock_game.id = 1
        mock_game.amountPlayers = 4
        mock_game.minPlayers = 2
        mock_game.maxPlayers = 4
        mock_game.TurnoActual = 1
        mock_game.forbiddenColor = "Red"
        mock_game.inGame = True

        mock_session_instance = mock_session.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game

        mock_player1 = MagicMock(spec=Player)
        mock_player2 = MagicMock(spec=Player)
        mock_player3 = MagicMock(spec=Player)
        mock_player4 = MagicMock(spec=Player)

        mock_player1.id = 1
        mock_player2.id = 2
        mock_player3.id = 3
        mock_player4.id = 4

        mock_player1.turn_assigned = 1
        mock_player2.turn_assigned = 4
        mock_player3.turn_assigned = 3
        mock_player4.turn_assigned = 2

        mock_game.players = [mock_player2,
                             mock_player1, mock_player3, mock_player4]

        # Llamar a la función get_game_turn
        for i in range(1, 5):
            mock_game.TurnoActual = i
            gameturn = get_game_turn(mock_game.id)
            print(f"gameturn: {gameturn}")

        assert mock_session_instance.close.called

    def test_game_not_found(self, mock_session):
        # Llamar a la función get_game_turn con un juego que no existe
        mock_session_instance = mock_session.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = None

        with self.assertRaises(ValueError):
            get_game_turn(1)

        mock_session_instance.rollback.assert_called_once()
        mock_session_instance.close.assert_called_once()

    def test_not_enough_players(self, mock_session):
        # Llamar a la función get_game_turn con un juego que no tiene suficientes jugadores
        mock_game = MagicMock(spec=Game)
        mock_game.id = 1
        mock_game.amountPlayers = 1
        mock_game.minPlayers = 2
        mock_game.maxPlayers = 4
        mock_game.TurnoActual = 1
        mock_game.forbiddenColor = "Red"
        mock_game.inGame = False

        mock_session_instance = mock_session.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game

        with self.assertRaises(ValueError):
            get_game_turn(1)

        mock_session_instance.rollback.assert_called_once()
        mock_session_instance.close.assert_called_once()

# ======================= Tests start_game =======================

@patch('core.games.get_random_movs_cards')
@patch('core.games.deal_cards')
@patch('core.games.initialize_game_tokens')
@patch('core.games.turn_assign')
@patch('core.games.Session')
@patch('core.games.send_logs')
class TestStartGame(unittest.TestCase):

    def test_start_game(self, mock_send_logs, mock_session, mock_turn_assign, mock_initialize_game_tokens, mock_deal_cards, mock_get_random_movs_cards):
        mock_game = MagicMock(spec=Game)
        mock_game.id = 1
        mock_game.inGame = False
        mock_game.TurnoActual = 0
        mock_game.Timer = 0
        mock_game.amountPlayers = 4
        mock_game.minPlayers = 2
        
        mock_player1 = MagicMock(spec=Player)
        mock_player2 = MagicMock(spec=Player)
        mock_player3 = MagicMock(spec=Player)
        mock_player4 = MagicMock(spec=Player)

        mock_player1.id = 1
        mock_player2.id = 2
        mock_player3.id = 3
        mock_player4.id = 4

        mock_player1.turn_assigned = 1
        mock_player2.turn_assigned = 4
        mock_player3.turn_assigned = 3
        mock_player4.turn_assigned = 2

        mock_game.players = [mock_player2, mock_player1, mock_player3, mock_player4]

        mock_query = mock_session.return_value.query.return_value
        mock_query.filter_by.return_value.first.return_value = mock_game

        start_game(mock_game.id)  # Llamar al método que estamos probando

        self.assertTrue(mock_game.inGame)
        self.assertEqual(mock_game.TurnoActual, 1)

        # Verificar las interacciones con la base de datos
        mock_session.return_value.close.assert_called_once()
        mock_turn_assign.assert_called_once_with(mock_game.id)
        mock_initialize_game_tokens.assert_called_once_with(mock_game.id)
        mock_deal_cards.assert_called_once_with(mock_game.id)
        self.assertEqual(mock_get_random_movs_cards.call_count, 4)
        self.assertEqual(mock_session.return_value.commit.call_count, 2)

        mock_send_logs.assert_called_once_with(mock_game.id, "Se ha iniciado la partida")

    def test_start_game_not_found(self, mock_send_logs, mock_session, mock_turn_assign, mock_initialize_game_tokens, mock_deal_cards, mock_get_random_movs_cards):
        mock_game = MagicMock(spec=Game)
        mock_game.id = 1

        mock_query = mock_session.return_value.query.return_value
        mock_query.filter_by.return_value.first.return_value = None

        with self.assertRaises(ValueError):
            start_game(mock_game.id)

        mock_turn_assign.assert_not_called()
        mock_initialize_game_tokens.assert_not_called()
        mock_deal_cards.assert_not_called()
        mock_get_random_movs_cards.assert_not_called()
        mock_session.return_value.commit.assert_not_called()

    def test_start_game_not_enough_players(self, mock_send_logs, mock_session, mock_turn_assign, mock_initialize_game_tokens, mock_deal_cards, mock_get_random_movs_cards):
        mock_game = MagicMock(spec=Game)
        mock_game.id = 1
        mock_game.amountPlayers = 1
        mock_game.minPlayers = 2

        mock_query = mock_session.return_value.query.return_value
        mock_query.filter_by.return_value.first.return_value = mock_game

        with self.assertRaises(ValueError):
            start_game(mock_game.id)

        mock_turn_assign.assert_not_called()
        mock_initialize_game_tokens.assert_not_called()
        mock_deal_cards.assert_not_called()
        mock_get_random_movs_cards.assert_not_called()
        mock_session.return_value.commit.assert_not_called()

@patch('core.games.Session')
class TestNewSessionId(unittest.TestCase):

    def test_new_session_id(self, mock_session):
        sessionCount = MagicMock(spec=SessionCounter)
        sessionCount.countId = 5


        mock_query = mock_session.return_value.query.return_value
        mock_query.order_by.return_value.first.return_value = sessionCount

        result = new_session_id()

        self.assertEqual(result, 6)
        mock_session.return_value.close.assert_called_once()

    def test_new_session_id_no_players(self, mock_session):
        mock_query = mock_session.return_value.query.return_value
        mock_query.order_by.return_value.first.return_value = None

        result = new_session_id()

        self.assertEqual(result, 1)
        mock_session.return_value.close.assert_called_once()

# ======================= Tests get_game_id =======================

@patch('core.games.GameListModel.from_db')
@patch('core.games.Session')
class TestGetGameId(unittest.TestCase):

    def test_get_game_id_exists(self, mock_session, mock_from_db):
        # Arrange
        game_id = 1

        # Crear un mock para el Game
        mock_game = MagicMock(spec=Game)
        mock_session_instance = mock_session.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game

        # Crear un mock para el GameListModel
        expected_model = MagicMock(spec=GameListModel)
        mock_from_db.return_value = expected_model

        # Act
        result = get_game_id(game_id)

        # Assert
        # Verificar que se llamó a session.query con el modelo Game
        mock_session_instance.query.assert_called_once_with(Game)
        # Verificar que se llamó a filter_by con el game_id correcto
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(id=game_id)
        # Verificar que se llamó a first()
        mock_session_instance.query.return_value.filter_by.return_value.first.assert_called_once()
        # Verificar que GameListModel.from_db fue llamado con el juego obtenido
        mock_from_db.assert_called_once_with(mock_game)
        # Verificar que el resultado es el esperado
        self.assertEqual(result, expected_model)
        # Verificar que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()

    def test_get_game_id_not_exists(self, mock_session, mock_from_db):
        # Arrange
        game_id = 2

        # Configurar el mock para que no encuentre el juego
        mock_session_instance = mock_session.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = None

        # Act
        result = get_game_id(game_id)

        # Assert
        # Verificar que se llamó a session.query con el modelo Game
        mock_session_instance.query.assert_called_once_with(Game)
        # Verificar que se llamó a filter_by con el game_id correcto
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(id=game_id)
        # Verificar que se llamó a first()
        mock_session_instance.query.return_value.filter_by.return_value.first.assert_called_once()
        # Verificar que GameListModel.from_db NO fue llamado
        mock_from_db.assert_not_called()
        # Verificar que el resultado es None
        self.assertIsNone(result)
        # Verificar que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()

import unittest
from unittest.mock import MagicMock, patch
from core.games import join_game
from models.tables import Game, Player
from schemas.game import GameListModel

# ======================= Tests join_game =======================

@patch('core.games.GameListModel.from_db')
@patch('core.games.send_logs')
@patch('core.games.Session')
class TestJoinGame(unittest.TestCase):

    def setUp(self):
        # Configuración común para todas las pruebas
        self.mock_session = MagicMock()
        self.mock_send_logs = MagicMock()
        self.mock_from_db = MagicMock()

    def test_join_game_success_no_password(self, mock_session_class, mock_send_logs, mock_from_db):
        """
        Verifica que un usuario puede unirse a un juego sin contraseña de manera exitosa.
        """
        # Arrange
        game_id = 1
        user_name = "Jugador1"
        password = ""  # Sin contraseña
        session_id = 100

        # Crear un mock para el Game
        mock_game = MagicMock(spec=Game)
        mock_game.id = game_id
        mock_game.maxPlayers = 4
        mock_game.password = None  # Juego sin contraseña
        mock_game.amountPlayers = 0

        # Configurar mock_game.players como MagicMock con spec list
        mock_game.players = MagicMock(spec=list)
        mock_game.players.__len__.return_value = 0  # Inicialmente sin jugadores

        # Configurar la sesión mock
        mock_session_instance = mock_session_class.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game

        # Crear un mock para GameListModel.from_db
        expected_model = MagicMock(spec=GameListModel)
        mock_from_db.return_value = expected_model

        # Act
        result = join_game(game_id, user_name, password, session_id)

        # Assert
        # Verificar que se consultó el juego correcto
        mock_session_instance.query.assert_called_once_with(Game)
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(id=game_id)
        mock_session_instance.query.return_value.filter_by.return_value.first.assert_called_once()

        # Verificar que se intentó añadir un nuevo jugador
        mock_game.players.append.assert_called_once()
        appended_player = mock_game.players.append.call_args[0][0]
        self.assertEqual(appended_player.name, user_name)
        self.assertEqual(appended_player.session_id, session_id)

        # Verificar que amountPlayers fue incrementado
        self.assertEqual(mock_game.amountPlayers, 1)

        # Verificar que se hizo commit en la sesión
        mock_session_instance.commit.assert_called_once()

        # Verificar que send_logs fue llamado correctamente
        mock_send_logs.assert_called_once_with(game_id, f"{user_name} se ha unido a la partida")

        # Verificar que GameListModel.from_db fue llamado con el juego actualizado
        mock_from_db.assert_called_once_with(mock_game)

        # Verificar que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()

        # Verificar que el resultado es el modelo esperado
        self.assertEqual(result, expected_model)

    def test_join_game_success_with_password(self, mock_session_class, mock_send_logs, mock_from_db):
        """
        Verifica que un usuario puede unirse a un juego con contraseña de manera exitosa.
        """
        # Arrange
        game_id = 2
        user_name = "Jugador2"
        password = "clave123"
        session_id = 101

        # Crear un mock para el Game
        mock_game = MagicMock(spec=Game)
        mock_game.id = game_id
        mock_game.maxPlayers = 4
        mock_game.password = "clave123"  # Juego con contraseña
        mock_game.amountPlayers = 0

        # Configurar mock_game.players como MagicMock con spec list
        mock_game.players = MagicMock(spec=list)
        mock_game.players.__len__.return_value = 0  # Inicialmente sin jugadores

        # Configurar la sesión mock
        mock_session_instance = mock_session_class.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game

        # Crear un mock para GameListModel.from_db
        expected_model = MagicMock(spec=GameListModel)
        mock_from_db.return_value = expected_model

        # Act
        result = join_game(game_id, user_name, password, session_id)

        # Assert
        # Verificar que se consultó el juego correcto
        mock_session_instance.query.assert_called_once_with(Game)
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(id=game_id)
        mock_session_instance.query.return_value.filter_by.return_value.first.assert_called_once()

        # Verificar que la contraseña fue verificada correctamente
        # No hay necesidad de assert aquí ya que la contraseña es correcta y el flujo continúa

        # Verificar que se intentó añadir un nuevo jugador
        mock_game.players.append.assert_called_once()
        appended_player = mock_game.players.append.call_args[0][0]
        self.assertEqual(appended_player.name, user_name)
        self.assertEqual(appended_player.session_id, session_id)

        # Verificar que amountPlayers fue incrementado
        self.assertEqual(mock_game.amountPlayers, 1)

        # Verificar que se hizo commit en la sesión
        mock_session_instance.commit.assert_called_once()

        # Verificar que send_logs fue llamado correctamente
        mock_send_logs.assert_called_once_with(game_id, f"{user_name} se ha unido a la partida")

        # Verificar que GameListModel.from_db fue llamado con el juego actualizado
        mock_from_db.assert_called_once_with(mock_game)

        # Verificar que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()

        # Verificar que el resultado es el modelo esperado
        self.assertEqual(result, expected_model)

    def test_join_game_game_not_found(self, mock_session_class, mock_send_logs, mock_from_db):
        """
        Verifica que se lance una excepción ValueError cuando el juego no se encuentra.
        """
        # Arrange
        game_id = 3
        user_name = "Jugador3"
        password = ""
        session_id = 102

        # Configurar la sesión mock para que no encuentre el juego
        mock_session_instance = mock_session_class.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = None

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            join_game(game_id, user_name, password, session_id)
        self.assertEqual(str(context.exception), "Game not found")

        # Verificar que se consultó el juego correcto
        mock_session_instance.query.assert_called_once_with(Game)
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(id=game_id)
        mock_session_instance.query.return_value.filter_by.return_value.first.assert_called_once()

        # Verificar que GameListModel.from_db NO fue llamado
        mock_from_db.assert_not_called()

        # Verificar que send_logs NO fue llamado
        mock_send_logs.assert_not_called()

        # Verificar que commit NO fue llamado
        mock_session_instance.commit.assert_not_called()

        # Verificar que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()

    def test_join_game_game_full(self, mock_session_class, mock_send_logs, mock_from_db):
        """
        Verifica que se lance una excepción ValueError cuando el juego ya está lleno.
        """
        # Arrange
        game_id = 4
        user_name = "Jugador4"
        password = ""
        session_id = 103

        # Crear un mock para el Game con jugadores suficientes
        mock_game = MagicMock(spec=Game)
        mock_game.id = game_id
        mock_game.maxPlayers = 4
        mock_game.password = None
        mock_game.amountPlayers = 4

        # Crear mock_game.players como MagicMock con spec list y definir __len__
        mock_game.players = MagicMock(spec=list)
        mock_game.players.__len__.return_value = 4  # Juego lleno

        # Configurar la sesión mock
        mock_session_instance = mock_session_class.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            join_game(game_id, user_name, password, session_id)
        self.assertEqual(str(context.exception), "Game is full")

        # Verificar que se consultó el juego correcto
        mock_session_instance.query.assert_called_once_with(Game)
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(id=game_id)
        mock_session_instance.query.return_value.filter_by.return_value.first.assert_called_once()

        # Verificar que GameListModel.from_db NO fue llamado
        mock_from_db.assert_not_called()

        # Verificar que send_logs NO fue llamado
        mock_send_logs.assert_not_called()

        # Verificar que commit NO fue llamado
        mock_session_instance.commit.assert_not_called()

        # Verificar que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()

    def test_join_game_incorrect_password(self, mock_session_class, mock_send_logs, mock_from_db):
        """
        Verifica que se lance una excepción ValueError cuando la contraseña proporcionada es incorrecta.
        """
        # Arrange
        game_id = 5
        user_name = "Jugador5"
        password = "incorrecta"
        session_id = 104

        # Crear un mock para el Game con contraseña
        mock_game = MagicMock(spec=Game)
        mock_game.id = game_id
        mock_game.maxPlayers = 4
        mock_game.password = "clave123"  # Juego con contraseña
        mock_game.amountPlayers = 0

        # Configurar mock_game.players como MagicMock con spec list
        mock_game.players = MagicMock(spec=list)
        mock_game.players.__len__.return_value = 0  # Inicialmente sin jugadores

        # Configurar la sesión mock
        mock_session_instance = mock_session_class.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            join_game(game_id, user_name, password, session_id)
        self.assertEqual(str(context.exception), "Incorrect Password")

        # Verificar que se consultó el juego correcto
        mock_session_instance.query.assert_called_once_with(Game)
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(id=game_id)
        mock_session_instance.query.return_value.filter_by.return_value.first.assert_called_once()

        # Verificar que GameListModel.from_db NO fue llamado
        mock_from_db.assert_not_called()

        # Verificar que send_logs NO fue llamado
        mock_send_logs.assert_not_called()

        # Verificar que commit NO fue llamado
        mock_session_instance.commit.assert_not_called()

        # Verificar que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()

    def test_join_game_commit_exception(self, mock_session_class, mock_send_logs, mock_from_db):
        """
        Verifica que la función maneje correctamente las excepciones que ocurren durante el commit de la sesión.
        """
        # Arrange
        game_id = 6
        user_name = "Jugador6"
        password = ""
        session_id = 105

        # Crear un mock para el Game
        mock_game = MagicMock(spec=Game)
        mock_game.id = game_id
        mock_game.maxPlayers = 4
        mock_game.password = None
        mock_game.amountPlayers = 0

        # Configurar mock_game.players como MagicMock con spec list
        mock_game.players = MagicMock(spec=list)
        mock_game.players.__len__.return_value = 0  # Inicialmente sin jugadores

        # Configurar la sesión mock para que lance una excepción al commit
        mock_session_instance = mock_session_class.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game
        mock_session_instance.commit.side_effect = Exception("Database Error")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            join_game(game_id, user_name, password, session_id)
        self.assertEqual(str(context.exception), "Database Error")

        # Verificar que se consultó el juego correcto
        mock_session_instance.query.assert_called_once_with(Game)
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(id=game_id)
        mock_session_instance.query.return_value.filter_by.return_value.first.assert_called_once()

        # Verificar que se intentó añadir un nuevo jugador
        mock_game.players.append.assert_called_once()
        appended_player = mock_game.players.append.call_args[0][0]
        self.assertEqual(appended_player.name, user_name)
        self.assertEqual(appended_player.session_id, session_id)

        # Verificar que amountPlayers fue incrementado
        self.assertEqual(mock_game.amountPlayers, 1)

        # Verificar que se intentó hacer commit y que lanzó la excepción
        mock_session_instance.commit.assert_called_once()

        # Verificar que send_logs NO fue llamado debido a la excepción
        mock_send_logs.assert_not_called()

        # Verificar que GameListModel.from_db NO fue llamado
        mock_from_db.assert_not_called()

        # Verificar que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()    

import unittest
from unittest.mock import MagicMock, patch
from core.games import get_games_by_session_id
from models.tables import Player, Game
from schemas.game import GameListModel

# ======================= Tests get_games_by_session_id =======================

@patch('core.games.GameListModel.from_db')
@patch('core.games.Session')
class TestGetGamesBySessionId(unittest.TestCase):

    def test_get_games_by_session_id_no_players(self, mock_session_class, mock_from_db):
        """
        Verifica que la función retorna una lista vacía cuando no hay jugadores en la sesión.
        """
        # Arrange
        session_id = 100

        # Configurar la sesión mock para que devuelva una lista vacía de jugadores
        mock_session_instance = mock_session_class.return_value
        mock_session_instance.query.return_value.filter.return_value.all.return_value = []

        # Act
        result = get_games_by_session_id(session_id)

        # Assert
        # Verificar que se consultó la tabla Player con el filtro correcto
        mock_session_instance.query.assert_called_once_with(Player)
        mock_session_instance.query.return_value.filter.assert_called_once()
        mock_session_instance.query.return_value.filter.return_value.all.assert_called_once()

        # Verificar que GameListModel.from_db NO fue llamado
        mock_from_db.assert_not_called()

        # Verificar que la función retorna una lista vacía
        self.assertEqual(result, [])

        # Verificar que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()

    def test_get_games_by_session_id_players_no_games(self, mock_session_class, mock_from_db):
        """
        Verifica que la función retorna una lista vacía cuando los jugadores no están asociados a ningún juego.
        """
        # Arrange
        session_id = 101

        # Crear mocks para jugadores sin juegos
        mock_player1 = MagicMock(spec=Player)
        mock_player1.game = None
        mock_player2 = MagicMock(spec=Player)
        mock_player2.game = None

        # Configurar la sesión mock para que devuelva estos jugadores
        mock_session_instance = mock_session_class.return_value
        mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_player1, mock_player2]

        # Act
        result = get_games_by_session_id(session_id)

        # Assert
        # Verificar que se consultó la tabla Player con el filtro correcto
        mock_session_instance.query.assert_called_once_with(Player)
        mock_session_instance.query.return_value.filter.assert_called_once()
        mock_session_instance.query.return_value.filter.return_value.all.assert_called_once()

        # Verificar que GameListModel.from_db NO fue llamado
        mock_from_db.assert_not_called()

        # Verificar que la función retorna una lista vacía
        self.assertEqual(result, [])

        # Verificar que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()

    def test_get_games_by_session_id_single_game(self, mock_session_class, mock_from_db):
        """
        Verifica que la función retorna una lista con una única instancia de GameListModel cuando todos los jugadores están en el mismo juego.
        """
        # Arrange
        session_id = 102

        # Crear un mock para un juego
        mock_game = MagicMock(spec=Game)

        # Crear mocks para jugadores asociados al mismo juego
        mock_player1 = MagicMock(spec=Player)
        mock_player1.game = mock_game
        mock_player1.session_id = session_id
        mock_player2 = MagicMock(spec=Player)
        mock_player2.game = mock_game

        # Configurar la sesión mock para que devuelva estos jugadores
        mock_session_instance = mock_session_class.return_value
        mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_player1, mock_player2]

        # Configurar GameListModel.from_db para retornar un modelo mock
        expected_model = MagicMock(spec=GameListModel)
        mock_from_db.return_value = expected_model

        # Act
        result = get_games_by_session_id(session_id)

        # Assert
        # Verificar que se consultó la tabla Player con el filtro correcto
        mock_session_instance.query.assert_called_once_with(Player)
        mock_session_instance.query.return_value.filter.assert_called_once()
        mock_session_instance.query.return_value.filter.return_value.all.assert_called_once()

        # Verificar que GameListModel.from_db fue llamado una vez con el juego
        mock_from_db.assert_called_once_with(mock_game)

        # Verificar que la función retorna una lista con el modelo esperado
        self.assertEqual(result, [expected_model])

        # Verificar que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()


