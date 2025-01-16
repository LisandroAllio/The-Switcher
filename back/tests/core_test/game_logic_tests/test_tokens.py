import unittest
from unittest.mock import patch, MagicMock
from models.tables import Game, Player, userFigureCard, gameToken

# Asumimos que estas clases están definidas en tu módulo
from core.game_logic.tokens import initialize_game_tokens, get_all_board_figures
from schemas.game import Game
from schemas.board import BoardFigureModel

class TestInitializeGameTokens(unittest.TestCase):
    
    @patch('core.game_logic.tokens.Session')
    @patch('core.game_logic.tokens.random.shuffle')
    def test_initialize_game_tokens(self, mock_shuffle, mock_session):
        mock_game = MagicMock()
        mock_game.id = 1
        mock_game.game_tokens = []
        
        # Configurar el retorno del método query
        mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = mock_game
        
        initialize_game_tokens(1)
        
        # Verificar que la sesión se haya creado
        mock_session.assert_called_once()
        
        # Verificar que el método query se llamó con el id correcto
        mock_session.return_value.query.assert_called_once_with(Game)
        mock_session.return_value.query.return_value.filter_by.assert_called_once_with(id=1)
        
        # Verificar que se agregaron 36 tokens al juego
        self.assertEqual(len(mock_game.game_tokens), 36)
        
        mock_session.return_value.commit.assert_called_once()
        
        # Verificar que la mezcla se haya llamado
        mock_shuffle.assert_called_once()

    @patch('core.game_logic.tokens.Session')
    def test_initialize_game_tokens_game_not_found(self, mock_session):
        # Configurar el mock de la sesión para que no encuentre el juego
        mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = None
        
        with self.assertRaises(ValueError) as context:
            initialize_game_tokens(999)  # ID que no existe
        
        self.assertEqual(str(context.exception), "Game not found")
        mock_session.return_value.close.assert_called_once()

class TestGetAllBoardFigures(unittest.TestCase):

    @patch('core.game_logic.tokens.BoardFigureModel')
    @patch('core.game_logic.tokens.get_figures')
    @patch('core.game_logic.tokens.get_board_figures')
    @patch('core.game_logic.tokens.Session')
    def test_get_all_board_figures_success(self, mock_session, mock_get_board_figures, mock_get_figures, mock_board_figure_model):
        # Configurar la sesión mock
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Crear un juego mock con jugadores y tokens
        mock_game = MagicMock(spec=Game)
        mock_game.id = 1

        # Crear un jugador con una carta de figura revelada
        mock_player = MagicMock(spec=Player)
        mock_figure_card = MagicMock(spec=userFigureCard)
        mock_figure_card.revealed = True
        mock_figure_card.blocked = False  # La figura no está bloqueada
        mock_figure_card.type = 'figure_type'
        mock_figure_card.id = 1
        mock_player.user_figure_cards = [mock_figure_card]
        mock_game.players = [mock_player]

        # Agregar tokens al juego
        mock_token = MagicMock(spec=gameToken)
        mock_token.x_coordinate = 0
        mock_token.y_coordinate = 0
        mock_token.color = 'red'
        mock_game.game_tokens = [mock_token]

        # Configurar el retorno del método query
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game

        # Configurar retornos de funciones auxiliares
        mock_get_board_figures.return_value = ['figure1', 'figure2']  # Simulamos que se encuentran figuras
        mock_get_figures.return_value = ['token1', 'token2']  # Simulamos que se encuentran tokens

        # Configurar BoardFigureModel.from_db para que devuelva un objeto simulado
        mock_board_figure_model.from_db.return_value = MagicMock(spec=BoardFigureModel)

        # Ejecutar la función
        result = get_all_board_figures(1)

        # Verificar que el resultado es una lista con elementos
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

        # Verificar que la sesión se cerró
        mock_session_instance.close.assert_called_once()

        # Verificar que las funciones auxiliares se llamaron correctamente
        mock_get_board_figures.assert_called_once_with('figure_type', [(0, 0, 'red')])
        mock_get_figures.assert_called_once_with(1, ['figure1', 'figure2'], mock_session_instance)

        # Verificar que BoardFigureModel.from_db fue llamado correctamente
        mock_board_figure_model.from_db.assert_called_once_with(mock_figure_card, ['token1', 'token2'])

    @patch('core.game_logic.tokens.Session')
    def test_get_all_board_figures_game_not_found(self, mock_session):
        # Configurar el mock de la sesión para que no encuentre el juego
        mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = None

        with self.assertRaises(ValueError) as context:
            get_all_board_figures(999)  # ID que no existe

        self.assertEqual(str(context.exception), "Game not found")
        mock_session.return_value.close.assert_called_once()

    @patch('core.game_logic.tokens.Session')
    @patch('core.game_logic.aux.figDetector.get_board_figures')
    def test_get_all_board_figures_figures_not_found(self, mock_get_board_figures, mock_session):
        # Configurar los mocks
        mock_game = MagicMock(spec=Game)
        mock_game.id = 1
        mock_game.players = []
        mock_game.game_tokens = []

        # Crear jugador sin cartas de figuras reveladas
        mock_player = MagicMock(spec=Player)
        mock_figure_card = MagicMock(spec=userFigureCard)
        mock_figure_card.revealed = True
        mock_figure_card.type = 'figure_type'
        mock_player.user_figure_cards = [mock_figure_card]
        mock_game.players.append(mock_player)

        # No hay tokens en el tablero

        # Configurar el retorno del método query
        mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = mock_game

        # Configurar retorno de función
        mock_get_board_figures.return_value = []

        with self.assertRaises(ValueError) as context:
            get_all_board_figures(1)

        self.assertEqual(str(context.exception), "Figures not found")

        # Verificar que la sesión se cerró
        mock_session.return_value.close.assert_called_once()