import core.games as games_repo
import core.game_logic.cards as cards
import core.game_logic.tokens as tokens
from fastapi import APIRouter, HTTPException, status

from schemas.game import GameTurn, LastMoveForm, MoveTokenForm, UsedFigureForm
from schemas.board import BoardFigureListModel, GameTokenListModel

from .websocket import connection_manager

in_game = APIRouter(tags=["in_game"])

# Información del turno
@in_game.get("/game/{game_id}/turn",
             response_model=GameTurn,
             name="Get game turn of the player",
             response_description="Returns the game turn of the player",
             status_code=status.HTTP_200_OK,
             responses={
                 404: {"description": "Game not found", }
             })
async def get_game_turn(game_id: int):
    try:
        game_turn = games_repo.get_game_turn(game_id)
        return game_turn
    except ValueError as e:
        error_message = str(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{error_message}")

# Consultar posicion de las fichas
@in_game.get("/game/{game_id}/tokens",
             response_model=GameTokenListModel,
             name="Get Game tokens",
             response_description="Returns a list of the tokens in format List(coordinate_x,coordinate_y,color)",
             status_code=status.HTTP_200_OK,
             responses={
                 404: {"description": "Game not found", },
             })
async def get_game_tokens(game_id: int):
    try:
        token_list = tokens.get_game_tokens(game_id)
        if not token_list:
            raise ValueError("No Tokens Found")

        token_list_model = GameTokenListModel.from_db(token_list)

        return token_list_model
    except ValueError as e:
        error_message = str(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{error_message}")

# Terminar turno
@in_game.get("/game/{game_id}/end_turn",
             response_model=GameTurn,
             name="Get game turn of the player",
             response_description="Returns the game turn of the player",
             status_code=status.HTTP_200_OK,
             responses={
                 404: {"description": "Game not found", }
             })
async def get_game_turn(game_id: int, player_id: int):
    try:
        is_winner = games_repo.end_turn(game_id, player_id)
        if is_winner:
            await connection_manager.broadcast(game_id, games_repo.create_game_message("status_winner", game_id, player_id))
        game_turn = games_repo.get_game_turn(game_id)
        return game_turn
    except ValueError as e:
        error_message = str(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{error_message}")

# Recepción cartas de movimiento y fichas a mover
@in_game.put("/game/{game_id}/move",
             response_model=dict,
             name="Move tokens",
             response_description="Return 200 OK if the movement was successful",
             status_code=status.HTTP_200_OK,
             responses={
                 400: {"description": "Invalid movement", }
             })
async def move_token(move_token_form: MoveTokenForm):
    try:
        cards.play_movement_card(move_token_form.player_id, move_token_form.move_id,
                                 move_token_form.token1_id, move_token_form.token2_id)

        await connection_manager.broadcast(
            move_token_form.game_id,
            games_repo.create_game_message("status_move", move_token_form.game_id))
        return {"message": "Token moved"}
    except ValueError as e:
        error_message = str(e)
        if "Invalid movement" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movement")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Deshacer movimiento
@in_game.post("/game/{game_id}/undo_last_movement",
              response_model=dict,
              name="Undo last movement",
              response_description="Return 200 OK after undoing the last movement",
              status_code=status.HTTP_200_OK,
              responses={
                  404: {"description": "Last movement not found"},
              })
async def undo_last_movement(last_move_form: LastMoveForm):
    try:
        cards.revert_last_play(last_move_form.player_id)

        await connection_manager.broadcast(
            last_move_form.game_id,
            games_repo.create_game_message("status_last_movement_undone", last_move_form.game_id))

        return {"message": "Last movement undone"}

    except ValueError as e:
        error_message = str(e)
        if "Last movement not found" in error_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Last movement not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mostrar figuras en tablero
@in_game.get("/game/{game_id}/show_all_figures",
             response_model=BoardFigureListModel,
             name="Show figures cards in board",
             response_description="Return 200 OK if any figure card is in the board",
             status_code=status.HTTP_200_OK,
             responses={
                 404: {"description": "There are no figures", },
                 404: {"description": "Game not found", },
             })
async def show_all_figures(game_id: int):
    try:
        figures = tokens.get_all_board_figures(game_id)
        return BoardFigureListModel(figures=figures)
    except ValueError as e:
        error_message = str(e)
        if "Figures not found" in error_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Figures not found")
        if "Game not found" in error_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Recepcion carta figura y actualizar color prohibido
@in_game.post("/game/{game_id}/use_figure",
              response_model=dict,
              name="Use figure card and update forbidden color",
              response_description="Return 200 OK if the figure card was used successfully",
              status_code=status.HTTP_200_OK,
              responses={
                    400: {"description": "Invalid Figure", },
                    400: {"description": "Figure has Forbidden Color", },
                    400: {"description": "Player cannot be blocked", },
                    400: {"description": "Card is blocked", },
              })
async def update_figure_card(use_figure_form: UsedFigureForm):
    try:
        cards.play_figure_card(use_figure_form.game_id, use_figure_form.player_id, use_figure_form.figure_id, use_figure_form.token_id)
        await connection_manager.broadcast(
            use_figure_form.game_id,
            games_repo.create_game_message("status_used_figure", use_figure_form.game_id))
        return {"message": "Figure card used successfully"}
    except ValueError as e:
        error_message = str(e)
        if "Invalid Figure" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Figure")
        if "Figure has Forbidden Color" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Figure has Forbidden Color")
        if "Player cannot be blocked" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Player cannot be blocked")
        if "Card is blocked" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Card is blocked")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
