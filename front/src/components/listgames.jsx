import React, { useState, useEffect, useRef } from "react";

const ListGames = ({ onBack, onJoinGame, userId }) => {
  const [partidas, setPartidas] = useState([]);
  const [activeGames, setActiveGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [joining, setJoining] = useState(null); // Para manejar el estado de unirse a la partida
  const [userName, setUserName] = useState(""); // Estado para almacenar el nombre del usuario
  const [userNameSubmitted, setUserNameSubmitted] = useState(false); // Controla si se ha ingresado el nombre
  const [filterName, setFilterName] = useState(""); // Estado para filtrar por nombre
  const [filterPlayers, setFilterPlayers] = useState("");
  const [selectedTab, setSelectedTab] = useState("disponibles");
  const [notify, setNotify] = useState("");
  const ws = useRef(null); // Referencia a WebSocket
  const hasConnected = useRef(false);
  const session_id = sessionStorage.getItem("sessionID");

  const connectWebSocket = async () => {
    if (!hasConnected.current || ws.current.readyState === WebSocket.CLOSED) {
      ws.current = new WebSocket(`ws://localhost:8000/ws/`);
      hasConnected.current = true; // Marcamos que ya está conectado

      ws.current.onopen = () => {
        console.log("Conectado al WebSocket");
      };
    }
    // Recibir mensajes del servidor
    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log("Mensaje recibido del servidor:", message);

      // Manejar diferentes tipos de mensajes del WebSocket
      switch (message.type) {
        case "status_update_games":
          handleListGames();
          console.log("Session ID listado (update):", session_id);
          handleListActiveGames();
          break;
        default:
          console.warn("Evento no reconocido");
      }
    };
  };

  useEffect(() => {
    if (!hasConnected.current) {
      connectWebSocket();
    }
  });

 useEffect(() =>{
  if (sessionStorage.getItem("currentframe") === 'list'){
    handleReconnectGame(sessionStorage.getItem("gameid"));
  }
 })

  const fetchGamesByName = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/games/list/name/${filterName}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          }
        }
      );

      if (!response.ok)
        throw new Error(`Error al filtrar por nombre: ${response.statusText}`);

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error obteniendo partidas por nombre:", error);
      return [];
    }
  };

  const fetchGamesByPlayers = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/games/list/players/${filterPlayers}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          }
        }
      );

      if (!response.ok)
        throw new Error(
          `Error al filtrar por jugadores: ${response.statusText}`
        );

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error obteniendo partidas por jugadores:", error);
      return [];
    }
  };

  // Función para obtener la lista de partidas
  const handleListGames = async () => {
    setLoading(true);
    setError(null);
    setPartidas([]);

    try {
      let partidasResult = [];

      if (filterName.trim()) {
        partidasResult = await fetchGamesByName();
      }

      if (filterPlayers.trim()) {
        const partidasByPlayers = await fetchGamesByPlayers();
        partidasResult =
          partidasResult.length > 0
            ? partidasResult.filter((p) =>
              partidasByPlayers.some((pp) => pp.id === p.id)
            ) // Intersección de resultados
            : partidasByPlayers;
      }

      // Si no hay filtros, obtenemos todas las partidas
      if (!filterName && !filterPlayers) {
        const response = await fetch("http://localhost:8000/games/list", {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          }
        });

        if (response.status === 404) {
          // Si es un 404, significa que no hay partidas disponibles, pero sigue siendo un caso esperado
          console.warn("No se encontraron partidas disponibles.");
          setPartidas([]); // Muestra el listado vacío
          setLoading(false);
          return; // Salimos del bloque para no lanzar un error
        }

        if (!response.ok)
          throw new Error(
            `Error al obtener todas las partidas: ${response.statusText}`
          );

        const data = await response.json();
        partidasResult = data;
      }

      const partidasDisponibles = partidasResult.filter(
        (partida) => !partida.in_game
      );
      setPartidas(partidasDisponibles);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleListActiveGames = async () => {
    setLoading(true);
    setError(null);
    console.log("Session ID listado (funcion):", session_id);
    console.log(`URL de solicitud: http://localhost:8000/games/get_session_id_games/${session_id}`);

    try {
      const response = await fetch(
        `http://localhost:8000/get_session_id_games/${session_id}`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" }
        }
      );

      if (response.status === 404) {
        // Si es un 404, significa que no hay partidas disponibles, pero sigue siendo un caso esperado
        console.warn("No se encontraron partidas activas.");
        setActiveGames([]); // Muestra el listado vacío
        setLoading(false);
        return; // Salimos del bloque para no lanzar un error
      }

      if (!response.ok)
        throw new Error(
          `Error al obtener partidas activas: ${response.statusText}`
        );
      const data = await response.json();
      console.log("Partidas activas:", data);
      setActiveGames(data); // Almacena las partidas activas
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Función para unirse a una partida con el gameId, userName y password
  const handleJoinGame = async (gameId, password) => {
    setJoining(gameId); // Marcamos la partida a la que se está intentando unir

    try {
      const response = await fetch(`http://localhost:8000/games/join`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          game_id: gameId,
          user_name: userName,
          password: password || "", // Contraseña (o vacío si no es privada)
          session_id: session_id
        })
      });

      // Verificamos si la respuesta es 200
      if (response.status === 200) {
        const data = await response.json();

        // Obtener la lista de jugadores
        const players = data.users.players;

        // Verifica si hay jugadores en la lista
        if (players.length > 0) {
          // Obtiene el último jugador (último objeto en el array)
          const lastPlayerObj = players[players.length - 1];

          // Extrae la ID del último jugador (la clave del objeto)
          const lastPlayerId = Object.keys(lastPlayerObj)[0];
          console.log("User ID:", lastPlayerId);
          userId = lastPlayerId;
        }
        // Cambiar al frame del tablero si todo está bien
        console.log("Entrando al tablero...");
        console.log("User ID: %d Game ID: %d", userId, gameId);
        onJoinGame(userId, gameId); // Cambiar al frame del tablero
      } else if (response.status === 401) {
        // Error de partida llena
        console.error("Error 401: Contraseña incorrecta.");
        setNotify("Contraseña Incorrecta.");
        setTimeout(() => {
          setNotify(""); // Limpiar el mensaje después de 3 segundos
        }, 3000);
      } else if (response.status === 403) {
        // Error de partida llena
        console.error("Error 403: El juego está lleno.");
        setNotify("El juego esta lleno.");
        setTimeout(() => {
          setNotify(""); // Limpiar el mensaje después de 3 segundos
        }, 3000);
      } else if (response.status === 404) {
        // Error de juego no encontrado
        console.error("Error 404: El juego no fue encontrado.");
        setNotify("El juego no fue encontrado.");
        setTimeout(() => {
          setNotify(""); // Limpiar el mensaje después de 3 segundos
        }, 3000);
      } else if (response.status === 422) {
        // Error de validación
        const errorData = await response.json();
        console.error("Error 422: Error de validación.");
        throw new Error(`Error de validación: ${errorData.detail}`);
      } else {
        // Otros errores
        console.error(`Error ${response.status}: Error inesperado.`);
        throw new Error(`Error inesperado: ${response.statusText}`);
      }
    } catch (error) {
      // Mostrar el mensaje de error en la interfaz y detener el flujo
      console.error("Error capturado:", error.message);
      return;
    } finally {
      setJoining(null);
    }
  };

  // Handle de games activas
  const handleReconnectGame = async (gameId) => {

    try {
      const player_id = await fetch(`http://localhost:8000/games/${gameId}/${session_id}/get_player_id`, {
        method: "GET",
        headers: { "Content-Type": "application/json" }
      });

      if (player_id.status == 200) {

        const game = await fetch(`http://localhost:8000/games/${gameId}`, {
          method: "GET",
          headers: { "Content-Type": "application/json" }
        });

        console.log("NO QUIERO JUGAR")
        const dataplayer = await player_id.json()
        console.log("Toda data player", dataplayer)
        console.log("Data player.id es:", dataplayer.player_id)
        const data = await game.json()
        console.log("Toda data de game es:", data)

        for (let i = 0; i < 4; i++) {
          // Obtén el ID del jugador como clave del objeto
          const playerId = Object.keys(data.users.players[i])[0];
          
          // Compara el ID con el que tienes en dataplayer
          if (parseInt(playerId) === dataplayer.player_id) {
            console.log("APARECI");
            sessionStorage.setItem("reconecting", true);
            console.log("Este sapo asqueroso es: ", playerId);
            console.log("El id del game en list es:", gameId);

            
            onJoinGame(dataplayer.player_id, gameId);
          }
        }
        
      }

    } catch (error) {
      return;
    }
  }


  // Ejecuta la función de obtener partidas al montar el componente
  useEffect(() => {
    if (userNameSubmitted && userName.trim()) {
      handleListGames();
      console.log("Session ID listado (primero):", session_id);
      handleListActiveGames();
    }
  }, [userNameSubmitted, userName]);

  // Si el nombre de usuario no se ha ingresado, muestra un formulario para ingresarlo
  if (!userNameSubmitted && sessionStorage.getItem("currentframe") !== "list") {
    return ( 
      <div className="username-container">
        <h1>Ingresa tu nombre para continuar</h1>
        <form
          onSubmit={(e) => {
            e.preventDefault(); // Evita el comportamiento por defecto del formulario
            if (userName.trim()) {
              setUserNameSubmitted(true); // Marca como ingresado el nombre del usuario
            }
          }}
        >
          <input
            type="text"
            value={userName}
            onChange={(e) => setUserName(e.target.value)} // Actualiza el nombre del usuario
            placeholder="Nombre de usuario"
            required
          />
          <button type="submit">Continuar</button>
        </form>
      </div>
    );
  }

  // Muestra el listado de partidas si ya se ingresó el nombre de usuario
  if (loading) {
    return <p>Cargando partidas...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  return (
    <div className="main1-container">
      <div className="tabs">
        <button
          className={selectedTab === "disponibles" ? "active-tab" : ""}
          onClick={() => { setSelectedTab("disponibles"); handleListGames }}
        >
          Disponibles
        </button>
        <button
          className={selectedTab === "activas" ? "active-tab" : ""}
          onClick={() => { setSelectedTab("activas"); console.log("Session ID listado (pestaña):", session_id); handleListActiveGames() }}
        >
          Activas
        </button>
      </div>
      <div className="partidas-container">
        {notify && <div className="notify-message">{notify}</div>}
        <div className="list-title">
          <h1>
            {selectedTab === "disponibles"
              ? "Lista de Partidas Disponibles"
              : "Lista de Partidas Activas"}
          </h1>
        </div>
        {selectedTab === "disponibles" && (
          <div className="filters">
            <input
              type="text"
              placeholder="Buscar por nombre"
              value={filterName}
              onChange={(e) => setFilterName(e.target.value)} // Actualiza el estado del filtro de nombre
            />

            <input
              type="number"
              placeholder="Buscar por jugadores"
              value={filterPlayers}
              onChange={(e) => setFilterPlayers(e.target.value)} // Actualiza el estado del filtro de jugadores
            />
            <button onClick={handleListGames}>Buscar</button>
          </div>
        )}
        <ul className="partidas-list">
          {(selectedTab === "disponibles" ? partidas : activeGames).map((partida) => (
            <li key={partida.id}>
              <h3>{partida.name}</h3> {/* Muestra el nombre de la partida */}
              <p>
                Min/Max: {partida.users.min} - {partida.users.max}
              </p>{" "}
              {/* Muestra el rango de jugadores */}
              <p>Jugadores: {partida.users.players.length}</p>
              <p>Partida {partida.is_private ? "Privada" : "Pública"}</p>{" "}
              {/* Muestra si es privada o pública */}
              {partida.is_private && selectedTab === "disponibles" && (
                <input
                  type="password"
                  placeholder="Contraseña"
                  onChange={(e) => (partida.password = e.target.value)} // Guardar la contraseña temporalmente
                />
              )}
              {selectedTab === "disponibles" ? (
                <button
                  className="join-button"
                  onClick={() => handleJoinGame(partida.id, partida.password)} // Pasa el gameId y password (si es privada)
                  disabled={joining === partida.id} // Deshabilita el botón si ya te estás uniendo a esa partida
                >
                  {joining === partida.id ? "Uniéndote..." : "Unirse"}
                </button>
              ) : (
                <button
                  className="join-button"
                  onClick={() => handleReconnectGame(partida.id)}
                  disabled={joining === partida.id}
                >
                  {joining === partida.id ? "Reconectando..." : "Reconectarse"}
                </button>
              )}
            </li>
          ))}
        </ul>
        <div className="back-button-container">
          <button className="back-button1" onClick={onBack}>
            Volver
          </button>
        </div>
      </div>
    </div>
  );
};

export default ListGames;
