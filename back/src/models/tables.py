from sqlalchemy import JSON, DateTime, ForeignKey, Column, Integer, String, Boolean, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from . import Base


# ======================= BD Tables ===========================

class Game(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    maxPlayers = Column(Integer, default=4, nullable=False)
    minPlayers = Column(Integer, default=2, nullable=False)
    password = Column(String, nullable=True)

    amountPlayers = Column(Integer, default=1, nullable=False)
    forbiddenColor = Column(Enum('RED', 'BLUE', 'GREEN', 'YELLOW'), nullable=True)
    inGame = Column(Boolean, default=False)
    TurnoActual = Column(Integer, nullable=True)
    Timer = Column(DateTime, nullable=True)
    
    players = relationship('Player', back_populates='game', cascade='all, delete')  # Relación con jugadores
    game_tokens = relationship('gameToken', back_populates='game', cascade='all, delete')  # Relación con fichas
    messages = relationship('Messages', back_populates='game', cascade='all, delete')  # Relación con mensajes
    logs = relationship('Logs', back_populates='game', cascade='all, delete')  # Relación con logs

# Tabla de Jugador
class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(32), nullable=False) 
    is_host = Column(Boolean, default=False)
    turn_assigned = Column(Integer, nullable=True)
    blocked = Column(Boolean, default=False)
    game_id = Column(Integer, ForeignKey('game.id'))   # Relación con la partida
    game = relationship('Game', back_populates='players')

    user_figure_cards = relationship('userFigureCard', back_populates='user', cascade='all, delete')
    user_movement_cards = relationship('userMovementCard', back_populates = 'user', cascade='all, delete')
    plays = relationship('Play', back_populates='players', cascade='all, delete')
    messages = relationship('Messages', back_populates='user', cascade='all, delete')
    
    session_id = Column(Integer, nullable = False)

# Tabla de cartas de figura
class userFigureCard(Base):
    __tablename__ = 'user_figure_cards'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    revealed = Column(Boolean, default=False)
    blocked = Column(Boolean, default=False)
    easy = Column(Boolean, default=False)
    type = Column(Enum('F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12'
                       ,'F13','F14','F15','F16','F17','F18','FE1','FE2','FE3','FE4','FE5'
                       ,'FE6','FE7'), nullable=False)
    userId = Column(Integer, ForeignKey('players.id'))
    user = relationship('Player', back_populates='user_figure_cards')


#Tabla de cartas de movimiento
class userMovementCard(Base):
    __tablename__ = 'movement_cards'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mov_type = Column(Enum('NO_SKIP_LINE','SKIP_ONE_LINE','SHORT_DIAG','LONG_DIAG','NORMAL_L','INVERSED_L','SKIP_THREE_LINES'), nullable=True)
    user_id = Column(Integer, ForeignKey('players.id'))
    user = relationship("Player", back_populates="user_movement_cards")


#Tabla de fichas
class gameToken(Base):
    __tablename__ = 'game_tokens'
    id = Column(Integer, primary_key=True, autoincrement=True) 
    color = Column(Enum('RED', 'BLUE', 'GREEN', 'YELLOW'), nullable=False)
    x_coordinate = Column(Integer, nullable=False)
    y_coordinate = Column(Integer, nullable=False)
    game_id = Column(Integer, ForeignKey('game.id'))

    game = relationship('Game', back_populates='game_tokens')


class Play(Base):
    __tablename__ = 'plays'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_movement_card_id = Column(Integer, ForeignKey('movement_cards.id')) 
    game_token_1_id = Column(Integer, ForeignKey('game_tokens.id'))
    game_token_2_id = Column(Integer, ForeignKey('game_tokens.id'))
    player_id = Column(Integer, ForeignKey('players.id'))

    user_movement_card = relationship("userMovementCard", foreign_keys=user_movement_card_id )
    game_token_1 = relationship("gameToken", foreign_keys=[game_token_1_id])
    game_token_2 = relationship("gameToken", foreign_keys=[game_token_2_id])

    players = relationship('Player', back_populates='plays')

class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('players.id'))
    game_id = Column(Integer, ForeignKey('game.id'))

    game = relationship('Game', back_populates='messages')
    user = relationship('Player', back_populates='messages')


class Logs(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey('game.id'))

    game = relationship('Game', back_populates='logs')

class SessionCounter(Base):
    __tablename__ = 'sessionCounter'
    countId = Column(Integer, primary_key=True, nullable=False, default=0)

