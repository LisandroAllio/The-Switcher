
from sqlalchemy.orm import sessionmaker
from models import engine
from models.tables import Messages, Logs
from schemas.messages import GameLog, MessageList

# Crea una sesión
Session = sessionmaker(bind=engine)


def send_message(user_id: int, game_id: int, message: str):
    session = Session()
    try:    
        new__message = Messages(user_id=user_id, game_id=game_id, content=message)
        session.add(new__message)
        session.commit()
        session.refresh(new__message)
        return 1
    except ValueError as e:
        raise e
    finally:
        session.close()

def get_game_messages(game_id: int):
    session = Session()
    try:
        messages = session.query(Messages).filter_by(game_id=game_id).all()
        return [MessageList.from_db(message) for message in messages ]
    except ValueError as e:
        raise e
    finally:
        session.close()

def send_logs(game_id: int, log: str):
    session = Session()
    try:    
        new_log = Logs(game_id=game_id, content=log)
        session.add(new_log)
        session.commit()
        session.refresh(new_log)
    except ValueError as e:
        raise e
    finally:
        session.close()

def get_game_logs(game_id: int):
    session = Session()
    try:
        messages = session.query(Logs).filter_by(game_id=game_id).all()
        return [GameLog.from_db(message) for message in messages ]
    except ValueError as e:
        raise e
    finally:
        session.close()

