from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import sessionmaker
from models import engine
from models.tables import Game, Player, SessionCounter
from schemas.game import GameListModel,GameTurn
from core.game_logic.cards import deal_cards, get_random_figure_cards, get_random_movs_cards, revert_last_play
from core.game_logic.tokens import initialize_game_tokens
from core.game_logic.turnLogic import turn_assign
from core.game_logic.winLogic import get_winner
from core.messages import send_logs
from schemas.socket import GameStatusTypes, GameMessage

# Crea una sesión
Session = sessionmaker(bind=engine)


def create_game(
    name: str,
    host_name: str,
    session_id : int,
    min_users: int = 4,
    max_users: int = 12,
    pwd: Optional[str] = None,
):
    if min_users < 2 or min_users > 4:
        raise ValueError("Minimum users invalid value")
    if max_users < 2 or max_users > 4:
        raise ValueError("Maximum users invalid value")
    if min_users > max_users:
        raise ValueError("Minimum users must be less than maximum users")

    session = Session()
    try:
        game = Game(name=name, maxPlayers=max_users,
                    minPlayers=min_users, password=pwd)
        host_player = Player(name=host_name, is_host=True, session_id = session_id)
        game.host_id = host_player.id
        game.players.append(host_player)


        session.add(game)
        session.commit()
        session.refresh(game)

        send_logs(game.id, f"{host_player.name} ha creado la partida")

        return game.id
    finally:
        session.close()


def get_games():
    session = Session()
    try:
        games = session.query(Game).filter(
            Game.maxPlayers > Game.amountPlayers, Game.inGame.is_(False)).all()
        return [GameListModel.from_db(game) for game in games]
    finally:
        session.close()


def get_games_by_name(name: str):
    session = Session()
    try:
        games = session.query(Game).filter(
            Game.maxPlayers > Game.amountPlayers, Game.inGame.is_(False), Game.name.like(name + '%')).all()
        return [GameListModel.from_db(game) for game in games]
    finally:
        session.close()

def get_games_by_players(players: int):
    session = Session()
    try:
        games = session.query(Game).filter(
            Game.maxPlayers > Game.amountPlayers, Game.inGame.is_(False), Game.amountPlayers == players).all()
        return [GameListModel.from_db(game) for game in games]
    finally:
        session.close()


def get_game_id(game_id: int):
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            return None
        return GameListModel.from_db(game)
    finally:
        session.close()


def join_game(game_id: int, user_name: str, password : str, session_id : int):
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise ValueError("Game not found")
        elif len(game.players) >= game.maxPlayers:
            raise ValueError("Game is full")
        elif (game.password != None):
            if (password != game.password):
                raise ValueError("Incorrect Password")

        new_player = Player(name=user_name, session_id = session_id)
        game.players.append(new_player)
        game.amountPlayers += 1
        session.commit()

        send_logs(game_id, f"{new_player.name} se ha unido a la partida")

        return GameListModel.from_db(game)
    finally:
        session.close()


def leave_game(game_id: int, user_id: int):
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise ValueError("Game not found")

        if game.amountPlayers > 0:
            game.amountPlayers -= 1
        else:
            raise ValueError("No players in the game")

        user_delete = session.query(Player).filter_by(id=user_id).first()
        if not user_delete:
            raise ValueError("Player not found")
        
        if game.inGame:
            #Reordenar turnos
            for player in game.players:
                if player.turn_assigned > user_delete.turn_assigned:
                    player.turn_assigned -= 1
                    session.commit()

            #Si es el turno del jugador
            if game.TurnoActual == user_delete.turn_assigned:
                #Setear next turn
                next_turn = (game.TurnoActual % game.amountPlayers) + 1
                game.TurnoActual = next_turn 
                session.commit()
        
                #Reverse partial movements
                if len(user_delete.plays) > 0:              
                    for i in range(len(user_delete.plays)):
                        revert_last_play(user_id)
    

        session.delete(user_delete)
        session.commit()
        session.refresh(game)

        send_logs(game_id, f"{user_delete.name} ha abandonado la partida")

        if user_delete.is_host and len(game.players) > 0:
            game.players[0].is_host = True
            session.commit()
            session.refresh(game)

        if user_delete.is_host and not game.inGame:
            return "status_cancel_game" 
        else:
            return "status_winner" if (get_winner(game_id) != None) else "status_leave"

    except ValueError as ve:
        session.rollback()
        raise ve
    finally:
        session.close()


