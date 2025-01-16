from fastapi import APIRouter, HTTPException, status
import core.games as games_repo 

timer = APIRouter(tags=["timer"])

#Listar Partidas
@timer.get(
    "/time/{game_id}",
    response_description="Returns 200 OK with a list of games\
          available in the database",
    status_code=status.HTTP_200_OK,
    responses={
               404: {"description": "No games found",},
    })
async def get_time_left(game_id: int):
    try:    
        return games_repo.get_time(game_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return games