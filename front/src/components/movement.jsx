import React, { useState, useEffect, useRef } from 'react';

const Movement = ({ gameId, userId, movementCards, onMoveCompleted }) => {
  const [selectedCard, setSelectedCard] = useState(null);
  const [selectedTokens, setSelectedTokens] = useState([]);
  const [tokens, setTokens] = useState([]); // Estado actual de las fichas
  // const [previousTokens, setPreviousTokens] = useState([]); // Estado anterior de las fichas
  const ws = useRef(null); // Referencia del WebSocket
  const hasConnected = useRef(false); // Evita múltiples conexiones WebSocket

// Funcion que actualiza el tablero cada vez que hay un movimiento o recibe el tablero inicial
  const fetchGameTokens = async () => {
    try {
      const response = await fetch(`http://localhost:8000/game/${gameId}/tokens`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error al obtener las fichas del juego:', errorData.detail);
        throw new Error(errorData.detail || 'Error al obtener las fichas del juego');
      }

      const data = await response.json();
      console.log('Tokens recibidos del servidor:', data);
      setTokens(data.tokens || []);
      return data.tokens || [];
    } catch (error) {
      console.error(error);
      return [];
    }
  };

  const handleUndoMove = async (gameId, playerId) => {
    try {
      const response = await fetch(`http://localhost:8000/game/${gameId}/undo_last_movement`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          game_id: gameId,
          player_id: playerId,
        }),
      });

      if (response.status === 404) {
        // Si es un 404, significa que no es valido el movimiento.
        console.warn('Ultimo movimiento no encontrado.');
        return;  // Salimos del bloque para no lanzar un error
      }

      if (!response.ok) {
        throw new Error('Error al cancelar el último movimiento');
      }

      const data = await response.json();
      console.log('Último movimiento cancelado:', data);
    } catch (error) {
      console.error('Error al cancelar el último movimiento:', error);
    }
  };

  // Función para seleccionar una carta de movimiento
  const handleCardClick = (card) => {
    if (parseInt(selectedTokens.length) == 0) {
      setSelectedCard(card); // Seleccionamos la carta
      console.log('Carta seleccionada:', card);
    } else {
      console.log('Deselecciona token o termina movimiento');
      //algo que diga que primero deseleccione tokens o termine el movimiento
    }
  };

  const handleTokenClick = (tokenId) => {
    if (!selectedCard) {
      console.log('No hay carta seleccionada');
      return;
    }
  
    if (selectedTokens.includes(tokenId)) {
      console.log('Deseleccionando token', tokenId);
      setSelectedTokens((prev) => prev.filter((id) => id !== tokenId));
      return;
    }
  
    if (selectedTokens.length === 0) {
      console.log('Token seleccionado:', tokenId);
      setSelectedTokens([tokenId]); // Seleccionar el primer token
      return;
    }
  
    if (selectedTokens.length === 1) {
      console.log('Token seleccionado:', tokenId);
      setSelectedTokens((prev) => [...prev, tokenId]); // Seleccionar el segundo token
  
      // Ejecutar el movimiento cuando haya dos tokens seleccionados
      executeMove(selectedCard.card_id, selectedTokens[0], tokenId);
    }
  };
  
  // Función para ejecutar el movimiento
  const executeMove = async (moveId, token1Id, token2Id) => {
    try {
      const response = await fetch(`http://localhost:8000/game/${gameId}/move`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          game_id: gameId,
          player_id: userId,
          move_id: moveId,
          token1_id: token1Id,
          token2_id: token2Id,
        }),
      });

      if (response.status === 400) {
        // Si es un 404, significa que no es valido el movimiento.
        console.warn('Movimiento invalido.');
        setSelectedCard(null);
        setSelectedTokens([]);
        return;  // Salimos del bloque para no lanzar un error
      }

      if (!response.ok) {
        throw new Error('Error al ejecutar el movimiento');
      }

      const data = await response.json();
      console.log('Movimiento ejecutado con éxito:', data);
      setSelectedCard(null);
      setSelectedTokens([]);
    } catch (error) {
      console.error('Error al ejecutar el movimiento:', error);
    }
    setSelectedCard(null);
    setSelectedTokens([]);
  };

  return {
    handleCardClick,
    handleTokenClick,
    tokens,
    selectedCard,
    selectedTokens,
    fetchGameTokens,
    handleUndoMove,
  };
};

export default Movement;
