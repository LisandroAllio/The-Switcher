from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from schemas.messages import ChatMessage, MessageList, GameLog
from schemas.socket import GameMessage
import core.games as games_repo

from core.messages import send_message, get_game_logs, get_game_messages

from .websocket import connection_manager

messages = APIRouter(tags=["messages"])

#===================================MESSAGES ROUTERS==============================================
@messages.post("/game/{game_id}/user/{user_id}/message",  
           name="Send message",
           response_description="Returns 201 when message is sent",
           status_code=status.HTTP_201_CREATED,
           responses={
               400: {"description": "Bad Request: Invalid input data"},
               500: {"description": "Internal Server Error"}
           })

async def new_game_message(Message : ChatMessage): 
    try: 
        send_message(Message.user_id, Message.game_id, Message.content)
        await connection_manager.broadcast(
                                Message.game_id,
                                games_repo.create_game_message("chat_message", Message.game_id))  
        return {"message": "Message sent"}
    except ValueError as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad Request: {error_message}")
    except SQLAlchemyError as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database Error: {error_message}")
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {error_message}")
    
@messages.get("/game/{game_id}",  
           response_model=list[MessageList], 
           name="Get messages",
           response_description="Returns 201 when all messages are sent",
           status_code=status.HTTP_201_CREATED,
           responses={
               400: {"description": "Bad Request: Invalid input data"},
               404: {"description": "No messages available for that game"},
               500: {"description": "Internal Server Error"}
           })
async def get_messages(game_id: int):
    try:
        messages = get_game_messages(game_id)
        if not messages:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No messages available for that game')
        return messages
    except ValueError as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad Request: {error_message}")
    except SQLAlchemyError as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database Error: {error_message}")
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {error_message}")


#===================================LOGS ROUTERS==============================================    
@messages.get("/game/{game_id}/logs",
           response_model=list[GameLog], 
           name="Get messages",
           response_description="Returns 201 when all messages are sent",
           status_code=status.HTTP_201_CREATED,
           responses={
               400: {"description": "Bad Request: Invalid input data"},
               404: {"description": "No messages available for that game"},
               500: {"description": "Internal Server Error"}
           })
async def get_logs(game_id: int):
    try:
        messages = get_game_logs(game_id)
        if not messages:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No messages available for that game')
        return messages
    except ValueError as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad Request: {error_message}")
    except SQLAlchemyError as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database Error: {error_message}")
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {error_message}")