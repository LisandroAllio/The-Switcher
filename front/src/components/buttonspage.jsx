import React, { useEffect, useState } from "react";

const ButtonsPage = ({ onCreateGame, onListGames}) => {
  const [isFirstVisit, setIsFirstVisit] = useState(true);

  const handleSessionID = async () => {
    try {
      if (isFirstVisit) {
        console.log("Estoy en casa")
        const response = await fetch(`http://localhost:8000/get_session_id`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          }
        });
        
        const data = await response.json();
        const sessionID = data.session_id
        setIsFirstVisit(false);
        console.log("ID Sesion:", sessionID);
        sessionStorage.setItem('sessionID', sessionID);
      }
    } finally {
    }
  };

  useEffect(() => {
    const firstVisit = sessionStorage.getItem('firstVisit');
    console.log("Llegue mama");

    if (!firstVisit) {
      setIsFirstVisit(true);
      console.log("Llegue papa");
      sessionStorage.setItem('firstVisit', 'true');
      handleSessionID();
    }
  });

  return (
    <div className="buttons-container">
      <button className="custom-button" onClick={onCreateGame}>
        Crear Partida
      </button>
      <button className="custom-button" onClick={onListGames}>
        Listar Partidas
      </button>
    </div>
  );
};

export default ButtonsPage;
