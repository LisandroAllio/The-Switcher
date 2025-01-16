import core.game_logic.cards as cards
from fastapi import APIRouter, HTTPException, status

from schemas.card import UserFigureCardsDeck, UserMovementCardsResponse
from schemas.board import UserPlaysModelResponse

card = APIRouter(tags=["cards"])

# Solicitar cartas figura  
@card.get("/games/{game_id}/{user_id}/figure-cards", 
           response_model=UserFigureCardsDeck, 
           name="Get user figure cards",
           response_description="Returns the users figure cards in format List(id, type)",
           status_code=status.HTTP_200_OK,
           responses={
               404: {"description": "No cards found for that user",},
               422: {"description": "Validation error"},
           })
async def get_figure_cards(game_id: int, user_id: int):
    try:
        card_list, card_count = cards.get_user_figure_cards(user_id)
        if not card_list:
            raise ValueError("No cards found")
        res_model = UserFigureCardsDeck.from_db(card_list, card_count)
        return res_model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Consultar Cartas de movimiento
@card.get("/game/{game_id}/{user_id}/movements", 
           response_model=UserMovementCardsResponse, 
           name="Get User movement cards",
           response_description="Returns the User movement card in format List(card_id,mov_type)",
           status_code=status.HTTP_200_OK,
           responses={
               404: {"description": "User not found",},
               404: {"description": "Game not found"}
           })
async def get_movement_cards(game_id : int, user_id : int):
    try:
        mov_cards = cards.get_player_movement_cards(game_id, user_id)
        if not mov_cards:
            raise ValueError("No Movement Cards Found")
        return  UserMovementCardsResponse(cards=mov_cards)
    except ValueError as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{error_message}")
    
#Consultar Cartas de movimiento jugadas
@card.get("/game/{game_id}/{user_id}/plays", 
           response_model=UserPlaysModelResponse, 
           name="Get User played cards",
           response_description="Returns the User movement card in format List(play)",
           status_code=status.HTTP_200_OK,
           responses={
               404: {"description": "User not found",},
               404: {"description": "No user found"}
           })
async def get_movement_cards(game_id : int, user_id : int):
    try:
        plays = cards.get_user_plays(user_id)
        if not plays:
            raise ValueError("No Played Cards Found")
        return UserPlaysModelResponse(plays=plays)
    except ValueError as e:
        error_message = str(e)
        if "No Played Cards Found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Played Cards Found")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{error_message}")