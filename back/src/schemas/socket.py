from enum import Enum
from pydantic import BaseModel, Field
from models.tables import Game, Player
from schemas.game import UsersInfo, GameListModel



# ======================= Auxiliar Enums =======================

class GameEventTypes(Enum):
    leave = "leave"
    start = "start"
    join = "join"
    endturn = "endturn"
    moveToken = "moveToken"
    status_last_movement_undone = "status_last_movement_undone"
    status_used_figure = "status_used_figure"
    reconect = "status_reconect"


    @classmethod
    def is_valid_event_type(cls, type: str):
        return type in GameEventTypes.__members__

class GameStatusTypes(Enum):
    info = "status_info"
    leave = "status_leave"
    start = "status_start"
    join = "status_join"
    endturn = "status_endturn"
    moveToken = "status_move"
    status_last_movement_undone = "status_last_movement_undone"
    status_used_figure = "status_used_figure"
    chat_message = "chat_message"
    


# ======================= Output Schemas =======================
class GameMessage(BaseModel):
    type: GameStatusTypes = Field(...)

    @classmethod
    def create(cls, type: GameStatusTypes, game: Game, user_id: int):
        match type:
            case "status_info":
                return {
                    "type": type,
                    "game": GameListModel.from_db(game),
                }
            case "status_winner":
                return {
                    "type": type,
                    "user_left": user_id,
                    "winner": next((p.name for p in game.players if p.id == user_id), None)
                }
            case _:
                return {
                    "type": type,
                    "user_left": user_id,
                    "game": {
                        "users": UsersInfo.get_users_info(game),
                    },
                }

class ErrorMessage(BaseModel):
    type: str = Field("error")
    message: str = Field(...)

    @classmethod
    def create(cls, message: str):
        return {
            "type": "error",
            "description": message,
        }