from typing import Dict
from pydantic import BaseModel, Field
from models.tables import Game

# ======================= Input Schemas =======================

class GameCreateModel(BaseModel):
    name: str = Field(max_length=32)
    password: str | None = Field(max_length=32)
    maxPlayers: int
    minPlayers: int


class GameJoinForm(BaseModel):
    game_id: int = Field(gt=0)
    user_name: str = Field(max_length=32)
    password: str | None = Field(max_length=32)
    session_id : int = Field(gt=0)

class MoveTokenForm(BaseModel):
    game_id: int = Field(gt=0)
    player_id: int = Field(gt=0)
    move_id: int = Field(gt=0)
    token1_id: int = Field(gt=0)
    token2_id: int = Field(gt=0)

class LastMoveForm(BaseModel):
    game_id: int = Field(gt=0)
    player_id: int = Field(gt=0)

class UsedFigureForm(BaseModel):
    game_id: int = Field(gt=0)
    player_id: int = Field(gt=0)
    figure_id: int = Field(gt=0)
    token_id: int = Field(gt=0)

# ======================= Output Schemas =======================

class GameIdInfo(BaseModel):
    id: int = Field(gt=0)


class UsersInfo(BaseModel):
    min: int = Field(gt=1, lt=5)
    max: int = Field(gt=1, lt=5)
    players: list[Dict[int, str]]

    @classmethod
    def get_users_info(cls, game: Game):
        users = game.players
        usernames = [{user.id: user.name} for user in users]
        return {
            "min": game.minPlayers,
            "max": game.maxPlayers,
            "players": usernames,
        }

class GameListModel(BaseModel):
    id: int
    name: str = Field(max_length=32)
    host_id: int
    in_game: bool = Field(default=False)
    is_private: bool = Field(default=False)
    users: UsersInfo

    @classmethod
    def from_db(cls, game: Game):
        return {
            "id": game.id,
            "name": game.name,
            "host_id": next(player.id for player in game.players if player.is_host),
            "in_game": game.inGame,
            "is_private": game.password is not None,
            "users": UsersInfo.get_users_info(game),
        }

class GameTurn(BaseModel):
    turnActive: int = Field(...)
    actualPlayer_id: int = Field(...)
    actualPlayer_name: str = Field(...)
    nextPlayer_id: int = Field(...)
    nextPlayer_name: str = Field(...)
    forbiddenColor: str | None = Field(...)
    amountPlayers: int = Field(...)

    @classmethod
    def from_db(cls, game: Game):
        turn_active = game.TurnoActual # {1 <= TurnoActual <= amountPlayers}
        amount_players = len(game.players)

        actual_player = next(player for player in game.players if player.turn_assigned == turn_active)   
        next_turn = (turn_active % amount_players) + 1                    
        next_player = next(player for player in game.players if player.turn_assigned == next_turn)

       
        return {
            "turnActive": turn_active,
            "actualPlayer_id": actual_player.id,
            "actualPlayer_name": actual_player.name,
            "nextPlayer_id": next_player.id,
            "nextPlayer_name": next_player.name,
            "forbiddenColor": game.forbiddenColor,
            "amountPlayers": amount_players
        }