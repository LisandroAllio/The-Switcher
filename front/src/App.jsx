import React, { useState, useEffect } from 'react';
import ButtonsPage from './components/buttonspage';
import ListGames from './components/listgames';
import CreateFormPage from './components/createformpage';
import SuccessPage from './components/successpage';
import BoardPage from './components/board';
import './App.css';
import './components/buttons.css';
import './components/form.css';
import './components/list.css';
import './components/board.css'; 
import './components/successpage.css'; 

function App() {
  const [gameId, setGameId] = useState(null); // Almacena el gameId
  const [userId, setUserId] = useState(null);
  const [currentFrame, setCurrentFrame] = useState('initial');  // Controla en qué "frame" estamos
  const [fade, setFade] = useState(false); 

  useEffect(() => {
    let initialTimer, transitionTimer, boardTimer;
  
    if (sessionStorage.getItem("currentframe") === 'list'){
      handleListGames();
    }

    if (currentFrame === 'initial') {
      initialTimer = setTimeout(() => {
        setFade(true);  // Inicia el fade de frame4
        transitionTimer = setTimeout(() => {
          setCurrentFrame('buttons');  // Cambia al frame de botones
          setFade(false);  // Termina el fade
        }, 1000);  // Espera 1 segundo para la transición de fade
      }, 2500);  // Espera 2.5 segundos antes de iniciar la transición
  
    } else if (currentFrame === 'success') {
      boardTimer = setTimeout(() => {
        setCurrentFrame('board');  
      }, 3000);  
  
    } else if (currentFrame === 'board') {
      setFade(false);  
    }
    return () => {
      clearTimeout(initialTimer);
      clearTimeout(transitionTimer);
      clearTimeout(boardTimer);
    };
  }, [currentFrame]); 
    
  // Función para cambiar al frame del formulario
  const handleCreateGame = () => {
    setCurrentFrame('form');
  };

  const handleListGames = () => {
    setCurrentFrame('list');
  };

  const handleGoBack = () => {
    setCurrentFrame('buttons');  // Volver al frame de los botones
  };

  const handleGameCreated = (gameId, userId) => {
    setGameId(gameId); // Almacenar el gameId recibido
    setUserId(userId); // Almacenar el UserID recibido
    setCurrentFrame('success');  // Cambia al frame de éxito cuando la partida ha sido creada
  };

  const handleGoToBoard = (userId, gameId) => {
    setUserId(userId);
    setGameId(gameId);
    setCurrentFrame('board');  // Cambia al frame del tablero después del éxito
  };

  const handleLeaveGame = () => {
    setCurrentFrame('buttons');  // Abandonar partida y volver al menú
  };

  return (
<div className={`App ${currentFrame === 'initial' ? 'frame4' : currentFrame === 'board' ? 'frame-board' : 'frame0'} ${fade ? 'fade-out' : 'fade-in'}`}>    
     {currentFrame === 'buttons' && (
        <ButtonsPage onCreateGame={handleCreateGame} 
          onListGames={handleListGames} />
      )}
      {currentFrame === 'form' && (
        <CreateFormPage onGoBack={handleGoBack} onGameCreated={handleGameCreated} />
      )}
      {currentFrame === 'list' && (
        <ListGames onBack={handleGoBack} onJoinGame={handleGoToBoard} />
      )}
      {currentFrame === 'success' && (
        <SuccessPage gameId={gameId} userId={userId} onGoToBoard={handleGoToBoard} /> 
      )}
      {currentFrame === 'board' && (
        <BoardPage gameId={gameId} userId={userId} onLeaveGame={handleLeaveGame} />
      )}
    </div>
  );
}

export default App;
