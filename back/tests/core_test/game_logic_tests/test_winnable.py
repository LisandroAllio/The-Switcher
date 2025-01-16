import unittest
from unittest.mock import patch, MagicMock
from core.game_logic.winLogic import game_winnable_for_leave, get_winner

class TestWin(unittest.TestCase):
    
    @patch('core.game_logic.winLogic.Session')
    def test_winLogic_success(self, mock_session):
        
        #Mockear la sesion
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        #Simulacion de las condiciones
        mock_game = MagicMock()
        mock_game.id = 1
        mock_game.inGame = True
        mock_game.players = [MagicMock(id=1)]

        #Simulacion de la query
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game

        #Llamada a la funcion y Assertions
        res = game_winnable_for_leave(1)
        self.assertTrue(res)
        mock_session_instance.close.assert_called_once()

    @patch('core.game_logic.winLogic.Session')
    def test_winLogic_fail(self, mock_session):
        #Mockear la sesion
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        #Simulacion de las condiciones
        mock_game = MagicMock()
        mock_game.id = 1
        mock_game.inGame = False
        mock_game.players = [MagicMock(id=1)]

        #Simulacion de la query
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game

        #Llamada a la funcion y Assertions
        res = game_winnable_for_leave(1)
        self.assertFalse(res)
        mock_session_instance.close.assert_called_once()

    
    @patch('core.game_logic.winLogic.Session')
    @patch('core.game_logic.winLogic.game_winnable_for_leave')
    def test_get_win_success(self,mock_game_winnable ,mock_session):

        #Mockear game_winnable
        mock_game_winnable.return_value = True

        #Simulacion de la sesion
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        #Simulacion de la partida y query
        mock_player = MagicMock()
        mock_player.id = 1
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_player


        #Llamada a la funcion y Assertions
        res = get_winner(1)

        self.assertIsNotNone(res)
        self.assertEqual(res, mock_player)

        mock_session_instance.query.return_value.filter_by.assert_called_once_with(game_id=1)
        mock_session_instance.close.assert_called_once()
