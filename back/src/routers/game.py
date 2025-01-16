import core.games as games_repo
from fastapi import APIRouter, HTTPException, status

from schemas.game import GameCreateModel, GameIdInfo, GameListModel, GameJoinForm
from schemas.user import PlayerCreateModel

from .websocket import connection_manager
from .websocket import game_manager

game = APIRouter(tags=["games"])

#Crear  Partida
@game.post("/games/new", 
           response_model=GameIdInfo, 
           name="Create a new game",
           response_description="Returns 201 Created with the game id",
           status_code=status.HTTP_201_CREATED,
           responses={
               400: {"description": "Minium or maximun users invalid value",},
               422: {"description": "Name or Password too long",}
           })

async def new_game(game_model_data: GameCreateModel, player_model_data: PlayerCreateModel): 
    try: 
        new_game_id = games_repo.create_game(
            game_model_data.name,
            player_model_data.name,
            player_model_data.session_id,
            game_model_data.minPlayers,
            game_model_data.maxPlayers,
            game_model_data.password
        )

        await game_manager.send_message("status_update_games")

        return GameIdInfo(id=new_game_id)
    except ValueError as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{error_message}")
    
#Listar Partidas
@game.get(
    "/games/list",
    response_model=list[GameListModel],
    response_description="Returns 200 OK with a list of games\
          available in the database",
    status_code=status.HTTP_200_OK,
    responses={
               404: {"description": "No games found",},
    })
async def get_games():
    games = games_repo.get_games() 
    if not games:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No games available')
    return games

#Listar Partidas por nombre
@game.get(
    "/games/list/name/{name}",
    response_model=list[GameListModel],
    response_description="Returns 200 OK with a list of games\
          available in the database",
    status_code=status.HTTP_200_OK,
    responses={
               404: {"description": "No games available with that name",},
    })
async def get_games_by_name(name=str):
    games = games_repo.get_games_by_name(name) 
    if not games:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No games available with that name')
    return games

#Listar Partidas por numero de jugadores
@game.get(
    "/games/list/players/{players}",
    response_model=list[GameListModel],
    response_description="Returns 200 OK with a list of games\
          available in the database",
    status_code=status.HTTP_200_OK,
    responses={
               404: {"description": "No games available with that number of players",},
    })
async def get_games_by_players(players=int):
    games = games_repo.get_games_by_players(players) 
    if not games:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No games available with that number of players')
    return games

#Obtener Una Partidas
@game.get(
    "/games/{game_id}",
    response_model=GameListModel,
    response_description="Returns 200 OK with a list of games\
          available in the database",
    status_code=status.HTTP_200_OK,
    responses={
               404: {"description": "No games found",},
    })
async def get_game(game_id= int):
    game = games_repo.get_game_id(game_id) 
    if not game:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No games available')
    return game


#Unirse a partida
@game.put(
    "/games/join",
    response_model=GameListModel,
    response_description="Returns 200 OK with info of game",
    status_code=status.HTTP_200_OK,
    responses={
            404: {"description": "Game not found",},
            403: {"description": "Game is full",},
            401: {"description": "Incorrect Password"}
    })
async def join_game(join_model_data: GameJoinForm):
    try: 
        game_info = games_repo.join_game(join_model_data.game_id, join_model_data.user_name, join_model_data.password, join_model_data.session_id)
        await connection_manager.broadcast(
                                join_model_data.game_id,
                                games_repo.create_game_message("status_join", join_model_data.game_id))  
        
        await game_manager.send_message("status_update_games")

        return game_info
    except ValueError as e:
        error_message = str(e)
        if "Game not found" in error_message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
        elif "Game is full" in error_message:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Game is full")
        elif "Incorrect Password" in error_message:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Password")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)  
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

#Abandonar partida
@game.patch("/games/{game_id}/leave")
async def leave_game(game_id: int, user_id: int):
    try:
        message = games_repo.leave_game(game_id, user_id)
        if message == "status_winner" or message == "status_cancel_game":
            games_repo.end_game(game_id)
        return {'message': message}
    except ValueError:
        raise HTTPException(status_code=404, dettokensail='Could not leave the game')


#Iniciar partida
@game.patch("/games/{game_id}/start")
async def start_game(game_id: int):
    try:
        games_repo.start_game(game_id)
        return {'message': 'Game started'}
    except ValueError: 
        raise HTTPException(status_code=404, detail='Could not start the game')



#Obtener partidas activas
@game.get("/get_session_id_games/{session_id}",
          response_model = list[GameListModel],
          response_description = "Returns 200 OK with a list of games with the session id requested",
          status_code = status.HTTP_200_OK,
          responses = {
                    404 : {"description" : "No games available with that session id"}
          }
          )
async def get_active_games(session_id : int):
    games = games_repo.get_games_by_session_id(session_id)
    if not games :
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No games available with that session id')
    return games

# Nuevo Session_id
@game.get("/get_session_id")
async def new_session_id():
    try:
        session_id = games_repo.new_session_id()
        return {'session_id': session_id}
    except ValueError:
        raise HTTPException(status_code=404, detail='Could not create a new  id')


#Obtener player_id
@game.get("/games/{game_id}/{session_id}/get_player_id",
          response_description = "Returns 200 OK with the player id",
          status_code = status.HTTP_200_OK,
          responses = {
                    404 : {"description" : "Game not found"},
                    404 : {"description" : "Player not found"}
          })
async def get_player_id(game_id : int, session_id : int):
    try:
        player_id = games_repo.get_player_id(game_id , session_id)
        await connection_manager.broadcast(
                                game_id,
                                games_repo.create_game_message("status_reconect", game_id))
        return {'player_id' : player_id}
    except ValueError as e:
        error_message = str(e)
        if "Game not found" in error_message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
        elif "Player not found" in error_message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)  
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)