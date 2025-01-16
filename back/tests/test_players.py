# Para testear la persistencia real y como interactúan los modelos en la BD
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.tables import Base, Game, Player, userMovementCard, gameToken, Play

class TestDatabaseIntegration(unittest.TestCase):

    def setUp(self):
        # Crear una base de datos en memoria
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        # Cerrar la sesión y eliminar todas las tablas
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_player_persistence(self):
        # Crear un juego y jugadores reales en la base de datos
        game = Game(name='Test Game', maxPlayers=4, minPlayers=2)

        player1 = Player(name='Player1', is_host=True, turn_assigned=1, game=game,  session_id = 1)
        player2 = Player(name='Player2', is_host=True, turn_assigned=2, game=game,  session_id = 2)


        # Agregar a la sesión real
        self.session.add(game)
        self.session.add(player1)
        self.session.add(player2)
        self.session.commit()

        # Verificar que los jugadores están en la base de datos
        players_in_db = self.session.query(Player).all()

        # Imprimir los resultados
        print("Jugadores guardados en la base de datos:")
        for player in players_in_db:
            print(f"ID: {player.id}, Nombre: {player.name}, Turno: {player.turn_assigned}, Es Host: {player.is_host}")

        # Verificaciones
        self.assertEqual(len(players_in_db), 2)
        self.assertEqual(len(game.players), 2)
        self.assertEqual(players_in_db[0].name, 'Player1')
        self.assertEqual(players_in_db[1].turn_assigned, 2)

    def test_plays_persistence(self):
        # Crear un juego y jugadores reales en la base de datos
        game = Game(name='Test Game', maxPlayers=4, minPlayers=2)
        player = Player(name='Player1', is_host=True, turn_assigned=1, game=game, session_id = 1)
        card = userMovementCard(mov_type="NO_SKIP_LINE", user_id = player.id)
        token_1 = gameToken(color='RED', x_coordinate=1, y_coordinate=1 ,game_id=game.id)
        token_2 = gameToken(color='BLUE', x_coordinate=2, y_coordinate=2 ,game_id=game.id)

        play = Play(user_movement_card=card, game_token_1=token_1, game_token_2=token_2, players = player)

        # Agregar a la sesión real
        self.session.add(game)
        self.session.add(player)
        self.session.add(card)
        self.session.add(token_1)
        self.session.add(token_2)
        self.session.add(play)

        self.session.commit()

        # Verificar que los jugadores están en la base de datos
        
        players_in_db = self.session.query(Player).first()
        print(f"ID: {players_in_db.id}, Nombre: {players_in_db.name}, Turno: {players_in_db.turn_assigned}, Es Host: {players_in_db.is_host}")

        print(f"Jugadas del jugador {players_in_db.name}:")
        
        for play in players_in_db.plays:
            print(f"Carta: {play.user_movement_card.mov_type}, ficha 1 : {play.game_token_1.color}, ficha 2 : {play.game_token_2.color}")

if __name__ == '__main__':
    unittest.main()
