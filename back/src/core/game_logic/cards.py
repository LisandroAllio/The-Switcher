from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from core.game_logic.aux.colorValidator import update_forbidden_color, validate_forbidden_color
from core.messages import send_logs
from models import engine
from models.tables import Player, userFigureCard, userMovementCard, Game, gameToken, Play
from schemas.card import UserFigureCardModel, UserMovementCardsModel
from schemas.board import Color, UserPlaysModel
from .aux.movValidator import is_valid_mov
from .tokens import get_all_board_figures
import random

FIGURE_CARDS_NUMBER = 50

Session = sessionmaker(bind=engine)

# ============================ GETTERS ==================================

# ================== MOVEMENT CARDS ====================
def get_random_movs_cards(player_id: int, cards_to_deal : int):
    session = Session()
    try:
        new_cards = []
        for i in range(cards_to_deal):
            random_mov_type = random.choice(['NO_SKIP_LINE','SKIP_ONE_LINE',
                                            'SHORT_DIAG','LONG_DIAG','NORMAL_L',
                                            'INVERSED_L','SKIP_THREE_LINES'])
            new_card = userMovementCard(mov_type=random_mov_type, user_id=player_id)
            new_cards.append(new_card)
        session.add_all(new_cards)
        session.commit()
    except ValueError as ve:
        session.rollback()
        raise ve
    finally:
        session.close()

def get_player_movement_cards(game_id : int, user_id : int):
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise ValueError("Game not found")
        
        user = session.query(Player).filter_by(id = user_id).first()
        if not user:
            raise ValueError("User not found")

        cards = session.query(userMovementCard).filter_by(user_id = user_id).all()
      
        return [UserMovementCardsModel.get_cards(card) for card in cards]
    finally:
        session.close()


# ================== FIGURE CARDS ====================
def deal_random_cards(user_id: int, cards_to_deal: int):
    session = Session()
    try:
        revealed_cards = random.sample(range(cards_to_deal),3)

        for i in range(cards_to_deal):
            if i in revealed_cards:
                figureCard = userFigureCard(userId=user_id, type=random.choice(
                        ['F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12'
                       ,'F13','F14','F15','F16','F17','F18','FE1','FE2','FE3','FE4','FE5','FE6','FE7']), revealed=True
                       )
            else:
                figureCard = userFigureCard(userId=user_id, type=random.choice(
                            ['F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12'
                        ,'F13','F14','F15','F16','F17','F18','FE1','FE2','FE3','FE4','FE5','FE6','FE7']
                        ))
            session.add(figureCard)
        session.commit()
    finally:
        session.close()

def deal_cards(game_id: int):
    try:
        session = Session()
        players_count = session.query(Player).filter_by(game_id=game_id).count()

        cards_to_deal = int(FIGURE_CARDS_NUMBER / players_count)
        players = session.query(Player).filter_by(game_id=game_id).all()

        if len(players) != players_count:
            raise ValueError("Wrong number of players")

        session.close()
        for player in players:
            if not player.blocked:
                deal_random_cards(player.id, cards_to_deal)
    finally:
        session.close()

def get_random_figure_cards(player_id: int, cards_to_deal : int):
    session = Session()
    try:
        player_figure_not_revealed = session.query(userFigureCard).filter_by(userId=player_id, revealed=False).all()

        if player_figure_not_revealed:
            for i in range(cards_to_deal):
                random_figure = random.choice(player_figure_not_revealed)
                random_figure.revealed = True
                session.commit()
        
    except ValueError as ve:
        session.rollback()
        raise ve
    finally:
        session.close()

def get_user_figure_cards(user_id: int):
    session = Session()
    try:
        user_cards_count = session.query(userFigureCard).filter_by(userId=user_id).count()
        user_cards = session.query(userFigureCard).filter_by(userId=user_id, revealed=True).all()
        if user_cards is None:
            raise ValueError("No cards found")
        
        return [UserFigureCardModel.from_db(card) for card in user_cards], user_cards_count
    finally:
        session.close()


# ================== PARTIAL MOVES ====================
def get_user_plays(user_id: int):
    session = Session()
    try:
        player = session.query(Player).filter_by(id=user_id).first()
        if player is None:
            raise ValueError("No user found")
        
        return [UserPlaysModel.from_db(play) for play in player.plays]
    finally:
        session.close()


# =============================== PLAY CARDS ===================================

def play_movement_card (player_id: int, card_id: int, token_1_id: int, token_2_id: int):
    session = Session()
    try:
        player = session.query(Player).filter_by(id = player_id).first()
        card = session.query(userMovementCard).filter_by(id = card_id).first()
        token1 = session.query(gameToken).filter_by(id = token_1_id).first()
        token2 = session.query(gameToken).filter_by(id = token_2_id).first()

        if is_valid_mov(card.mov_type, 
                        (token1.x_coordinate, token1.y_coordinate), 
                        (token2.x_coordinate, token2.y_coordinate)):
            
            print(f"Validating move: {card.mov_type}, {token1}, {token2}")

                 
            temp_x = token1.x_coordinate
            temp_y = token1.y_coordinate

            token1.x_coordinate = token2.x_coordinate
            token1.y_coordinate = token2.y_coordinate

            token2.x_coordinate = temp_x
            token2.y_coordinate = temp_y

            play = Play(user_movement_card=card, game_token_1=token1, 
                        game_token_2=token2, players = player)
            
            session.add(play)

            player.user_movement_cards.remove(card)
            session.commit()

            send_logs(player.game_id, f"{player.name} ha jugado una carta movimiento")

        else:
            raise ValueError("Invalid movement")
    finally:
        session.close()

