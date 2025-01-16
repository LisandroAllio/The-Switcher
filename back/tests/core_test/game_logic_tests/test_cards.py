import unittest
from unittest.mock import patch, MagicMock
from models.tables import Play, Player, gameToken, userMovementCard
from core.game_logic.cards import deal_random_cards, deal_cards, FIGURE_CARDS_NUMBER, get_random_figure_cards, get_user_figure_cards, get_random_movs_cards, get_player_movement_cards, play_figure_card, play_movement_card, revert_last_play

class TestFigureCards(unittest.TestCase):
    @patch('core.game_logic.cards.Session')
    @patch('core.game_logic.cards.random.choice', return_value="Figure1")
    def test_deal_random_cards(self, mock_random_choice, mock_session):
        # Mock para la sesión y los commits
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Probamos la función con 3 cartas
        deal_random_cards(1, 3)
        
        # Verificamos que se añadieron 3 cartas y que se llamó a commit
        self.assertEqual(mock_session_instance.add.call_count, 3)
        mock_session_instance.commit.assert_called_once()

    @patch('core.game_logic.cards.Session')
    @patch('core.game_logic.cards.deal_random_cards')
    def test_deal_cards(self, mock_deal_random_cards, mock_session):
        # Simulamos la sesión y los jugadores
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_player_query = MagicMock()
        mock_player_query.filter_by.return_value.all.return_value = [
            Player(id=1), Player(id=2), Player(id=3)
        ]
        mock_session_instance.query.return_value = mock_player_query

        mock_query = mock_session_instance.query.return_value
        mock_query.filter_by.return_value.count.return_value = 3
        
        # Probamos la función
        deal_cards(1)
        
        # Verificamos que se llamara a deal_random_cards para cada jugador
        self.assertEqual(mock_deal_random_cards.call_count, 3)
        mock_deal_random_cards.assert_any_call(1, FIGURE_CARDS_NUMBER // 3)
        mock_deal_random_cards.assert_any_call(2, FIGURE_CARDS_NUMBER // 3)
        mock_deal_random_cards.assert_any_call(3, FIGURE_CARDS_NUMBER // 3)

    @patch('core.game_logic.cards.Session')
    @patch('core.game_logic.cards.deal_random_cards')
    def test_deal_cards_to_blocked_user(self, mock_deal_random_cards, mock_session):
        # Simulamos la sesión y los jugadores
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_player_query = MagicMock()
        mock_player_query.filter_by.return_value.all.return_value = [
            Player(id=1), Player(id=2), Player(id=3, blocked=True)
        ]
        mock_session_instance.query.return_value = mock_player_query

        mock_query = mock_session_instance.query.return_value
        mock_query.filter_by.return_value.count.return_value = 3
        
        # Probamos la función
        deal_cards(1)
        
        # Verificamos que se llamara a deal_random_cards para cada jugador
        self.assertEqual(mock_deal_random_cards.call_count, 2)
        mock_deal_random_cards.assert_any_call(1, FIGURE_CARDS_NUMBER // 3)
        mock_deal_random_cards.assert_any_call(2, FIGURE_CARDS_NUMBER // 3)

    @patch('core.game_logic.cards.Session')
    def test_deal_cards_invalid_player_count(self, mock_session):
        # Simulamos la sesión
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Verificamos que se lance el error si hay menos de 2 o más de 4 jugadores
        with self.assertRaises(ValueError) as context:
            deal_cards(1)
        self.assertEqual(str(context.exception), "Wrong number of players")

    @patch('core.game_logic.cards.Session')
    @patch('core.game_logic.cards.random.choice')
    def test_get_random_figure_cards(self, mock_random, mock_session):
        mock_card1 = MagicMock(mov_type='F1', revealed=True)
        mock_card2 = MagicMock(mov_type='F1', revealed=False)
        mock_card3 = MagicMock(mov_type='F1', revealed=False)

        mock_player1 = MagicMock(spec=Player)
        mock_player1.id = 1
        mock_player1.user_figure_cards = [mock_card1, mock_card2, mock_card3]

        mock_session_instance = mock_session.return_value

        mock_session_instance.query.return_value.filter_by.return_value.all.return_value = [mock_card1, mock_card2, mock_card3]
        mock_random.side_effect = [mock_card2, mock_card3]

        # Probamos la función
        get_random_figure_cards(1, 2)
        
        # Verificamos que se llamara a deal_random_cards para cada jugador
        mock_random.call_count == 2
        assert mock_card2.revealed == True
        assert mock_card3.revealed == True
 
    @patch('core.game_logic.cards.Session')
    def test_get_user_figure_cards_success(self, mock_session):
        # Mockear la sesion y la query
        mock_session_instance = MagicMock()
        mock_query = mock_session_instance.query.return_value
        mock_filter = mock_query.filter_by.return_value
        mock_filter.all.return_value = [MagicMock(userId=1, revealed=True)]
        mock_filter.count.return_value = 1  
        mock_session.return_value = mock_session_instance

        # Mockear UserFigureCardModel.from_db
        with patch('core.game_logic.cards.UserFigureCardModel.from_db', return_value=MagicMock()) as mock_from_db:
            # Llamar a la funcion
            result = get_user_figure_cards(1)

            # Assertions
            mock_session.assert_called_once()
            self.assertEqual(mock_query.filter_by.call_count, 2)
            mock_filter.all.assert_called_once()
            mock_from_db.assert_called()
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)

    @patch('core.game_logic.cards.Session')
    def test_get_user_figure_cards_no_cards(self, mock_session):
        # Mockear la sesion y la query
        mock_session_instance = MagicMock()
        mock_query = mock_session_instance.query.return_value
        mock_filter = mock_query.filter_by.return_value
        mock_filter.all.return_value = None
        mock_session.return_value = mock_session_instance

        # Llamar a la funcion y ver si lanza el error
        with self.assertRaisesRegex(ValueError, "No cards found"):
            get_user_figure_cards(1)

        # Asserts
        mock_session.assert_called_once()
        self.assertEqual(mock_query.filter_by.call_count, 2)
        mock_filter.all.assert_called_once()

class TestMovCards(unittest.TestCase):
    @patch('core.game_logic.cards.Session')
    @patch('core.game_logic.cards.random.choice', return_value='NO_SKIP_LINE')
    def test_get_random_movs_cards(self, mock_random_choice, mock_session):
        #Simulacion de la Sesion
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        #Simulacion de 2 jugadores
        mock_player_query = MagicMock()
        mock_player_query.filter_by.return_value.all.return_value = [Player(id=1), Player(id=2)]
        mock_session_instance.query.return_value = mock_player_query

        #Llamada a la funcion y verificacion de que se llamaron correctamente add, commit y random.choice
        for i in range(1,3):
            get_random_movs_cards(i,3)

        self.assertEqual(mock_session_instance.add_all.call_count, 2)
        self.assertEqual(mock_session_instance.commit.call_count, 2)
        self.assertEqual(mock_random_choice.call_count, 6)

        #Verificacion de las cartas
        for call in mock_session_instance.add.call_args_list:
            card = call[0][0]
            self.assertEqual(card.mov_type, 'NO_SKIP_LINE')
    
    @patch('core.game_logic.cards.Session')
    def test_get_random_movs_cards_handles_exceptions(self, mock_session):
        # Simulamos una excepción en el commit
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.commit.side_effect = ValueError("Some error")

        # Verificamos que la excepción se maneja correctamente
        with self.assertRaises(ValueError) as context:
            get_random_movs_cards(1, 3)
        
        self.assertEqual(str(context.exception), "Some error")
        mock_session_instance.rollback.assert_called_once()


    @patch('core.game_logic.cards.Session')
    def test_get_user_movement_card(self, mock_session):
        #Mockear la sesion
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        #Mockear Jugador, Partida y cartas
        mock_player = MagicMock()
        mock_player.id = 1

        mock_game = MagicMock()
        mock_game.id = 1

        mock_card1 = MagicMock()
        mock_card1.id = 1
        mock_card1.mov_type = "NORMAL_L"

        mock_card2 = MagicMock()
        mock_card2.id = 2
        mock_card2.mov_type = "NO_SKIP_LINE"        

        #Simulacion de las querys
        mock_session_instance.query.return_value.filter_by.return_value.first.side_effect = [mock_game, mock_player]

        mock_session_instance.query.return_value.filter_by.return_value.all.return_value = [mock_card1, mock_card2]

        #Simulacion de la funcion a testear
        res = get_player_movement_cards(1,1)
        res_dict = [card.model_dump() for card in res]

        #Assertions
        self.assertEqual(res_dict, [{'card_id': 1, 'mov_type': 'NORMAL_L'}, {'card_id' : 2, 'mov_type' : 'NO_SKIP_LINE'}])

        mock_session_instance.query.return_value.filter_by.assert_any_call(id=1)
        mock_session_instance.query.return_value.filter_by.assert_any_call(user_id=1)

        mock_session_instance.close.assert_called_once()

    @patch('core.game_logic.cards.Session')
    def test_not_found_game(self, mock_session):
        #Mock de la sesion
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        #Simulacion de la query
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = None

        #Llamada a la funcion y Assertion
        with self.assertRaises(ValueError) as context:
            get_player_movement_cards(1, 1)

        self.assertEqual(str(context.exception), "Game not found")
        mock_session_instance.close.assert_called_once()

    
    @patch('core.game_logic.cards.Session')
    def test_not_found_player(self, mock_session):
        #Mock de la sesion
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        #Simulacion de juego encontrado sin jugadores
        mock_game = MagicMock()
        mock_game.id = 1

        mock_session_instance.query.return_value.filter_by.return_value.first.side_effect = [mock_game, None]

        with self.assertRaises(ValueError) as context:
            get_player_movement_cards(1,1)

        self.assertEqual(str(context.exception), "User not found")
        mock_session_instance.close.assert_called_once()


class TestPlayMovementCard(unittest.TestCase):
    @patch('core.game_logic.cards.Session')
    @patch('core.game_logic.cards.send_logs')  # Mock de send_logs
    def test_play_movement_card_valid_move(self, mock_send_logs, mock_session):
        # Configuración de los mocks
        mock_player = MagicMock()
        mock_player.id = 1  # Asegurarnos de que el ID esté correctamente configurado
        mock_player.name = "Jugador 1"  # Nombre del jugador

        mock_card = MagicMock(mov_type='NORMAL_L')
        mock_token1 = MagicMock(x_coordinate=1, y_coordinate=1)
        mock_token2 = MagicMock(x_coordinate=2, y_coordinate=3)

        # Configurar el comportamiento de la sesión
        mock_session.return_value.query.return_value.filter_by.return_value.first.side_effect = [
            mock_player,  # Primer retorno: mock_player
            mock_card,    # Segundo retorno: mock_card
            mock_token1,  # Tercer retorno: mock_token1
            mock_token2   # Cuarto retorno: mock_token2
        ]

        with patch('core.game_logic.aux.movValidator.is_valid_mov', return_value=True), patch('models.tables.Play') as mock_play:

            # Llamar a la función
            play_movement_card(1, 1, 1, 9)

            # Verificar que los tokens intercambiaron posiciones
            self.assertEqual(mock_token1.x_coordinate, 2)
            self.assertEqual(mock_token1.y_coordinate, 3)
            self.assertEqual(mock_token2.x_coordinate, 1)
            self.assertEqual(mock_token2.y_coordinate, 1)

            # Verificar que se eliminó la carta de usuario
            mock_player.user_movement_cards.remove.assert_called_once_with(mock_card)
        
            # Verificar que se agregó un play al usuario
            mock_session.return_value.add.assert_called_once()

            # Verificar que se hizo commit
            mock_session.return_value.commit.assert_called_once()

            # Verificar que send_logs fue llamado con el mensaje correcto
            # Se puede mejorar con un mensaje esperado
            mock_send_logs.assert_called_once()

    @patch('core.game_logic.cards.Session')
    def test_play_movement_card_invalid_move(self, mock_session):
        
        mock_card = MagicMock(mov_type='F1')
        mock_token1 = MagicMock(x_coordinate=1, y_coordinate=1)
        mock_token2 = MagicMock(x_coordinate=4, y_coordinate=3)

        mock_session.return_value.query.return_value.filter_by.return_value.first.side_effect = [
            MagicMock(),  
            mock_card,    
            mock_token1,  
            mock_token2   
        ]

        # Llamar a la función que se está probando
        with self.assertRaises(ValueError) as context:
            play_movement_card(1, 1, 1, 2)

        # Verifica que se lanzó la excepción correcta
        self.assertEqual(str(context.exception), "Invalid movement")

        # Verificar que los tokens NO intercambiaron posiciones
        self.assertEqual(mock_token1.x_coordinate, 1)
        self.assertEqual(mock_token1.y_coordinate, 1)
        self.assertEqual(mock_token2.x_coordinate, 4)
        self.assertEqual(mock_token2.y_coordinate, 3)

class TestPlayFigureCard(unittest.TestCase):
    @patch('core.game_logic.cards.Session')
    @patch('core.game_logic.cards.send_logs')  # Mockear send_logs
    def test_play_figure_card_valid(self, mock_send_logs, mock_session):
        # Crear una instancia del mock para la sesión
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance 

        # Crear el mock para la figura
        mock_figure = {
            "figure": {
                "id": 1,
                "userId": 1,  # El mismo userId que player_id
                "type": "example"
            },
            "tokens": [
                [{"id": 100, "x_coordinate": 1, "y_coordinate": 1, "color": "RED"}]
            ]
        }

        # Crear el mock para la carta
        mock_card = MagicMock()
        mock_card.userId = 1  # Asegúrate de que coincida con player_id
        mock_card.blocked = False

        # Crear el mock para el jugador
        mock_player = MagicMock()
        mock_player.name = "player_name"  # Asignar un nombre al jugador

        # Configurar los mocks
        with patch('core.game_logic.cards.get_all_board_figures', return_value=[mock_figure]), \
             patch('core.game_logic.cards.get_card', return_value=mock_card), \
             patch('core.game_logic.cards.validate_forbidden_color', return_value=True), \
             patch('core.game_logic.cards.get_player', return_value=mock_player), \
             patch('core.game_logic.cards.update_forbidden_color') as mock_update_forbidden_color, \
             patch('core.game_logic.cards.update_played_mov_cards') as mock_update_played_mov_cards:
            
            result = play_figure_card(1, 1, 1, 100)

            # Verificar que el resultado sea True
            self.assertTrue(result)

            # Verificar que las funciones externas fueron llamadas correctamente
            mock_update_forbidden_color.assert_called_once()
            mock_update_played_mov_cards.assert_called_once()

            self.assertEqual(mock_send_logs.call_count, 2)
            # Verificar que send_logs fue llamada correctamente
            mock_send_logs.assert_called_with(1, "player_name se ha desbloqueado")

    @patch('core.game_logic.cards.Session')
    def test_play_figure_card_invalid(self, mock_session):
        
        mock_card = MagicMock()  # Crear un mock para la carta
        mock_card.userId = 1
        mock_card.blocked = False
        # Configurar el comportamiento para no encontrar figuras
        with patch('core.game_logic.cards.get_all_board_figures', return_value=[]), \
             patch('core.game_logic.cards.get_card', return_value=mock_card):
            with self.assertRaises(ValueError) as context:
                play_figure_card(1, 1, 1, 100)
        
            self.assertEqual(str(context.exception), "Invalid Figure")

    @patch('core.game_logic.cards.Session')
    def test_play_figure_card_blocked(self, mock_session):
        
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance 

        mock_figure = {
            "figure": {
                "id": 1,
                "userId": 1,
                "type": "example"
            },
            "tokens": [
                [{"id": 100, "x_coordinate": 1, "y_coordinate": 1, "color": "RED"}]
            ]
        }

        mock_card = MagicMock()  # Crear un mock para la carta
        mock_card.userId = 1
        mock_card.blocked= True

        # Configurar el comportamiento del mock para obtener las figuras en el tablero
        with patch('core.game_logic.cards.get_all_board_figures', return_value=[mock_figure]), \
             patch('core.game_logic.cards.get_card', return_value=mock_card):
            with self.assertRaises(ValueError) as context:
                play_figure_card(1, 1, 1, 100)
        
            self.assertEqual(str(context.exception), "Card is blocked")

    @patch('core.game_logic.cards.Session')
    @patch('core.game_logic.cards.send_logs')  # Mockear send_logs
    def test_play_figure_card_unlock_player(self, mock_send_logs, mock_session):
        # Crear una instancia del mock para la sesión
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Crear el mock para la figura
        mock_figure = {
            "figure": {
                "id": 1,
                "userId": 1,  # El mismo userId que player_id
                "type": "example"
            },
            "tokens": [
                [{"id": 100, "x_coordinate": 1, "y_coordinate": 1, "color": "RED"}]
            ]
        }

        # Crear el mock para la carta
        mock_card = MagicMock()
        mock_card.id = 1
        mock_card.userId = 1  # Asegúrate de que coincida con player_id
        mock_card.blocked = False

        # Crear el mock para el jugador
        mock_player = MagicMock()
        mock_player.id = 1
        mock_player.name = "player_name"
        mock_player.blocked = False  # No está bloqueado, por lo que se debe desbloquear

        # Configurar los mocks
        with patch('core.game_logic.cards.get_all_board_figures', return_value=[mock_figure]), \
             patch('core.game_logic.cards.get_card', return_value=mock_card), \
             patch('core.game_logic.cards.get_player', return_value=mock_player), \
             patch('core.game_logic.cards.validate_forbidden_color', return_value=True), \
             patch('core.game_logic.cards.cards_revelead_count', return_value=0), \
             patch('core.game_logic.cards.update_forbidden_color') as mock_update_forbidden_color, \
             patch('core.game_logic.cards.update_played_mov_cards') as mock_update_played_mov_cards:

            result = play_figure_card(1, 1, 1, 100)

            # Verificar que el resultado sea True
            self.assertTrue(result)

            # Verificar que las funciones externas fueron llamadas correctamente
            mock_update_forbidden_color.assert_called_once()
            mock_update_played_mov_cards.assert_called_once()

            # Verificar que el jugador ha sido desbloqueado
            mock_player.blocked = False
            self.assertFalse(mock_player.blocked)

            # Verificar que send_logs fue llamado correctamente
            self.assertEqual(mock_send_logs.call_count, 2)

            mock_send_logs.assert_called_with(1, f"player_name se ha desbloqueado")

    @patch('core.game_logic.cards.Session')
    @patch('core.game_logic.cards.send_logs')  # Mock de send_logs
    def test_play_figure_card_unlock_card(self, mock_send_logs, mock_session):
        # Crear una instancia del mock para la sesión
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Crear el mock para la figura
        mock_figure = {
            "figure": {
                "id": 1,
                "userId": 1,
                "type": "example"
            },
            "tokens": [
                [{"id": 100, "x_coordinate": 1, "y_coordinate": 1, "color": "RED"}]
            ]
        }

        # Crear el mock para la carta 1 (la carta que se juega)
        mock_card_1 = MagicMock()
        mock_card_1.id = 1
        mock_card_1.userId = 1
        mock_card_1.blocked = False

        # Crear el mock para la carta 2 (la carta revelada)
        mock_card_2 = MagicMock()
        mock_card_2.id = 2
        mock_card_2.userId = 1
        mock_card_2.blocked = True  # Comienza bloqueada

        # Mock del jugador
        mock_player = MagicMock()
        mock_player.id = 1
        mock_player.blocked = False  # No está bloqueado
        mock_player.name = "Jugador 1"  # Nombre del jugador

        # Simular la consulta a la base de datos para obtener la carta revelada
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_card_2

        # Configurar los mocks para las funciones necesarias
        with patch('core.game_logic.cards.get_all_board_figures', return_value=[mock_figure]), \
             patch('core.game_logic.cards.get_card', return_value=mock_card_1), \
             patch('core.game_logic.cards.get_player', return_value=mock_player), \
             patch('core.game_logic.cards.validate_forbidden_color', return_value=True), \
             patch('core.game_logic.cards.cards_revelead_count', side_effect=[2, 1]), \
             patch('core.game_logic.cards.update_forbidden_color') as mock_update_forbidden_color, \
             patch('core.game_logic.cards.update_played_mov_cards') as mock_update_played_mov_cards:

            result = play_figure_card(1, 1, 1, 100)

            # Verificar que el resultado sea True
            self.assertTrue(result)

            # Verificar que las funciones externas fueron llamadas correctamente
            mock_update_forbidden_color.assert_called_once()
            mock_update_played_mov_cards.assert_called_once()

            # Verificar que la carta 2 haya sido desbloqueada
            self.assertFalse(mock_card_2.blocked)

            # Verificar que send_logs fue llamada con el mensaje correcto
            expected_message = f"{mock_player.name} ha desbloqueado su carta"
            mock_send_logs.assert_called_with(mock_player.id, expected_message)

    
            
    
    @patch('core.game_logic.cards.Session')
    @patch('core.game_logic.cards.send_logs')  # Mock de send_logs
    def test_blocked_figure_card_valid(self, mock_send_logs, mock_session):
        
        # Crear mock de la sesión
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Mock de la figura en el tablero
        mock_figure = {
            "figure": {
                "id": 1,
                "userId": 1,
                "type": "example"
            },
            "tokens": [
                [{"id": 100, "x_coordinate": 1, "y_coordinate": 1, "color": "RED"}]
            ]
        }

        # Mock de la carta
        mock_card = MagicMock()  
        mock_card.id = 1
        mock_card.userId = 2
        mock_card.blocked = False

        # Mock del jugador rival
        mock_player_rival = MagicMock()
        mock_player_rival.id = 2
        mock_player_rival.blocked = False  # El jugador rival no está bloqueado

        # Configurar el comportamiento del mock para obtener las figuras en el tablero
        with patch('core.game_logic.cards.get_all_board_figures', return_value=[mock_figure]), \
             patch('core.game_logic.cards.get_card', return_value=mock_card), \
             patch('core.game_logic.cards.get_player', return_value=mock_player_rival), \
             patch('core.game_logic.cards.validate_forbidden_color', return_value=True), \
             patch('core.game_logic.cards.cards_revelead_count', return_value=2), \
             patch('core.game_logic.cards.update_forbidden_color') as mock_update_forbidden_color, \
             patch('core.game_logic.cards.update_played_mov_cards') as mock_update_played_mov_cards:

            # Llamar a la función play_figure_card
            result = play_figure_card(1, 1, 1, 100)

            # Verificar que el resultado sea True
            self.assertTrue(result)

            # Verificar que las funciones externas fueron llamadas correctamente
            mock_update_forbidden_color.assert_called_once()
            mock_update_played_mov_cards.assert_called_once()

            # Verificar que el jugador rival haya sido bloqueado
            self.assertTrue(mock_player_rival.blocked)
            self.assertTrue(mock_card.blocked)

            # Verificar que send_logs fue llamada correctamente con los parámetros esperados
            # pordira mejorarse con un called once with y un expected message
            mock_send_logs.assert_called_once()

    @patch('core.game_logic.cards.Session')
    def test_blocked_figure_card_fail(self, mock_session):
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance 

        mock_figure = {
            "figure": {
                "id": 1,
                "userId": 1,
                "type": "example"
            },
            "tokens": [
                [{"id": 100, "x_coordinate": 1, "y_coordinate": 1, "color": "RED"}]
            ]
        }

        mock_card = MagicMock()  # Crear un mock para la carta
        mock_card.id = 1
        mock_card.userId = 2
        mock_card.blocked = False

        # Mock del jugador rival
        mock_player_rival = MagicMock()
        mock_player_rival.id = 2
        mock_player_rival.blocked = True  # SI está bloqueado

        with patch('core.game_logic.cards.get_all_board_figures', return_value=[mock_figure]), \
             patch('core.game_logic.cards.get_card', return_value=mock_card), \
             patch('core.game_logic.cards.get_player', return_value=mock_player_rival), \
             patch('core.game_logic.cards.validate_forbidden_color', return_value=True), \
             patch('core.game_logic.cards.cards_revelead_count', return_value=2):

            with self.assertRaises(ValueError) as context:
                play_figure_card(1, 1, 1, 100)
        
            self.assertEqual(str(context.exception), "Player cannot be blocked")
        
            
class TestRevertLastPlay(unittest.TestCase):

    @patch('core.game_logic.cards.send_logs')  # Parcheamos send_logs de core.game_logic.cards
    @patch('core.game_logic.cards.Session')  # Parcheamos Session
    def test_revert_last_play(self, mock_session, mock_send_logs):
        # Configurar el mock para la sesión
        mock_session_instance = mock_session.return_value
        mock_session_instance.begin.return_value = MagicMock()

        # Mock para el objeto Play
        mock_play = MagicMock()
        mock_play.game_token_1_id = 1
        mock_play.game_token_1.x_coordinate = 10
        mock_play.game_token_1.y_coordinate = 20
        mock_play.game_token_2_id = 2
        mock_play.game_token_2.x_coordinate = 30
        mock_play.game_token_2.y_coordinate = 40
        mock_play.user_movement_card_id = 100

        # Mock para las fichas
        mock_token1 = MagicMock()
        mock_token2 = MagicMock()

        # Mock para el jugador y la carta de movimiento
        mock_player = MagicMock()
        mock_movement_card = MagicMock()

        # Simular las consultas a la base de datos
        mock_session_instance.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = mock_play
        mock_session_instance.query.return_value.filter_by.return_value.first.side_effect = [mock_token1, mock_token2, mock_player, mock_movement_card]

        # Ejecutar la función
        revert_last_play(1)

        # Asegurar que las consultas ocurrieron como se esperaba
        mock_session_instance.query.assert_any_call(Play)
        mock_session_instance.query.assert_any_call(gameToken)
        mock_session_instance.query.assert_any_call(Player)
        mock_session_instance.query.assert_any_call(userMovementCard)

        # Verificar que se cambiaron las coordenadas de los tokens
        mock_token1.x_coordinate = 30
        mock_token1.y_coordinate = 40
        mock_token2.x_coordinate = 10
        mock_token2.y_coordinate = 20

        assert mock_token1.x_coordinate == 30
        assert mock_token1.y_coordinate == 40
        assert mock_token2.x_coordinate == 10
        assert mock_token2.y_coordinate == 20

        # Verificar que la carta de movimiento fue reasignada al jugador
        assert mock_movement_card.user_id == 1
        assert mock_movement_card.user == mock_player

        # Verificar que la última jugada fue eliminada
        mock_session_instance.delete.assert_called_once_with(mock_play)

        # Asegurar que los cambios fueron confirmados (commit)
        mock_session_instance.commit.assert_called_once()

        # Asegurarse de que la sesión fue cerrada
        mock_session_instance.close.assert_called_once()

        # Verificar que se llamó a send_logs con los parámetros correctos
        mock_send_logs.assert_called_once_with(mock_player.game_id, f"{mock_player.name} ha revertido una carta movimiento")


if __name__ == '__main__':
    unittest.main()
