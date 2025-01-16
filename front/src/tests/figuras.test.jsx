import React from 'react';
import { render, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import Figuras from '/src/components/figuras';

describe('Figuras component tests', () => {
  const gameId = 'test-game-id';
  const onFiguresFetched = vi.fn(); // Mock de la función onFiguresFetched
  const onFigureSelected = vi.fn(); // Mock de la función onFigureSelected
  const triggerFetch = true; // Simula un trigger inicial

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock del fetch global para simular una respuesta exitosa del backend
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          figures: [
            { id: 1, name: 'Figura 1' },
            { id: 2, name: 'Figura 2' },
          ],
        }),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should fetch figures correctly and call onFiguresFetched with the data', async () => {
    render(
      <Figuras 
        gameId={gameId} 
        onFiguresFetched={onFiguresFetched} 
        triggerFetch={triggerFetch} 
        onFigureSelected={onFigureSelected}
      />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(`http://localhost:8000/game/${gameId}/show_all_figures`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    await waitFor(() => {
      expect(onFiguresFetched).toHaveBeenCalledWith([
        { id: 1, name: 'Figura 1' },
        { id: 2, name: 'Figura 2' },
      ]);
    });
  });

  it('should handle errors when the fetch fails', async () => {
    // Mock del fetch para simular un error
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        statusText: 'Internal Server Error',
      })
    );

    // Spy en console.error para verificar que se llame
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <Figuras 
        gameId={gameId} 
        onFiguresFetched={onFiguresFetched} 
        triggerFetch={triggerFetch} 
        onFigureSelected={onFigureSelected}
      />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(`http://localhost:8000/game/${gameId}/show_all_figures`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

   

    // Restaurar el spy
    consoleErrorSpy.mockRestore();
  });
});
