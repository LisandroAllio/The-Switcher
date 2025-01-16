import unittest
from unittest.mock import MagicMock, patch
from models.tables import Game, Player
from core.game_logic.turnLogic import turn_assign


@patch("core.game_logic.turnLogic.Session")
class TestTurnAssign(unittest.TestCase):

    def test_turn_assign(self, mock_session):

        mock_game = MagicMock(spec=Game)
        mock_game.amountPlayers = 4
        mock_game.id = 1
        mock_player1 = MagicMock(spec=Player)
        mock_player1.id = 1
        mock_player2 = MagicMock(spec=Player)
        mock_player2.id = 2
        mock_player3 = MagicMock(spec=Player)
        mock_player3.id = 3
        mock_player4 = MagicMock(spec=Player)
        mock_player4.id = 4
        mock_game.players = [mock_player1,
                             mock_player2, mock_player3, mock_player4]

        mock_session_instance = mock_session.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_game

        turn_assign(mock_game.id)  # DUT
        for player in mock_game.players:
            print(f"Turn: {player.turn_assigned}, id: {player.id}")

        assert mock_session_instance.commit.called

        assigned_turns = [player.turn_assigned for player in mock_game.players]

        self.assertEqual(len(set(assigned_turns)), len(
            assigned_turns), "The turns must be unique")

        for turno in assigned_turns:
            self.assertTrue(1 <= turno <= mock_game.amountPlayers,
                            "The turns must be within the expected range")

        expected_turns = set(range(1, mock_game.amountPlayers + 1))
        self.assertEqual(set(assigned_turns), expected_turns,
                         "All turns must be assigned")

        mock_session_instance.commit.assert_called_once()

        mock_session_instance.close.assert_called_once()

    def test_turn_assign_game_not_found(self, mock_session):
        mock_session_instance = mock_session.return_value
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = None

        with self.assertRaises(ValueError, msg="Game not found"):
            turn_assign(1)

        mock_session_instance.rollback.assert_called_once()

        mock_session_instance.close.assert_called_once()

    def test_turn_assign_exception(self, mock_session):
        mock_session_instance = mock_session.return_value
        mock_session_instance.query.side_effect = Exception("Database error")

        with self.assertRaises(Exception, msg="Database error"):
            turn_assign(1)

        mock_session_instance.rollback.assert_called_once()

        mock_session_instance.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
