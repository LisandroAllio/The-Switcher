import React, { useEffect } from 'react';
import './successpage.css'
const SuccessPage = ({ onGoToBoard, userId, gameId }) => {
  useEffect(() => {
    // Después de 3 segundos, ir a la página del tablero
    const timer = setTimeout(() => {
      onGoToBoard(userId, gameId);
    }, 3000);

    return () => clearTimeout(timer);  // Limpia el temporizador al desmontar
  }, [onGoToBoard]);

  return (
    <div className="success-container">
    <div className="success-message-box">
      <h1>¡Partida Creada con Éxito!</h1>
      <p>Redirigiendo al tablero en 3 segundos...</p>
    </div>
  </div>
  );
};

export default SuccessPage;