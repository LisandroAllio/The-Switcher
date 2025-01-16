import { useEffect, useRef } from 'react';

const useWebSocket = (url, onMessage) => {
  const socket = useRef(null);

  useEffect(() => {
    // Conectar al WebSocket solo una vez
    socket.current = new WebSocket(url);

    // Manejar los mensajes recibidos
    socket.current.onmessage = (event) => {
      const data = event.data;
      onMessage(data);  // Pasar el mensaje al callback
    };

    // Cerrar la conexión al desmontar el componente
    return () => {
      if (socket.current) {
        socket.current.close();
      }
    };
  }, [url, onMessage]);  // Solo se ejecuta cuando la URL o el callback cambian

  // Función para enviar un mensaje al WebSocket
  const sendMessage = (message) => {
    if (socket.current && socket.current.readyState === WebSocket.OPEN) {
      socket.current.send(message);
    } else {
      console.error("WebSocket no está conectado.");
    }
  };

  return { sendMessage };
};

export default useWebSocket;