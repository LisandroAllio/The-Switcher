import React, { useEffect, useState } from 'react';

const Figuras = ({ gameId, onFiguresFetched, triggerFetch }) => {
  const [error, setError] = useState(null);
  const [figures, setFigures] = useState([]);

  // Función para obtener todas las figuras desde el backend
  const fetchFigures = async () => {
    try {
      const response = await fetch(`http://localhost:8000/game/${gameId}/show_all_figures`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      setFigures(data.figures || []);  // Guardamos las figuras en el estado
      onFiguresFetched(data.figures || []);  // Pasamos las figuras obtenidas al padre (Board)
      console.log('FIGURAS OBTENIDAS');
    } catch (err) {
      setError(err.message);
      console.log('Error al obtener las figuras:', err);
    }
  };

  // Función para usar una carta figura
  
  // Se ejecuta cuando el componente es montado o cuando triggerFetch cambia
  useEffect(() => {
    fetchFigures();
  }, [gameId, triggerFetch]);

  return null
};

export default Figuras;
