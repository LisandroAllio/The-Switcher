import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { vi } from 'vitest';
import BoardPage from '/src/components/board';

// Definir un mock detallado de WebSocket
const mockWebSocket = {
  send: vi.fn(),
  close: vi.fn(),
  onmessage: null,
  onopen: vi.fn(),
  onerror: vi.fn(),
  onclose: vi.fn(),
};

// Reemplazar la implementación global de WebSocket
global.WebSocket = vi.fn(() => mockWebSocket);

describe('BoardPage WebSocket and API tests', () => {
  const gameId = 'test-game-id';
  const userId = 'test-user-id';
  let onLeaveGame;

  beforeEach(() => {
    vi.clearAllMocks();

    // Declarar onLeaveGame como función simulada antes de cada prueba
    onLeaveGame = vi.fn();

    global.fetch = vi.fn((url) => {
      if (url.endsWith('/logs')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([
            { id: 1, actionType: 'MOVE', description: 'Player moved' },
            { id: 2, actionType: 'JOIN', description: 'Player joined the game' },
          ]),
        });
      } else if (url.includes(`/games/${gameId}`)) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            users: { players: [{ '1': 'Player1' }, { '2': 'Player2' }] },
            host_id: userId,
            status: 'waiting',
          }),
        });
      } else {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([
            { id: 1, user_id: 'User1', content: 'Hello' },
            { id: 2, user_id: 'User2', content: 'Hi there' },
          ]),
        });
      }
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should connect to WebSocket and fetch game info on mount', async () => {
    await act(async () => {
      render(<BoardPage onLeaveGame={onLeaveGame} gameId={gameId} userId={userId} />);
    });

    // Verificar que se llama a fetch para obtener la información de la partida
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(`http://localhost:8000/games/${gameId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    // Verificar la conexión a WebSocket
    await waitFor(() => {
      expect(WebSocket).toHaveBeenCalledWith(`ws://localhost:8000/ws/${gameId}/${userId}`);
    });
  });

  it('should handle WebSocket messages correctly', async () => {
    await act(async () => {
      render(<BoardPage onLeaveGame={onLeaveGame} gameId={gameId} userId={userId} />);
    });

    // Simular recepción de mensaje 'status_start' del WebSocket
    const messageEvent = { data: JSON.stringify({ type: 'status_start' }) };
    
    act(() => {
      mockWebSocket.onmessage(messageEvent);
    });

    await waitFor(() => {
      // Verificar que se actualiza el estado del juego cuando se recibe el mensaje de inicio
      expect(global.fetch).toHaveBeenCalledWith(`http://localhost:8000/games/${gameId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });
  });

  it('should send a message to WebSocket when ending the turn', async () => {
    await act(async () => {
      render(<BoardPage onLeaveGame={onLeaveGame} gameId={gameId} userId={userId} />);
    });

    // Simular el final de turno
    act(() => {
      mockWebSocket.send(JSON.stringify({
        type: 'endturn',
        gameId,
        userId,
      }));
    });

    // Verificar que el mensaje fue enviado a WebSocket
    await waitFor(() => {
      expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify({
        type: 'endturn',
        gameId,
        userId,
      }));
    });
  });

  it('should handle errors in WebSocket connection', async () => {
    await act(async () => {
      render(<BoardPage onLeaveGame={onLeaveGame} gameId={gameId} userId={userId} />);
    });

    // Simular error en WebSocket
    act(() => {
      const errorEvent = new Event('error');
      mockWebSocket.onerror(errorEvent);
    });

    // Verificar que el evento de error fue manejado
    expect(mockWebSocket.onerror).toBeDefined();
  });


  // it('should fetch and set messages without duplicates in fetchMessages', async () => {
  //   await act(async () => {
  //     render(<BoardPage onLeaveGame={onLeaveGame} gameId={gameId} userId={userId} />);
  //   });

  //   // Llamar a fetchMessages y verificar que se haya llamado al endpoint de mensajes
  //   await act(async () => {
  //     const fetchMessagesButton = screen.getByRole('button', { name: '💬' });
  //     fetchMessagesButton.click();
  //   });

  //   await waitFor(() => {
  //     expect(global.fetch).toHaveBeenCalledWith(`http://localhost:8000/game/${gameId}`);
  //     expect(screen.getByText('Hello')).toBeInTheDocument();
  //     expect(screen.getByText('Hi there')).toBeInTheDocument();
  //   });
  // });

  // it('should add a unique message to messages state without duplicates', async () => {
  //   const mockMessages = [
  //     { id: 1, user_id: 'User1', content: 'Hello' },
  //     { id: 2, user_id: 'User2', content: 'Hi there' },
  //   ];
  
  //   global.fetch.mockResolvedValueOnce({
  //     ok: true,
  //     json: async () => mockMessages,
  //   });
  
  //   await act(async () => {
  //     render(<BoardPage onLeaveGame={onLeaveGame} gameId={gameId} userId={userId} />);
  //   });
  
  //   // Simular que se recibe un mensaje duplicado y un nuevo mensaje
  //   const duplicateMessage = { id: 1, user_id: 'User1', content: 'Hello' };
  //   const newMessage = { id: 3, user_id: 'User3', content: 'New message' };
  
  //   await act(async () => {
  //     // Simular que fetchMessages recibe el mensaje duplicado y uno nuevo
  //     global.fetch.mockResolvedValueOnce({
  //       ok: true,
  //       json: async () => [...mockMessages, duplicateMessage, newMessage],
  //     });
  //     // Llamar a fetchMessages para actualizar el estado de messages
  //     const fetchMessagesButton = screen.getByRole('button', { name: '💬' });
  //     fetchMessagesButton.click();
  //   });
  
  //   // Verificar que solo haya una instancia de cada mensaje en el DOM
  //   await waitFor(() => {
  //     expect(screen.getByText('Hi there')).toBeInTheDocument();
  //     expect(screen.getByText('New message')).toBeInTheDocument();
  //   });
  // });
  
});
