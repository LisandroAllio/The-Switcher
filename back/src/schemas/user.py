from pydantic import BaseModel, Field
from models.tables import Player

# ======================= Input Schemas =======================

class PlayerCreateModel(BaseModel):
    name: str = Field(max_length=32)
    session_id : int = Field(gt=0)


# ======================= Output Schemas =======================

class UserOut(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(max_length=32)

    @classmethod
    def from_db(cls, user: Player):
        return cls(
            id=user.id,
            username=user.username,
        )