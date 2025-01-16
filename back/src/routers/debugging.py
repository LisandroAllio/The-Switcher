from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import sessionmaker
from models import engine
from schemas.game import GameIdInfo
from models.tables import userFigureCard

debug = APIRouter(tags=["debugging"])

# Crea una sesión
Session = sessionmaker(bind=engine)

@debug.post("/{user_id}/figure-cards-reset", 
           response_model=int, 
           name="Set user figure cards on 0",
           response_description="Returns 201 with the game id",
           status_code=status.HTTP_201_CREATED,
           responses={
               400: {"description": "Minium or maximun users invalid value",},
               422: {"description": "Name or Password too long",}
           })

async def remove_figure_cards(user_id: int): 
    session = Session()
    try:
        for i in range(0, session.query(userFigureCard).filter_by(userId=user_id).count() - 1):
            card = session.query(userFigureCard).filter_by(userId=user_id).first()
            session.delete(card)
        session.commit()
        return 1
    except ValueError as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{error_message}")
    finally:
        session.close()