# Este archivo contiene la lógica para asignar los turnos de los jugadores
from sqlalchemy.orm import sessionmaker
from models import engine
from models.tables import Game
import random

# PRE:{ game.amountPlayers == len(game.players) }
# Crea una sesión
Session = sessionmaker(bind=engine)


def turn_assign(game_id: int):
    session = Session()

    try:
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise ValueError("Game not found")

        # Turnos disponibles
        available_turns = [i for i in range(1, game.amountPlayers + 1)]

        for player in game.players:
            player.turn_assigned = available_turns.pop(random.randint(
                0, len(available_turns) - 1))  # Asignar un turno aleatorio

        session.commit()
    except Exception as e:
        session.rollback()  # Deshacer cambios
        raise e
    finally:
        session.close()
