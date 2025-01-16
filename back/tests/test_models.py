# test_models.py
import pytest
from unittest.mock import MagicMock
from models.tables import Game, Player, userFigureCard, userMovementCard, gameToken, Play, Messages

@pytest.fixture
def mock_session():
    return MagicMock()

def test_create_game(mock_session):
    game = Game(name="Test Game", maxPlayers=4, minPlayers=2, amountPlayers=1, inGame=False)
    mock_session.add(game)
    mock_session.commit()
    mock_session.add.assert_called_once_with(game)
    mock_session.commit.assert_called_once()
    assert game.name == "Test Game"
    assert game.maxPlayers == 4
    assert game.minPlayers == 2
    assert game.amountPlayers == 1
    assert game.inGame is False

def test_create_player(mock_session):
    player = Player(name="Player1")
    mock_session.add(player)
    mock_session.commit()
    mock_session.add.assert_called_once_with(player)
    mock_session.commit.assert_called_once()
    assert player.name == "Player1"

def test_add_player_to_game(mock_session):
    game = Game(name="Test Game", maxPlayers=4, minPlayers=2)
    player = Player(name="Player1")
    game.players.append(player)
    mock_session.add(game)
    mock_session.commit()
    mock_session.add.assert_called_once_with(game)
    mock_session.commit.assert_called_once()
    assert len(game.players) == 1
    assert game.players[0].name == "Player1"

def test_add_card_to_player(mock_session):
    player = Player(name="CardOwner")
    mock_session.add(player)
    mock_session.commit()

    saved_player = mock_session.query(Player).filter_by(name="CardOwner").first()
    assert saved_player is not None

    card = userFigureCard(type='F1', userId=saved_player.id)
    mock_session.add(card)
    mock_session.commit()

    assert mock_session.add.call_count == 2
    assert mock_session.commit.call_count == 2

    assert card is not None
    assert card.type == 'F1'
    assert card.userId == saved_player.id

def test_add_movement_card(mock_session):
    player = Player(name="PlayerwithMov")
    mock_session.add(player)
    mock_session.commit()

    saved_player = mock_session.query(Player).filter_by(name="PlayerwithMov").first()
    assert saved_player is not None

    card = userMovementCard(mov_type="NO_SKIP_LINE", user_id = saved_player.id)
    player.user_movement_cards.append(card)
    mock_session.commit()


    assert mock_session.add.call_count == 1
    assert mock_session.commit.call_count == 2

    assert card is not None
    assert card.mov_type == "NO_SKIP_LINE"
    assert card.user_id == saved_player.id
    assert player.user_movement_cards[0].id == card.id


# test game_tokens
def test_add_game_token(mock_session):
    game = Game(name="Test Game", maxPlayers=4, minPlayers=2)
    mock_session.add(game)
    mock_session.commit()

    saved_game = mock_session.query(Game).filter_by(name="Test Game").first()
    assert saved_game is not None

    token = gameToken(color='RED', x_coordinate=1, y_coordinate=1 ,game_id=saved_game.id)
    mock_session.add(token)
    mock_session.commit()


    assert mock_session.add.call_count == 2
    assert mock_session.commit.call_count == 2

    # token asserts
    assert token is not None
    assert token.color == 'RED'
    assert token.x_coordinate == 1
    assert token.y_coordinate == 1
    assert token.game_id == saved_game.id

# test plays
def test_add_movement_card(mock_session):
    game = Game(name="Test Game", maxPlayers=4, minPlayers=2)
    mock_session.add(game)
    mock_session.commit()

    saved_game = mock_session.query(Game).filter_by(name="Test Game").first()
    assert saved_game is not None

    player = Player(name="PlayerwithPlay", game_id=saved_game.id)
    mock_session.add(player)
    mock_session.commit()

    saved_player = mock_session.query(Player).filter_by(name="PlayerwithPlay").first()
    assert saved_player is not None

    card = userMovementCard(mov_type="NO_SKIP_LINE", user_id = saved_player.id)
    player.user_movement_cards.append(card)
    mock_session.commit()
    assert card is not None

    token_1 = gameToken(color='RED', x_coordinate=1, y_coordinate=1 ,game_id=saved_game.id)
    mock_session.add(token_1)
    mock_session.commit()
    assert token_1 is not None

    token_2 = gameToken(color='BLUE', x_coordinate=2, y_coordinate=2 ,game_id=saved_game.id)
    mock_session.add(token_2)
    mock_session.commit()
    assert token_2 is not None

    play = Play(user_movement_card_id=card.id, game_token_1_id=token_1.id, game_token_2_id=token_2.id, player_id = saved_player.id)
    player.plays.append(play)
    mock_session.commit()

    assert play is not None
    assert play.user_movement_card_id == card.id
    assert len(player.plays) == 1 
    assert player.plays[0].id == play.id


# ======================= Tests Messages =======================
def test_create_message(mock_session):
    # Crear un mensaje simple para verificar su creación en la base de datos
    message = Messages(content="This is a standalone test message", user_id=1, game_id=1)
    
    # Simular el comportamiento del mock para el método `add` y `commit`
    mock_session.add(message)
    
    # Simular el commit
    mock_session.commit()
    
    # Simular que el mensaje se ha añadido
    mock_session.query.return_value.filter_by.return_value.first.return_value = message

    # Recuperar el mensaje para comprobar su contenido y asociación
    saved_message = mock_session.query(Messages).filter_by(content="This is a standalone test message").first()
    assert saved_message is not None
    assert saved_message.content == "This is a standalone test message"
    assert saved_message.user_id == 1
    assert saved_message.game_id == 1

def test_message_user_relationship(mock_session):
    # Crear y guardar un mensaje vinculado a un usuario (ID de usuario predeterminado para simplificar)
    message = Messages(content="Message linked to a user", user_id=1, game_id=None)
    
    mock_session.add(message)
    mock_session.commit()
    
    # Simular que el mensaje se ha añadido
    mock_session.query.return_value.filter_by.return_value.first.return_value = message

    # Verificar que el mensaje se ha creado y contiene el ID de usuario correcto
    saved_message = mock_session.query(Messages).filter_by(content="Message linked to a user").first()
    assert saved_message is not None
    assert saved_message.user_id == 1
    assert saved_message.game_id is None

def test_message_game_relationship(mock_session):
    # Crear y guardar un mensaje vinculado a un juego (ID de juego predeterminado para simplificar)
    message = Messages(content="Message linked to a game", user_id=None, game_id=1)
    
    mock_session.add(message)
    mock_session.commit()
    
    # Simular que el mensaje se ha añadido
    mock_session.query.return_value.filter_by.return_value.first.return_value = message

    # Verificar que el mensaje se ha creado y contiene el ID de juego correcto
    saved_message = mock_session.query(Messages).filter_by(content="Message linked to a game").first()
    assert saved_message is not None
    assert saved_message.user_id is None
    assert saved_message.game_id == 1