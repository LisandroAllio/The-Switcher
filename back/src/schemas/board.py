from typing import List
from pydantic import BaseModel, Field, validator
from enum import Enum
from models.tables import gameToken, Play, userFigureCard
from schemas.card import UserFigureCardModel

# ======================= Auxiliar Enum =======================

class Color(str, Enum):
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"

# ======================= Output Schemas =======================

class GameTokenModel(BaseModel):
    id : int
    x_coordinate: int
    y_coordinate: int
    color: Color

    @classmethod
    def from_db(cls, token: gameToken):
        return {
            "id": token.id,
            "x_coordinate": token.x_coordinate,
            "y_coordinate": token.y_coordinate,
            "color": token.color
        }

class GameTokenListModel(BaseModel):
    tokens: List[GameTokenModel] = Field(...)

    @validator('tokens')
    def validate_token_list_length(cls, v):
        if not (len(v) == 36):
            raise ValueError('La lista de tokens debe tener 36 elementos.')
        return v

    @classmethod
    def from_db(cls, tokens: List[GameTokenModel]):
        return {
            "tokens": tokens
        }

class UserPlaysModel(BaseModel):
    move_type: str
    token_1: GameTokenModel
    token_2: GameTokenModel

    @classmethod
    def from_db(cls, play: Play):
        return {
            "move_type": play.user_movement_card.mov_type,
            "token_1": GameTokenModel.from_db(play.game_token_1),
            "token_2": GameTokenModel.from_db(play.game_token_2)
        }
    
class UserPlaysModelResponse(BaseModel):
    plays : List[UserPlaysModel]


class BoardFigureModel(BaseModel):
    figure: UserFigureCardModel
    tokens: List[List[GameTokenModel]]

    @classmethod
    def from_db(cls, card: userFigureCard, tokens: List[List[GameTokenModel]]):
        return {
            "figure": UserFigureCardModel.from_db(card),
            "tokens": tokens
        }

class BoardFigureListModel(BaseModel):
    figures : List[BoardFigureModel]