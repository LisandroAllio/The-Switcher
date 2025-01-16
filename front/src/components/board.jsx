import React, { useState, useEffect, useRef } from "react";
import "./board.css";
import Movement from "./movement";
import Figuras from "./figuras";
import Chat from "./chat";
import LogComponent from "./LogComponent";


const BoardPage = ({ onLeaveGame, gameId, userId }) => {
  const { fetchGameTokens } = Movement({ gameId, userId });
  const [previousTokens, setPreviousTokens] = useState([]); // Estado para almacenar las fichas anteriores
  const colors = ["red", "blue", "green", "yellow"];
  const [timeLeft, setTimeLeft] = useState(120); // 120 segundos = 2 minutos
  const [tokens, setTokens] = useState([]);
  const [isHost, setIsHost] = useState(false); // Saber si el jugador es el host
  const [gameStarted, setGameStarted] = useState(() => {
    return sessionStorage.getItem(gameId) === "true";
  });
  const [players, setPlayers] = useState([]); // Lista de jugadores que se han unido
  const [minplayers, setminPlayers] = useState(1000); // Lista de jugadores que se han unido
  const [lengthplayers, setlengthPlayers] = useState(0);
  const [gameInfo, setGameInfo] = useState(null); // Información de la partida
  const [turnInfo, setTurnInfo] = useState(null); // Información de la partida
  const [myTurn, setMyTurn] = useState(false); // Información de la partida
  const [moveCount, setMoveCount] = useState(0);
  const [undoCount, setUndoCount] = useState(0);
  const [leaveMessage, setLeaveMessage] = useState(""); // Estado para el mensaje de abandono
  const [winnerMessage, setWinnerMessage] = useState(""); // Estado para el mensaje de ganador
  const [figureCards, setFigureCards] = useState({
    left: [],
    right: [],
    top: [],
    bottom: []
  });
  const [showAllMovementCards, setShowAllMovementCards] = useState(false);
  const [movementCards, setMovementCards] = useState([]);
  const ws = useRef(null); // Usamos `useRef` para almacenar la conexión WebSocket
  const hasConnected = useRef(false); // Nueva bandera para controlar la conexión WebSocket
  const { handleCardClick, handleTokenClick, handleUndoMove } = Movement({
    gameId,
    userId,
    movementCards
  });
  const [selectedFigure, setSelectedFigure] = useState(null);
  const [selectedMovement, setSelectedMovement] = useState(false);
  const [tokensh, setTokensh] = useState([]);
  const [triggerFetchFigures, setTriggerFetchFigures] = useState(0); // Disparador para volver a fetchear figuras
  const [fetchedFigures, setFetchedFigures] = useState([]); // Estado para guardar todas las figuras fetcheadas
  const [selectedfiguretoken, setSelectedfiguretoken] = useState(null);
  const [highlightedTokens, setHighlightedTokens] = useState([]);
  const [gameCancel, setGameCancel] = useState(false);
  const [playersReady, setPlayersReady] = useState(false);
  const [winner, setWinner] = useState("");
  const [warningMessage, setWarningMessage] = useState(""); // Estado para el mensaje de advertencia
  const [hasUnreadMessages, setHasUnreadMessages] = useState(false);
  const [messages, setMessages] = useState([]); // Estado para los mensajes
  const [logs, setLogs] = useState([]);
  const [confirm, setConfirm] = useState(false);
  const [confirmMessage, setConfirmMessage] = useState("");

  const [errorMessage, setErrorMessage] = useState(""); // Estado para el mensaje de error


  const reorderPlayers = (players, currentUserId) => {
    if (!players || players.length === 0) {
      console.warn("Lista de jugadores vacía o indefinida.");
      return [null, null, null, null]; // Devuelve cuatro posiciones vacías si no hay jugadores
    }

    // Asegúrate de que currentUserId es un número
    const normalizedCurrentUserId = Number(currentUserId);

    // Encuentra al jugador actual y su índice
    const currentUserIndex = players.findIndex(
      (player) => player.userId === normalizedCurrentUserId
    );

    if (currentUserIndex === -1) {
      console.log(
        `No se encontró al usuario actual (ID: ${normalizedCurrentUserId}) en la lista de jugadores. Jugadores recibidos:`,
        players
      );
      return [null, null, null, null]; // Devolver una lista vacía si no encuentra al usuario actual
    }

    console.log(
      `Jugador actual: ${normalizedCurrentUserId} en la posición ${currentUserIndex}`
    );

    // Colocar al jugador actual en la posición `bottom`
    const reordered = [players[currentUserIndex]];

    // Reorganizar el resto de los jugadores en las posiciones izquierda, derecha y arriba
    let remainingPlayers = [
      ...players.slice(currentUserIndex + 1),
      ...players.slice(0, currentUserIndex)
    ];

    // Asignar jugadores a las posiciones left, right, y top
    for (let i = 0; i < 3; i++) {
      if (remainingPlayers[i]) {
        reordered.push(remainingPlayers[i]);
      } else {
        reordered.push(null); // Rellenar con null si hay menos de 4 jugadores
      }
    }

    console.log("Jugadores reordenados:", reordered);
    return reordered;
  };
  //!!!!!!!!!!!!!NO MOVER DE LUGAR!!!!!!!!!!!!!!!!! funciona por magia :p
  const reorderedPlayers = React.useMemo(
    () => reorderPlayers(players, userId),
    [players, userId]
  );

  const handleResetFigureCards = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/${userId}/figure-cards-reset`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          }
        }
      );
      if (!response.ok) {
        throw new Error("Error al resetear las cartas de figuras");
      }
      const data = await response.json(); // Parseamos la respuesta a JSON
      console.log("Reset de cartas de figura exitoso:", data);
    } catch (error) {
      console.error("Error:", error);
      alert("Hubo un error al resetear las cartas de figura.");
    }
  };
  //===================== Resaltado de figuras =============================//

  const useFigureCard = async (figureId, tokensid) => {
    console.log("Token IDs:", tokensid);
    console.log("Figure IDs:", figureId);

    try {
      const response = await fetch(
        `http://localhost:8000/game/${gameId}/use_figure`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            game_id: gameId,
            player_id: userId,
            figure_id: figureId, // ID de la carta figura seleccionada
            token_id: tokensid // Lista de tokens asociados a la figura
          })
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        console.log("Error al usar carta figura:", errorData.detail);
        setErrorMessage("Error al usar carta figura: " + errorData.detail); // Actualiza el estado de error
        return;
      }

      const data = await response.json();
      console.log("Carta figura usada con éxito:", data);
      setErrorMessage("");
      // Refrescar las cartas figura después de usar una
    } catch (error) {
      console.log("Error al usar la carta figura:", error);
      setErrorMessage("Error al usar carta figura: " + errorData.detail); // Actualiza el estado de error

    }
  };

  useEffect(() => {
    if (errorMessage) {
      const timer = setTimeout(() => {
        setErrorMessage(""); // Limpia el mensaje de error después de 2 segundos
      }, 3000);

      // Limpia el temporizador si el componente se desmonta o errorMessage cambia
      return () => clearTimeout(timer);
    }
  }, [errorMessage]);

  // Función para usar la carta figura
  const handleUseFigure = (token) => {
    if (selectedFigure) {
      useFigureCard(selectedFigure.id, token.id); // Llamamos a la función de `Figuras`
      setSelectedFigure(null);
      // Fuerza un reset de los tokens para asegurarse de que las posiciones se recalculen
      fetchGameInfo();
      setTokensh([]);
      handleFiguresFetched();
      setTokens([]);
      fetchAndSetTokens();
    } else {
      alert("Por favor selecciona una figura y tokens");
    }
  };

  const handleFiguresFetched = (figures) => {
    if (figures && Array.isArray(figures)) {
      setFetchedFigures(figures);

      const allTokensh = figures.flatMap((figure) =>
        Array.isArray(figure.tokens) ? figure.tokens.flat() : []
      );
      setTokensh(allTokensh);
    } else {
      console.log("No se recibieron figuras o no es un array");
      setTokensh([]);
    }
  };
  // Función para manejar la selección de una figura específica
  const handleFigureSelected = (figure) => {
    console.log("Figura seleccionada:", figure);
    console.log("FetchedFigures:", fetchedFigures);
    const selectedFigureData = fetchedFigures.find(
      (f) => f.figure.id === figure.id
    );
    console.log(
      "Datos de la figura seleccionada en fetchedFigures:",
      selectedFigureData
    ); // Depuración de la figura seleccionada

    if (
      selectedFigureData &&
      selectedFigureData.tokens &&
      Array.isArray(selectedFigureData.tokens)
    ) {
      // Extraemos los tokens de la figura seleccionada
      const tokensForSelectedFigure = selectedFigureData.tokens.flat();
      setTokensh(tokensForSelectedFigure); // Resaltamos solo los tokens de esa figura
    } else {
      console.log(
        "La figura seleccionada no tiene tokens definidos o no es un array"
      );
    }
    setSelectedFigure(figure);
    console.log("SELECIONO A:", selectedFigure);
  };

  const isTokenHighlighted = (tokenId) => {
    return tokensh.some((token) => token.id === tokenId);
  };

  useEffect(() => {
    if (tokens.length > 0) {
      console.log("Tokens actualizados, disparando el fetch de figuras...");
      setTriggerFetchFigures((prev) => prev + 1);
    }
  }, [tokens]);
  //======================================================================//

  const handleTokenClickHigh = async (tokenId) => {
    if (highlightedTokens < 2) {
      setHighlightedTokens([...highlightedTokens, tokenId]);
    } else if (highlightedTokens.includes(tokenId)) {
      setHighlightedTokens(highlightedTokens.filter((id) => id !== tokenId));
    }
    if (highlightedTokens.length == 1) {
      setHighlightedTokens([]);
    }
    handleTokenClick(tokenId); // Llamar a la función original para gestionar el clic
    console.log("Tokens resaltados", highlightedTokens);
  };

  const handleCardClickB = async (card) => {
    if (selectedMovement) {
      setSelectedMovement(false);
      return;
    } else {
      setSelectedMovement(true);
      handleCardClick(card);
    }
  };

  const fetchGameInfo = async () => {
    try {
      const response = await fetch(`http://localhost:8000/games/${gameId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        throw new Error("Error al obtener la información de la partida");
      }

      const data = await response.json();
      setminPlayers(data.users.min);
      const validPlayers = data.users.players.filter(
        (player) => player !== null
      );
      setlengthPlayers(validPlayers.length);

      console.log("lengthjugadores:", lengthplayers);
      console.log("MINjugadores:", minplayers);
      const playersFromServer = data.users.players.map((playerObj) => {
        const [userId, userName] = Object.entries(playerObj)[0];
        return { userId: parseInt(userId), userName };
      });

      console.log(
        "Lista de jugadores obtenida de fetchGameInfo:",
        playersFromServer
      );

      setPlayers(playersFromServer); // Actualiza el estado de los jugadores

      if (data.host_id === userId) {
        setIsHost(true);
      }

      if (data.status === "started") {
        sessionStorage.setItem(gameId, true);
        console.log("En started, se seteo como true el gameId:", gameId)
        setGameStarted(sessionStorage.getItem(gameId) === "true");
        console.log("en session se guardo:", sessionStorage.getItem(gameId) )
        console.log("La comparacion dio: ", sessionStorage.getItem(gameId) === "true")
      }

      setGameInfo(data); // Guarda información del juego
    } catch (error) {
      console.log(error);
    }
  };


  useEffect(() => {
    if (sessionStorage.getItem(gameId) === "true") {
      if (sessionStorage.getItem("currentframe") === "list") {
        setTimeLeft(parseInt(sessionStorage.getItem("timer")));
        sessionStorage.setItem("currentframe", false);
      }
      if (sessionStorage.getItem("backmenu") === "true"){
        handlegetTimeLeft();
        sessionStorage.setItem("backmenu", false);
      }
      sessionStorage.getItem(gameId)
      console.log("gamestarted en session es:",sessionStorage.getItem(gameId));
      fetchTurnInfo();
      fetchGameInfo();
      fetchLogs();
      fetchAllFigureCards(players);
      fetchAndSetTokens();
      fetchUserMovementCards().then((cards) => {
        setMovementCards(cards);
      });
      setTokensh([]);
      handleFiguresFetched();
      fetchUserFigureCards(userId);
      setTriggerFetchFigures((prev) => prev + 1);
    } else{
      setGameStarted(sessionStorage.getItem(gameId) === "true");
    }
  }, [gameStarted]);
  

  const fetchTurnInfo = async () => {
    try {

      const response = await fetch(
        `http://localhost:8000/game/${gameId}/turn`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          }
        }
      );

      if (!response.ok) {
        throw new Error("Error al obtener la información de turno");
      }

      const data = await response.json();
      console.log("Llego la data del turno papa:",data)
      setTurnInfo(data);

      const current_turn = data?.actualPlayer_id;
      console.log("Actual Player ID:", current_turn);
      console.log("Actual User ID:", userId);

      if (parseInt(current_turn) == parseInt(userId)) {
        setMyTurn(true);
      } else {
        setMyTurn(false);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handlegetTimeLeft = async () => {

    const get_time = await fetch(`http://localhost:8000/time/${gameId}`,
      {
        method : 'GET',
        headers : {"Content-Type": "application/json"}
      }
    );

    const data = await get_time.json()
    setTimeLeft(data)
  }


  const handleBeforeUnload = (e) => {
    // Guardamos el dato en sessionStorage antes de que se recargue la página
    sessionStorage.setItem("currentframe", 'list');
    sessionStorage.setItem("gameid", gameId);
    
    console.log("la var time es:", timeLeft)
    sessionStorage.setItem("timer", timeLeft - 2);
  };


  window.addEventListener('beforeunload', handleBeforeUnload);




  // Conectar al WebSocket
  const connectWebSocket = async (gameId, userId) => {
    if (!hasConnected.current || ws.current.readyState === WebSocket.CLOSED) {
      console.log("Conectando o reconectando a ws", gameId)
      ws.current = new WebSocket(`ws://localhost:8000/ws/${gameId}/${userId}`);
      hasConnected.current = true; // Marcamos que ya está conectado

      ws.current.onopen = () => {
        console.log("Conectado al WebSocket", userId);
      };
    }
    // Recibir mensajes del servidor
    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log("Mensaje recibido del servidor:", message);

      // Manejar diferentes tipos de mensajes del WebSocket
      switch (message.type) {
        case "status_start":
          if (!gameStarted) {
            console.log("Partida iniciada, obteniendo jugadores y cartas...");
            sessionStorage.setItem(gameId, true);
            console.log("En ws start,se seteo true el gameID es:", gameId)
            setGameStarted(sessionStorage.getItem(gameId) === "true");
            console.log("en session se guardo:", sessionStorage.getItem(gameId) )
            console.log("En ws start, comparacion es:", sessionStorage.getItem(gameId) === "true")

            fetchLogs();
            fetchGameInfo();
            fetchAndSetTokens();
            fetchTurnInfo();
            setTriggerFetchFigures((prev) => prev + 1);
          }
          break;

        case "status_join":
          if (!gameStarted) {
            fetchGameInfo();

          }
          fetchLogs();

          break;

        case "status_used_figure":
          console.log("Figura usada, actualizando estado...");
          fetchTurnInfo();
          fetchAndSetTokens();
          fetchAllFigureCards(players);
          setTokens([]);
          fetchGameInfo();
          fetchLogs();

          setTokensh([]);
          handleFiguresFetched();
          setTriggerFetchFigures((prev) => prev + 1);
          break;

        case "status_move":
          console.log("Movimiento detectado, actualizando fichas...");
          fetchAndSetTokens();
          setTokensh([]);
          fetchLogs();
          handleFiguresFetched();
          setSelectedMovement(false);
          fetchUserMovementCards().then((cards) => {
            setMovementCards(cards);
          });
          setTokensh([]);
          handleFiguresFetched();
          setTriggerFetchFigures((prev) => prev + 1);
          setMoveCount((prev) => prev + 1);

          break;

        case "status_leave":
          console.log("Recibido mensaje status_leave:", message);
          const leavingPlayerId = message.user_left;
          fetchLogs();
          fetchGameInfo();
          fetchTurnInfo();
          setLeaveMessage(
            `Jugador ${leavingPlayerId} ha abandonado la partida`
          );
          setTimeout(() => {
            setLeaveMessage("");
          }, 3000);
          break;

        case "status_winner":
          fetchLogs();
          if (message.user_left != userId) {
            setWinner(message.winner);
          }          
          setWinnerMessage(`¡Ganaste la partida!`);
          sessionStorage.setItem(gameId, false)
          break;

        case "info":
          setGameInfo(message.game_info);
          break;

        case "status_endturn":
          fetchTurnInfo();
          fetchGameInfo();
          fetchLogs();
          fetchAllFigureCards(players);
          fetchAndSetTokens();
          fetchUserMovementCards().then((cards) => {
            setMovementCards(cards);
          });
          setTokensh([]);
          handleFiguresFetched();
          fetchUserFigureCards(userId);
          setTriggerFetchFigures((prev) => prev + 1);
          setMoveCount((prev) => prev + 1);
          setTimeLeft(120); // --> Usar este pasandole el 
          setMoveCount(0);
          setUndoCount(0);
          break;

        case "status_last_movement_undone":
          console.log("Movimiento cancelado, actualizando fichas...");
          fetchAndSetTokens();
          fetchLogs();
          fetchUserMovementCards().then((cards) => {
            setMovementCards(cards);
          });
          break;

        case "status_cancel_game":
          console.log("Host abandono la partida");
          setGameCancel(true);
          break;

        case "chat_message":
          fetchLogs();
          fetchMessages();
          clearUnreadMessages();
          addMessage(message);
          setHasUnreadMessages(true);
          break;

        case "status_reconect":
          console.log("SOY CORDOBES ME GUSTA EL VINO Y LA JODA")
          //sessionStorage.setItem(gameId, true)
          //setGameStarted(sessionStorage.getItem(gameId) === "true")
          /*fetchTurnInfo();
          fetchGameInfo();
          fetchLogs();
          fetchAllFigureCards(players);
          fetchAndSetTokens();
          fetchUserMovementCards().then((cards) => {
            setMovementCards(cards);
          });
          handleFiguresFetched();
          fetchUserFigureCards(userId);  */  
          break;

        default:
          console.warn("Evento no reconocido:", message.type);
          console.log(message);
      }
    };



    // Manejar errores en la conexión WebSocket
    ws.current.onerror = (error) => {
      console.log("Error en el WebSocket:", error);
    };

    // Cerrar la conexión WebSocket
    ws.current.onclose = () => {
      console.log("Conexión WebSocket cerrada");
      hasConnected.current = false; // Permitimos reconexión en caso de cierre
    };
  };

  //------------------logs-----------------------//
  const fetchLogs = async () => {
    try {
      const response = await fetch(`http://localhost:8000/game/${gameId}/logs`);
      if (response.ok) {
        const data = await response.json();
        setLogs(data);
      } else {
        console.error("Failed to fetch logs");
      }
    } catch (error) {
      console.error("Error fetching logs:", error);
    }
  };
  //--------------------------------------------//

  // -----------------Chat-----------------------//
  const addMessage = (newMessage) => {
    if (newMessage.content && newMessage.content.trim() !== "") { // Asegura que el mensaje tenga contenido
      setMessages((prevMessages) => {
        const isDuplicate = prevMessages.some((msg) => msg.id === newMessage.id);
        if (!isDuplicate) {
          return [...prevMessages, newMessage];
        }
        return prevMessages;
      });
    }
  };

  const fetchMessages = async () => {
    try {
      const response = await fetch(`http://localhost:8000/game/${gameId}`);
      if (response.ok) {
        const data = await response.json();
        data.forEach((msg) => addMessage(msg)); // Agrega cada mensaje si aún no está en la lista
      } else {
        console.error("Failed to fetch messages");
      }
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  };
  //------------------------------------------------//

  useEffect(() => {
    if (players.length > 0 && gameStarted) {
      console.log("Players actualizados, obteniendo cartas...");
      fetchAllFigureCards(players); // Llamamos a la función cuando players tiene datos
    }
  }, [players, gameStarted]);

  useEffect(() => {
    fetchGameInfo();
  }, [gameId, userId]);

  const fetchUserMovementCards = async () => {
    console.log("Valores usados en la petición:", { gameId, userId });

    try {
      const response = await fetch(
        `http://localhost:8000/game/${gameId}/${userId}/movements`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          }
        }
      );
      console.log("Respuesta del servidor:", response);

      if (!response.ok) {
        throw new Error("Error al obtener las cartas de movimiento");
      }

      const data = await response.json();
      console.log(
        `Cartas de movimiento recibidas para el jugador ${userId}:`,
        data
      );
      return data.cards || [];
    } catch (error) {
      console.error(error);
      return [];
    }
  };
  // Obtener cartas de los jugadores
  const fetchUserFigureCards = async (userId) => {
    try {
      const response = await fetch(
        `http://localhost:8000/games/${gameId}/${userId}/figure-cards`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          }
        }
      );

      if (!response.ok) {
        throw new Error("Error al obtener las cartas de figura");
      }

      const data = await response.json();
      console.log(`Respuesta completa para el jugador ${userId}:`, data);
      console.log(`Cartas recibidas para el jugador ${userId}:`, data);
      return data.cards || [];
    } catch (error) {
      console.log(error);
      return [];
    }
  };

  // Obtener las cartas de figura de todos los jugadores
  const fetchAllFigureCards = async (playersList) => {
    try {
      const cardsMap = {
        left: [],
        right: [],
        top: [],
        bottom: []
      };
      console.log("Jugadores OBTENIDOS:", playersList);
      const currentPlayerIndex = players.findIndex(
        (player) => player.userId === userId
      );

      console.log(
        "Jugador actual:",
        userId,
        "en la posición",
        currentPlayerIndex
      );

      for (let i = 0; i < reorderedPlayers.length; i++) {
        const player = reorderedPlayers[i];

        if (player != null) {
          const playerUserId = player.userId;
          const cards = await fetchUserFigureCards(playerUserId);
          if (cards.length > 0) {
            console.log(
              `Cartas recibidas para el jugador ${playerUserId}:`,
              cards
            );
            if (i === 0) {
              cardsMap.bottom = cards;
            } else if (i === 1) {
              cardsMap.left = cards;
            } else if (i === 2) {
              cardsMap.right = cards;
            } else if (i === 3) {
              cardsMap.top = cards;
            }
          } else {
            console.log(
              `No se encontraron cartas para el jugador ${playerUserId}`
            );            
          }
        } else {
          console.log(`Posición ${i} no tiene jugador.`);
        }
      }
      console.log("Jugadores ordenados", reorderedPlayers);
      setPlayersReady(true);
      setFigureCards(cardsMap);
      console.log("Cartas mapeadas correctamente:", cardsMap);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    if (!hasConnected.current) {
      connectWebSocket(gameId, userId);
    }
  }, [gameId, userId]);

  useEffect(() => {
    if (gameStarted) {
      fetchUserMovementCards().then((cards) => {
        setMovementCards(cards);
      });
    }
  }, [gameStarted]);

  // Función para abandonar la partida
  const handleLeaveGame = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      sessionStorage.setItem(gameId,false)
      ws.current.send(JSON.stringify({ type: "leave", gameId, userId }));
      handleEndTurn();
      setTimeout(() => {
        ws.current.close();
        onLeaveGame();
      }, 100); // Espera 100 milisegundos
    } else {
      onLeaveGame();
    }
  };
  // Función para iniciar la partida (solo si es el host)
  const handleStartGame = async () => {
    if (isHost && !gameStarted) {
      console.log("Iniciando partida como host...");
     
      sessionStorage.setItem(gameId, true)
      console.log("en session se guardo:", sessionStorage.getItem(gameId) )
      setGameStarted(sessionStorage.getItem(gameId) === "true");
    
      fetchTurnInfo();
      ws.current.send(JSON.stringify({ type: "start", gameId, userId }));
    }
  };
  const fetchAndSetTokens = async () => {
    console.log("Fetching tokens...");

    const tokensData = await fetchGameTokens();

    if (!tokensData || tokensData.length === 0) {
      console.log("No se recibieron fichas del servidor o el array está vacío");
      return;
    }
    console.log("tokensData:", tokensData); // Verifica lo que llega

    const fetchedTokens = tokensData.map((token, index) => {
      const mappedToken = {
        id: token.id,
        color: token.color,
        position: {
          gridRow: token.y_coordinate,
          gridColumn: token.x_coordinate
        }
      };
      console.log("Mapped token:", mappedToken);
      return mappedToken;
    });
    if (tokens.length > 0) {
      console.log("ACTUALIZANDO previousTokens antes de cambiar los tokens");
      setPreviousTokens([...tokens]); // Guarda los tokens actuales antes de actualizarlos
    }
    setTokens([...fetchedTokens]);
    console.log("Tokens state updated:", fetchedTokens);
  };

  useEffect(() => {
    if (tokens.length > 0) {
      console.log("ACTUALIZANDO previousTokens antes de cambiar los tokens");
      setPreviousTokens([...tokens]);
    }
  }, [tokens]);

  useEffect(() => {
    console.log("Tokens state changed:", tokens);
  }, [tokens]);

  const handleEndTurn = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      // Solo enviar si el WebSocket está en estado OPEN
      ws.current.send(JSON.stringify({ type: "endturn", gameId, userId }));
      console.log("Turno finalizado, mensaje enviado.");
      setMyTurn(false);
      fetchGameInfo();
      fetchTurnInfo();
      fetchUserMovementCards().then((cards) => {
        setMovementCards(cards);
      });
      fetchAndSetTokens();
      setTokensh([]);
      handleFiguresFetched();
    } else if (ws.current && ws.current.readyState === WebSocket.CONNECTING) {
      console.log(
        "El WebSocket aún se está conectando. Intenta de nuevo en unos momentos."
      );
    } else {
      console.log(
        "El WebSocket no está disponible. Estado:",
        ws.current ? ws.current.readyState : "desconocido"
      );
    }
  };

  useEffect(() => {
    console.log("TurnInfo:", turnInfo);
    console.log("Es mi turno:", myTurn);
  }, [turnInfo, myTurn]);

  // Función para comparar posiciones de tokens y aplicar la clase de animación si la posición cambió
  const getMovementClass = (token) => {
    if (previousTokens.length === 0) {
      return "";
    }
    const previousToken = previousTokens.find(
      (prevToken) => prevToken.id == token.id
    );

    if (
      previousToken &&
      (previousToken.position.gridRow !== token.position.gridRow ||
        previousToken.position.gridColumn !== token.position.gridColumn)
    ) {
      setTimeout(() => {
        document
          .querySelector(`.token-${token.id}`)
          .classList.remove("token-move");
        document.querySelector(`.token-${token.id}`).offsetWidth; // Fuerza el reflow
        document
          .querySelector(`.token-${token.id}`)
          .classList.add("token-move");
      }, 10);
      return `token-${token.id} token-move`;
    }
    return `token-${token.id}`;
  };

  useEffect(() => {
    let timer;

    if (gameStarted && timeLeft > 0) {
      timer = setTimeout(() => {
        setTimeLeft((prevTimeLeft) => prevTimeLeft - 1);
      }, 1000);
    } else if (timeLeft === 0 && myTurn) {
      handleEndTurn();
    }

    return () => {
      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [timeLeft, gameStarted, myTurn]);

  // Función para abandonar la partida
  const handleLeaveGameAttempt = () => {
    if (myTurn) {
      setWarningMessage(
        "No puedes abandonar la partida hasta que termines tu turno."
      );
      setTimeout(() => {
        setWarningMessage(""); // Limpiar el mensaje después de 3 segundos
      }, 3000);
    } else {
      handleLeaveGame();
    }
  };

  const handleNoLeaveGame = () => {
    setConfirmMessage("¿Deseas volver al menu?");
    sessionStorage.setItem("backmenu", true);
    setConfirm(true);
  };

  const confirmedLeave = () => {
    setConfirm(false);
    onLeaveGame();
  }

  const canceledLeave = () => {
    setConfirm(false);
  }

  // Formatear tiempo
  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs < 10 ? "0" : ""}${secs}`;
  };

  const clearUnreadMessages = () => {
    setHasUnreadMessages(false);
  };

  return (
    <div className="game-page">
      {/* Error al querer bloquear una carta de un jugador bloqueado */}
      {errorMessage && (
        <div className="error-message">
          {errorMessage}
        </div>
      )}
      {/* Botón de chat */}
      <Chat gameId={gameId} fetchMessages={fetchMessages} userId={userId} messages={messages} addMessage={addMessage} hasUnreadMessages={hasUnreadMessages} clearUnreadMessages={clearUnreadMessages} />
      {warningMessage && (
        <div className="warning-message">{warningMessage}</div>
      )}
      <LogComponent
        gameId={gameId}
        logs={logs}
        fetchLogs={fetchLogs}
      />
      {/* Component Figuras para manejar la lógica */}
      <Figuras
        gameId={gameId}
        onFiguresFetched={handleFiguresFetched}
        triggerFetch={triggerFetchFigures}
      />
      {playersReady && (
        <>
          {reorderedPlayers[1] && (
            <div className="player-name-left">
              {reorderedPlayers[1]?.userName || ""}
            </div>
          )}
          {reorderedPlayers[2] && (
            <div className="player-name-right">
              {reorderedPlayers[2]?.userName || ""}
            </div>
          )}
          {reorderedPlayers[3] && (
            <div className="player-name-top">
              {reorderedPlayers[3]?.userName || ""}
            </div>
          )}
        </>
      )}
      {/* Contenedor de la capa oscura y el mensaje "Esperando jugadores" */}
      {!gameStarted  && (
        <div className="overlay">
          {!gameCancel && (
            <div className="waiting-message">
              <h2>Esperando jugadores...</h2>
              {isHost && lengthplayers >= minplayers && (
                <button className="start-game-button" onClick={handleStartGame}>
                  Iniciar Partida
                </button>
              )}
              <button className="leave-button" onClick={handleLeaveGameAttempt}>
                Abandonar Partida
              </button>
            </div>
          )}
        </div>
      )}
      {/* Mostrar mensaje cuando un jugador abandona */}
      {leaveMessage && (
        <div className="leave-notification"> {leaveMessage} </div>
      )}
      {/* Mostrar mensaje de ganador */}
      {(winnerMessage || winner) && (
        <div className="winner-notification">
          {winner ? `El ganador es el usuario "${winner}"` : winnerMessage}
          <button className="ok-button" onClick={handleLeaveGame}>
            OK
          </button>
        </div>
      )}
      {confirm && (
        <div className="confirm-notification">
          <p>{confirmMessage}</p>
          <button className="confirm-button" onClick={confirmedLeave}>
            Aceptar
          </button>
          <button className="cancel-button" onClick={canceledLeave}>
            Cancelar
          </button>
        </div>
      )}
      {gameCancel && (
        <div className="game-cancel">
          {"El host ha cancelado la partida"}
          <button className="ok-button" onClick={handleLeaveGame}>
            OK
          </button>
        </div>
      )}

      {playersReady && (
        <div className="cards">
          {reorderedPlayers[1] && (
            <div className="card-container card-left">
              {figureCards.left.map((card) => (
                <div
                  key={card.id}
                  className={`card-bottomdata ${selectedFigure?.id === card.id ? "selected" : ""
                    }`}
                  onClick={() => handleFigureSelected(card)}>
                  <img src={`./src/designs/${card.blocked ? "Blocked" : card.type}.svg`} />
                </div>
              ))}
            </div>
          )}
          {reorderedPlayers[2] && (
            <div className="card-container card-right">
              {figureCards.right.map((card) => (
                <div
                  key={card.id}
                  className={`card-bottomdata ${selectedFigure?.id === card.id ? "selected" : ""
                    }`}
                  onClick={() => handleFigureSelected(card)}
                >
                  <img
                    src={`./src/designs/${card.blocked ? "Blocked" : card.type
                      }.svg`}
                  />
                </div>
              ))}
            </div>
          )}
          {reorderedPlayers[3] && (
            <div className="card-container card-top">
              {figureCards.top.map((card) => (
                <div
                  key={card.id}
                  className={`card-bottomdata ${selectedFigure?.id === card.id ? "selected" : ""
                    }`}
                  onClick={() => handleFigureSelected(card)}
                >
                  <img
                    src={`./src/designs/${card.blocked ? "Blocked" : card.type
                      }.svg`}
                  />
                </div>
              ))}
            </div>
          )}
          <div className="card-container card-bottom">
            {figureCards.bottom.map((card) => (
              <div
                key={card.id}
                className={`card-bottomdata ${selectedFigure?.id === card.id ? "selected" : ""
                  }`}
                onClick={() => handleFigureSelected(card)}
              >
                <img
                  src={`./src/designs/${card.blocked ? "Blocked" : card.type
                    }.svg`}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card-container card-bottommove">
        {movementCards.length > 0 && (
          <>
            <button
              className="arrow-button"
              onClick={() => setShowAllMovementCards(!showAllMovementCards)}
            >
              {showAllMovementCards ? "▲" : "▼"}
            </button>
            <div className="card-movedata">
              <img
                onClick={() => handleCardClickB(movementCards[0])}
                src={`./src/designs/${movementCards[0].mov_type}.svg`}
                alt={movementCards[0].mov_type}
              />
            </div>
            {showAllMovementCards &&
              movementCards.slice(1).map((card) => (
                <div
                  key={card.id}
                  className="card-movedata"
                  onClick={() => myTurn && handleCardClickB(card)}
                >
                  <img
                    src={`./src/designs/${card.mov_type}.svg`}
                    alt={card.mov_type}
                  />
                </div>
              ))}
          </>
        )}
      </div>
      {/* Tablero */}
      <div
        className={`board-container ${!gameStarted ? "board-disabled" : ""}`}
      >
        {tokens.length > 0
          ? tokens.map((token) => (
            <div
              key={token.id}
              className={`
                token 
                ${token.color} 
                ${getMovementClass(token)} 
                ${isTokenHighlighted(token.id) ? "highlighted" : ""}  ${highlightedTokens.includes(token.id) ? "high" : ""
                } `}
              onClick={() => {
                if (myTurn && selectedMovement) {
                  handleTokenClickHigh(token.id);
                }
                if (myTurn && selectedFigure) {
                  handleUseFigure(token);
                }
              }}
              style={{
                gridColumn: token.position.gridColumn,
                gridRow: token.position.gridRow
              }}
            />
          ))
          : gameStarted}
      </div>

      {/* Información del turno y cartas */}
      <div className="info-container">
        {gameStarted && turnInfo && Object.keys(turnInfo).length > 0 && (
          <div className="turn-info">
            <h2>Informacion de Turno</h2>
            <p>Tiempo restante: {formatTime(timeLeft)}</p>
            <p>
              Color Bloqueado:{" "}
              {turnInfo.forbiddenColor
                ? `${turnInfo.forbiddenColor}`
                : "Ninguno"}{" "}
            </p>
            <p>
              Jugador Activo:{" "}
              {myTurn
                ? "Tu turno"
                : turnInfo?.actualPlayer_id
                  ? `${turnInfo.actualPlayer_name}`
                  : "Desconocido"}
            </p>
            <p>
              Siguiente Jugador:{" "}
              {turnInfo.nextPlayer_name
                ? `${turnInfo.nextPlayer_name}`
                : "Desconocido"}
            </p>
          </div>
        )}

        {myTurn && (
          <button
            className="cancel-move-button"
            onClick={() => {
              handleUndoMove(gameId, userId);
              setUndoCount((prev) => prev + 1);
            }}
            disabled={!myTurn || moveCount <= undoCount} // Habilitado solo si es el turno del jugador
          >
            ⟲
          </button>
        )}

        <button className="leave-button" onClick={handleLeaveGameAttempt}>
          Abandonar Partida
        </button>
        {gameStarted && (
          <button className="noleave-button" onClick={handleNoLeaveGame}>
            Volver a Menu
          </button>
        )}
        {myTurn && (
          <button
            className="turno-finalizado"
            disabled={!gameStarted || !myTurn}
            onClick={handleEndTurn}
          >
            Finalizar Turno
          </button>
        )}
      </div>
    </div>
  );
};

export default BoardPage;