def play_figure_card (game_id: int, player_id: int, card_id: int, token_id: int):
    session = Session()
    try:
        figures_in_board = get_all_board_figures(game_id)
        card = get_card(card_id, session)

        if card.blocked:
            raise ValueError("Card is blocked")

        for figure in figures_in_board:
            figure_id = figure['figure']['id']
            token_ids = [token['id'] for token in figure['tokens'][0]]

            if figure_id == card_id and token_id in (token_ids):
                if not validate_forbidden_color(game_id, token_id, session):
                    raise ValueError("Figure has Forbidden Color")
                
                if  card.userId == player_id:      
                    #play own figure card   
                    player = get_player(card.userId, session)                                   
                    session.delete(card)
                    session.commit()

                    send_logs(game_id, f"{player.name} ha jugado una carta figura propia")

                    #unlock player or card
                    if cards_revelead_count(player_id, session) == 0:
                        unlock_player(player_id, session) 
                        send_logs(game_id, f"{player.name} se ha desbloqueado")

                    elif cards_revelead_count(player_id, session) == 1:
                        unlock_figured_card(player_id, session)
                        send_logs(game_id, f"{player.name} ha desbloqueado su carta")

                else: 
                    #block rival's figure card
                    player_rival = get_player(card.userId, session)
                    if cards_revelead_count(player_rival.id, session) == 1 or player_rival.blocked: 
                        raise ValueError("Player cannot be blocked")
                    
                    card.blocked = True
                    player_rival.blocked = True
                    session.commit()
                    
                    send_logs(game_id, f"{card.user.name} ha bloquead una carta figura de {player_rival.name}")

                update_forbidden_color(game_id, token_id, session)
                update_played_mov_cards(player_id, session)

                session.close()
                return True
            
        #If nothing is found, then the card figure is invalid   
        raise ValueError("Invalid Figure")
    finally:
        session.close()

def revert_last_play(player_id: int):
    session = Session()
    try:
        last_play = session.query(Play).filter_by(player_id=player_id).order_by(desc(Play.id)).first()
        if not last_play:
            raise ValueError("No play to revert")
        
        # Obtener datos de carta de movimiento y fichas movidas
        movement_card_id = last_play.user_movement_card_id

        ptoken1_id = last_play.game_token_1_id
        ptoken1_x_coordinate = last_play.game_token_1.x_coordinate
        ptoken1_y_coordinate = last_play.game_token_1.y_coordinate

        ptoken2_id = last_play.game_token_2_id
        ptoken2_x_coordinate = last_play.game_token_2.x_coordinate
        ptoken2_y_coordinate = last_play.game_token_2.y_coordinate

        # Intercambiar las posiciones de las fichas
        token1 = session.query(gameToken).filter_by(id=ptoken1_id).first()
        token2 = session.query(gameToken).filter_by(id=ptoken2_id).first()

        if token1:
            token1.x_coordinate = ptoken2_x_coordinate
            token1.y_coordinate = ptoken2_y_coordinate
        else:
            raise ValueError("Token not found")
        if token2:
            token2.x_coordinate = ptoken1_x_coordinate
            token2.y_coordinate = ptoken1_y_coordinate
        else:
            raise ValueError("Token not found")

        # Devolver la carta de movimiento al jugador
        player = session.query(Player).filter_by(id=player_id).first() 
        movement_card = session.query(userMovementCard).filter_by(id=movement_card_id).first()

        movement_card.user_id = player_id
        movement_card.user = player

        session.delete(last_play)
        session.commit()

        send_logs(player.game_id, f"{player.name} ha revertido una carta movimiento")

    except Exception as e:
        session.rollback()
        raise e
    
    finally:
        session.close()

# =============================== PLAY CARDS AUX ===================================
def update_played_mov_cards(player_id: int,  session):
    player = session.query(Player).filter_by(id = player_id).first()
    if not player:
        raise ValueError("Player not found")
    
    for played_card in player.plays:
        session.delete(played_card)

    session.commit()

def cards_revelead_count(player_id: int, session):
    cards = session.query(userFigureCard).filter_by(userId = player_id, revealed=True).all()
    return len(cards)

def get_player(player_id: int, session):
    player = session.query(Player).filter_by(id = player_id).first()
    if not player:
        raise ValueError("Player not found")
    return player

def get_card(card_id: int, session):
    card = session.query(userFigureCard).filter_by(id = card_id).first()
    if not card:
        raise ValueError("Figure Card not found")
    return card

def unlock_figured_card(player_id: int, session):
    card = session.query(userFigureCard).filter_by(userId = player_id, revealed=True).first()
    card.blocked = False

def unlock_player(player_id: int, session):
    player = get_player(player_id, session)
    player.blocked = False