import React, { useEffect, useState } from 'react';
import './form.css';

const CreateFormPage = ({ onGoBack, onGameCreated}) => {
  const [gameType, setGameType] = useState('public');  // Estado para controlar si es pública o privada
  const [gameName, setGameName] = useState('');        // Estado para manejar el nombre de la partida
  const [maxPlayers, setMaxPlayers] = useState('');    // Estado para manejar el máximo de jugadores
  const [minPlayers, setMinPlayers] = useState('');    // Estado para manejar el mínimo de jugadores
  const [password, setPassword] = useState('');        // Estado para manejar la contraseña
  const [userName, setUserName] = useState('');        // Estado para manejar el usuario
  const [loading, setLoading] = useState(false);        // Estado de carga
  const [errorMessage, setErrorMessage] = useState(''); // Estado para manejar los mensajes de error
  const [userNameError, setUserNameError] = useState('');  // Estado para el error del nombre de usuario


  // Estados separados para manejar errores de cada campo
  const [gameNameError, setGameNameError] = useState('');
  const [maxPlayersError, setMaxPlayersError] = useState('');
  const [minPlayersError, setMinPlayersError] = useState('');
  const sessionID = sessionStorage.getItem("sessionID");

  const fetchHostUserId = async (gameId) => {
    if (!gameId) {
      console.error('gameId está undefined');
      return;
    }
    try {
      const response = await fetch(`http://localhost:8000/games/${gameId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error('Error al obtener el host del juego');
      }

      const gameData = await response.json();
      const userId = gameData.host_id;

      return userId;
    } catch (error) {
      console.error('Error al obtener el host del juego:', error);
      return null;
    }
  };

  // Función para manejar la creación de la partida
  const handleCreateGame = async (e) => {
    
    e.preventDefault();  // Evita que la página se recargue
    setLoading(true);

    // Validaciones

    if (!userName) {
      setUserNameError('El nombre de usuario es obligatorio');
      setLoading(false);  // Detener la carga si hay un error
      return;
    }

    if (gameName.length > 20) {
      setGameNameError('El nombre de la partida no puede tener más de 20 caracteres');
      return;
    }

    if (maxPlayers < 2 || maxPlayers > 4) {
      setMaxPlayersError('El número máximo de jugadores debe ser entre 2 y 4');
      return;
    }

    if (minPlayers < 2 || minPlayers > 4) {
      setMinPlayersError('El número mínimo de jugadores debe ser entre 2 y 4');
      return;
    }

    // Prepara los datos del juego
    const gameData = {
      game_model_data: {
        name: gameName,
        password: gameType === 'private' ? password : null,  // Solo enviar la contraseña si es privada
        maxPlayers: parseInt(maxPlayers, 10),
        minPlayers: parseInt(minPlayers, 10),
      },
      player_model_data: {
        name: userName,  // Nombre del jugador
        session_id: sessionID//Cambiar agregar endpoint

      }
    };

    try {
      // Realiza la solicitud POST al servidor
      const response = await fetch('http://localhost:8000/games/new', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(gameData),  // Enviar los datos como JSON
      });

      // Manejar la respuesta
      if (!response.ok) {
        throw new Error(`Error al crear la partida: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Partida creada con éxito:', result);  
      const gameId = result.id; 
      const userId = await fetchHostUserId(gameId);
      if (userId) {
        onGameCreated(gameId, userId);
      }

    } catch (error) {
      console.error('Error durante la creación del juego:', error);  // Manejar el error
      setErrorMessage('Hubo un problema al crear la partida. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleUserNameChange = (e) => {
    setUserName(e.target.value);
  
    // Limpiar el error si el usuario empieza a escribir
    if (e.target.value) {
      setUserNameError('');
    }
  };

  // Función para manejar el cambio en el nombre del juego
  const handleGameNameChange = (e) => {
    const value = e.target.value;
    if (value.length <= 20) {
      setGameName(value);
      setGameNameError('');  // Limpia el mensaje de error si está dentro del límite
    } else {
      setGameNameError('El nombre de la partida no puede tener más de 20 caracteres');
    }
  };

  // Función para manejar el cambio en el número máximo de jugadores
  const handleMaxPlayersChange = (e) => {
    const value = e.target.value;
    if (value >= 2 && value <= 4) {
      setMaxPlayers(value);
      setMaxPlayersError('');  // Limpia el mensaje de error si está dentro del límite
    } else {
      setMaxPlayersError('El número máximo de jugadores debe ser entre 2 y 4');
    }
  };

  // Función para manejar el cambio en el número mínimo de jugadores
  const handleMinPlayersChange = (e) => {
    const value = e.target.value;
    if (value >= 2 && value <= 4) {
      setMinPlayers(value);
      setMinPlayersError('');  // Limpia el mensaje de error si está dentro del límite
    } else {
      setMinPlayersError('El número mínimo de jugadores debe ser entre 2 y 4');
    }
  };

  // Función para manejar el cambio entre pública y privada
  const handleGameTypeChange = (event) => {
    setGameType(event.target.value);
  };

  useEffect(() => {
    console.log("Id sesion:", sessionID);
  });

  return (
    <div>

      {/* Campo Nombre de Usuario separado y posicionado */}
      <div className="user-name-container">
        <label htmlFor="userName" className="user-label">Nombre de Usuario</label>
        <div className="input-container">
          <input
            type="text"
            name="userName"
            id="userName"
            placeholder="Escribe su nombre de usuario"
            value={userName}
            onChange={handleUserNameChange}
            required
          />
        </div>
        {userNameError && <p className="error">{userNameError}</p>}  {/* Mostrar error si está vacío */}
      </div>

      {/* Formulario de crear partida */}
      <div className="form-container">
        <div className="title">
          <h2>Insertar Información de Partida</h2>
        </div>

        <form className="custom-form" onSubmit={handleCreateGame} data-testid="create-form">
          <div className="form-group">
            <label htmlFor="gameName">Nombre de la partida</label>
            <div className="input-container">
              <input
                type="text"
                name="gameName"
                id="gameName"
                placeholder="Escribe el nombre de la partida"
                value={gameName}
                onChange={handleGameNameChange}  // Maneja el estado del nombre
                required
              />
            </div>
            {gameNameError && <p className="error">{gameNameError}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="maxPlayers">Máximo de jugadores</label>
            <div className="input-container">
              <input
                type="number"
                name="maxPlayers"
                id="maxPlayers"
                placeholder="Número máximo de jugadores"
                value={maxPlayers}
                onChange={handleMaxPlayersChange}  // Maneja el estado de maxPlayers
                required
              />
            </div>
            {maxPlayersError && <p className="error">{maxPlayersError}</p>} 
          </div>

          <div className="form-group">
            <label htmlFor="minPlayers">Mínimo de jugadores</label>
            <div className="input-container">
              <input
                type="number"
                name="minPlayers"
                id="minPlayers"
                placeholder="Número mínimo de jugadores"
                value={minPlayers}
                onChange={handleMinPlayersChange}  // Maneja el estado de minPlayers
                required
              />
            </div>
            {minPlayersError && <p className="error">{minPlayersError}</p>} 
          </div>

          {/* Opciones de partida pública o privada */}
          <div className="form-group">
            <label>Tipo de partida</label>
            <div className="radio-container">
              <label>
                <input
                  type="radio"
                  name="gameType"
                  value="public"
                  checked={gameType === 'public'}
                  onChange={handleGameTypeChange}
                />
                Pública
              </label>
              <label>
                <input
                  type="radio"
                  name="gameType"
                  value="private"
                  checked={gameType === 'private'}
                  onChange={handleGameTypeChange}
                />
                Privada
              </label>
            </div>
          </div>

          {gameType === 'private' && (
            <div className="form-group">
              <label htmlFor="password">Contraseña</label>
              <div className="input-container">
                <input
                  type="password"
                  name="password"
                  id="password"
                  placeholder="Introduce una contraseña"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}  // Maneja el estado de la contraseña
                  required
                />
              </div>
            </div>
          )} 
          <button type="submit" className="custom-button1" disabled={loading} >Crear</button>

          <button className="back-button" onClick={onGoBack} disabled={loading}>Volver</button>
        </form>
      </div>
      {errorMessage && <p className="error">{errorMessage}</p>}
    </div>
  );
};

export default CreateFormPage;
