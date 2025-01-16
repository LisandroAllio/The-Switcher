import random
from sqlalchemy.orm import sessionmaker
from core.game_logic.aux.figDetector import get_board_figures, get_figures
from models import engine
from models.tables import Game, gameToken
from schemas.board import BoardFigureModel, GameTokenModel, Color

# Crea una sesión
Session = sessionmaker(bind=engine)

def get_game_tokens(game_id: int):
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise ValueError("Game not found")
        
        return [GameTokenModel.from_db(token) for token in game.game_tokens]
    finally:
        session.close()

def initialize_game_tokens(game_id: int):
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise ValueError("Game not found")
        
        colores = [Color["RED"], Color["BLUE"], Color["GREEN"], Color["YELLOW"]] * 9

        # Mezclar la lista de colores aleatoriamente
        random.shuffle(colores)
        
        for i in range(1,7):
            for j in range(1,7):
                index = (i-1)* 6 + (j-1)
                token = gameToken(color = colores[index], x_coordinate=i, y_coordinate=j, game_id=game_id)
                game.game_tokens.append(token)
        session.commit()
    finally:
        session.close()

def get_all_board_figures(game_id: int):
    session = Session()
    try: 
        figure_cards = []
        board = []
        result =  []
        game = session.query(Game).filter_by(id=game_id).first()

        if not game:
            raise ValueError("Game not found")

        for player in game.players:
            for figure_card in player.user_figure_cards:
                if (figure_card.revealed and not figure_card.blocked):
                    figure_cards.append(figure_card)

        for token in game.game_tokens:
            board.append((token.x_coordinate, token.y_coordinate, token.color))
        
        for card in figure_cards:
            figures_found = get_board_figures(card.type, board)
            
            if len(figures_found) > 0:
                tokens = get_figures(game_id, figures_found, session)
                if len(tokens) > 0:
                    result.append(BoardFigureModel.from_db(card, tokens))  
        
        if len(result) == 0:
            raise ValueError('Figures not found')
        return result
    
    finally:
        session.close()