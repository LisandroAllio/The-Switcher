from models.tables import Game, gameToken


def validate_forbidden_color(game_id: int, token_id: int, session):
    game = session.query(Game).filter_by(id = game_id).first()
    if not game:
        raise ValueError("Game not found")
    
    token = session.query(gameToken).filter_by(id = token_id).first()
    if not token:
        raise ValueError("Token not found")
    
    return game.forbiddenColor != token.color


def update_forbidden_color(game_id: int, token_id: int, session):
    game = session.query(Game).filter_by(id = game_id).first()
    if not game:
        raise ValueError("Game not found")
    
    token = session.query(gameToken).filter_by(id = token_id).first()
    if not token:
        raise ValueError("Token not found")
    game.forbiddenColor = token.color
    session.commit()