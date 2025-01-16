from models.tables import Game, Player
from sqlalchemy.orm import sessionmaker
from models import engine


Session = sessionmaker(bind=engine)


def game_winnable_for_leave(game_id : int):
    session = Session()
    try:
        game = session.query(Game).filter_by(id = game_id).first()

        if not game:
            raise ValueError("Game not found")

        return (game.inGame and (len(game.players)==1))

    finally:
        session.close()


def get_winner(game_id : int):
    session = Session()
    try:
        if game_winnable_for_leave(game_id):
            user = session.query(Player).filter_by(game_id = game_id).first()
            return user
        else:
            return None

    finally:
        session.close()

