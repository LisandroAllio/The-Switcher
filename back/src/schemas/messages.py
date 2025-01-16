from pydantic import BaseModel, Field
from models.tables import Logs, Messages

# ======================= Input Schemas =======================
class ChatMessage(BaseModel):
    user_id: int = Field(ge=0)
    game_id: int = Field(ge=0)
    content: str = Field(max_length=256)

# ======================= Output Schemas =======================
class MessageList(BaseModel):
    id: int
    name: str = Field(max_length=30)
    game_id: int
    content: str = Field(max_length=256)

    @classmethod
    def from_db(cls, message: Messages):
        return {
            "id": message.id,
            "name": message.user.name,
            "game_id": message.game_id,
            "content": message.content,
        }
    
class GameLog(BaseModel):
    id: int
    game_id: int = Field(ge=0)
    content: str = Field(max_length=256)

    @classmethod
    def from_db(cls, message: Logs):
        return {
            "id": message.id,
            "game_id": message.game_id,
            "content": message.content,
        }