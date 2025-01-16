from typing import List
from pydantic import BaseModel, Field, validator
from models.tables import userFigureCard, userMovementCard
from enum import Enum

# ======================= Auxiliar Enum =======================

class MoveType(str, Enum):
    NO_SKIP_LINE = "NO_SKIP_LINE"
    SKIP_ONE_LINE = "SKIP_ONE_LINE"
    SHORT_DIAG = "SHORT_DIAG"
    LONG_DIAG = "LONG_DIAG"
    NORMAL_L = "NORMAL_L"
    INVERSED_L = "INVERSED_L"
    SKIP_THREE_LINES = "SKIP_THREE_LINES"

# ======================= Output Schemas =======================

class UserMovementCardsModel(BaseModel):
    card_id: int
    mov_type: MoveType

    @classmethod
    def get_cards(cls, mov_card: userMovementCard):
        return cls(card_id = mov_card.id, mov_type = mov_card.mov_type)
    
class UserMovementCardsResponse(BaseModel):
    cards : List[UserMovementCardsModel]
    

class UserFigureCardModel(BaseModel):
    id: int
    type: str = Field(max_length=3, min_length=2)
    blocked: bool

    @classmethod
    def from_db(cls, user_card: userFigureCard):
        return {
            "id": user_card.id,
            "type": user_card.type,
            "blocked": user_card.blocked
        }

class UserFigureCardsDeck(BaseModel):
    cards: List[UserFigureCardModel] = Field(...)
    count: int = Field(gt=0)

    @validator('cards')
    def validate_cards_length(cls, v):
        if not (1 <= len(v) <= 3):
            raise ValueError('La lista de cartas de figura debe tener entre 1 y 3 elementos.')
        return v
      
    @classmethod
    def from_db(cls, user_cards: List[UserFigureCardModel], count: int):
        return {
            "cards": user_cards,
            "count": count
        }