def start_game(game_id: int):
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise ValueError("Game not found")
        elif game.amountPlayers < game.minPlayers:
            raise ValueError("Not enough players")

        game.inGame = True
        game.TurnoActual = 1
        game.Timer = datetime.utcnow()        

        session.commit()

        # Lógica para asignar turnos.
        turn_assign(game_id)
        
        # Lógica para inicializar tablero
        initialize_game_tokens(game_id)

        # Logica para asignar cartas a los jugadores al inicio de la partida.
        deal_cards(game_id)
        
        for player in game.players:
            get_random_movs_cards(player.id, 3)

        session.commit()

        send_logs(game_id, f"Se ha iniciado la partida")

    except ValueError as ve:
        session.rollback()
        raise ve
    finally:
        session.close()

def end_game(game_id: int, session=None):
    if session is None:
        session = Session()  
    try:
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise ValueError("Game not found")

        for player in game.players:
            session.delete(player)
        
        session.delete(game)
        session.commit()

        return game.id

    except ValueError as ve:
        session.rollback()
        raise ve
    finally:
        session.close()

def create_game_message(type: GameStatusTypes, game_id: int, user_id=None):
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise ValueError("Game not found")
        return GameMessage.create(type, game, user_id)
    finally:
        session.close()

def get_game_turn(game_id: int) -> GameTurn:
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            raise ValueError("Game not found")
        if game.amountPlayers < game.minPlayers:
            raise ValueError("Not enough players")
        game_turn = GameTurn.from_db(game)
        return game_turn
    except ValueError as ve:
        session.rollback()
        raise ve
    finally:
        session.close()

def end_turn(game_id: int, player_id: int): 
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()
        player = session.query(Player).filter_by(id=player_id).first()

        if not game:
            raise ValueError("Game not found")
        
        next_turn = (game.TurnoActual % game.amountPlayers) + 1

        game.TurnoActual = next_turn 
        game.Timer = datetime.utcnow()   
        session.commit()
        
        if len(player.user_figure_cards) > 0: #If there is no winner
            #Reverse partial movements
            if len(player.plays) > 0:              
                for i in range(len(player.plays)):
                    revert_last_play(player_id)

            #Deal new cards
            player_figures_revealed_count = len([card for card in player.user_figure_cards if card.revealed])
            player_movement_count = len(player.user_movement_cards)

            get_random_movs_cards(player_id, 3 - player_movement_count)

            if not player.blocked:   #Nuevo
                get_random_figure_cards(player_id, 3 - player_figures_revealed_count)

        session.close()

        send_logs(game_id, f" {player.name} ha finalizado su turno")

        return "status_winner" if len(player.user_figure_cards) == 0 else "status_endturn"

    except ValueError as ve:
        session.rollback()
        raise ve
    finally:
        session.close()


def get_games_by_session_id(session_id : int):
    session = Session()
    try:
        players = session.query(Player).filter(Player.session_id == session_id).all()

        games = {player.game for player in players if player.game}

        return [GameListModel.from_db(game) for game in games]
    finally:
        session.close()


def new_session_id() -> int:
    session = Session()
    try:
        sessionCounter = session.query(SessionCounter).order_by(SessionCounter.countId.desc()).first()
        if not sessionCounter:
            new_Session = 1
        else:
            new_Session = sessionCounter.countId + 1

        new_session_counter = SessionCounter(countId=new_Session)
        session.add(new_session_counter)
        session.commit()

        return new_Session
    finally:
        session.close()
        
def get_player_id(game_id : int, session_id : int):
    session = Session()
    try:
        game = session.query(Game).filter(Game.id == game_id).first()

        if not game:
            raise ValueError("Game not found")

        player = session.query(Player).filter(Player.game_id == game_id, Player.session_id == session_id).first()
        if player is None:
            raise ValueError("Player not Found")
        
        return player.id
    finally:
        session.close
        
        
def get_players(game_id: int):
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()

        if not game:
            raise ValueError("Game not found")

        return [player.id for player in game.players]
    finally:
        session.close()


def get_time(game_id: int):
    session = Session()
    try:
        game = session.query(Game).filter_by(id=game_id).first()

        if not game:
            raise ValueError("Game not found")

        delta = datetime.utcnow() - game.Timer

        return 120 - int(delta.total_seconds())
    finally:
        session.close()