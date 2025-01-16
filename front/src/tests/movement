import { renderHook, act } from '@testing-library/react-hooks';
import { waitFor } from '@testing-library/react'; // Importar waitFor de @testing-library/react
import { vi } from 'vitest';
import Movement from '/src/components/movement';

describe('Movement component tests', () => {
     const gameId = 'test-game-id';
     const userId = 'test-user-id';

     beforeEach(() => {
          vi.clearAllMocks();

          global.fetch = vi.fn(() =>
               Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({
                         tokens: [
                              { id: 1, y_coordinate: 1, x_coordinate: 1, color: 'RED' },
                              { id: 2, y_coordinate: 2, x_coordinate: 2, color: 'BLUE' },
                         ],
                    }),
               })
          );

          // Mock para `console.error` para capturar y verificar errores
          vi.spyOn(console, 'error').mockImplementation(() => { });
     });

     afterEach(() => {
          vi.restoreAllMocks();
     });

     it('should fetch game tokens on mount', async () => {
          const { result } = renderHook(() => Movement({ gameId, userId }));

          // Llamar a la función fetchGameTokens para obtener las fichas del servidor
          await act(async () => {
               await result.current.fetchGameTokens();
          });

          await waitFor(() => {
               // Asegúrate de que se llama a fetch
               expect(global.fetch).toHaveBeenCalledWith(`http://localhost:8000/game/${gameId}/tokens`, {
                    method: 'GET',
                    headers: {
                         'Content-Type': 'application/json',
                    },
               });
          });

          // Verificar que las fichas se guardaron correctamente en el estado
          expect(result.current.tokens).toEqual([
               { id: 1, y_coordinate: 1, x_coordinate: 1, color: 'RED' },
               { id: 2, y_coordinate: 2, x_coordinate: 2, color: 'BLUE' },
          ]);
     });

     it('should handle card and token selection correctly', () => {
          const { result } = renderHook(() => Movement({ gameId, userId }));

          // Simular la selección de una carta
          act(() => {
               result.current.handleCardClick({ card_id: 1 });
          });

          // Verificar que la carta fue seleccionada
          expect(result.current.selectedCard).toEqual({ card_id: 1 });

          // Simular la selección de un token
          act(() => {
               result.current.handleTokenClick(1);
          });

          // Verificar que el primer token fue seleccionado
          expect(result.current.selectedTokens).toEqual([1]);

          // Simular la selección de un segundo token
          act(() => {
               result.current.handleTokenClick(2);
          });

          // Verificar que ambos tokens fueron seleccionados
          expect(result.current.selectedTokens).toEqual([1, 2]);
     });

     it('should handle move execution when two tokens are selected', async () => {
          global.fetch = vi.fn(() =>
               Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ success: true }),
               })
          );

          const { result } = renderHook(() => Movement({ gameId, userId }));

          // Simular la selección de una carta
          act(() => {
               result.current.handleCardClick({ card_id: 1 });
          });

          // Simular la selección del primer token
          act(() => {
               result.current.handleTokenClick(1); // Selecciona el primer token
          });

          // Esperar que el primer token esté seleccionado
          await waitFor(() => {
               expect(result.current.selectedTokens).toEqual([1]);
          });

          // Simular la selección del segundo token
          act(() => {
               result.current.handleTokenClick(2); // Selecciona el segundo token
          });

          // Verificar que después de seleccionar el segundo token, `executeMove` se llama
          await waitFor(() => {
               expect(global.fetch).toHaveBeenCalledWith(`http://localhost:8000/game/${gameId}/move`, {
                    method: 'PUT',
                    headers: {
                         'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                         game_id: gameId,
                         player_id: userId,
                         move_id: 1,  // ID de la carta seleccionada
                         token1_id: 1,  // Primer token seleccionado
                         token2_id: 2,  // Segundo token seleccionado
                    }),
               });
          });

          // Verificar que las selecciones se resetean después de un movimiento exitoso
          expect(result.current.selectedCard).toBeNull();
          expect(result.current.selectedTokens).toEqual([]);
     });



     it('should handle errors when fetching game tokens fails', async () => {
          // Mock de fetch que simula un error
          global.fetch = vi.fn(() =>
               Promise.resolve({
                    ok: false,
                    json: () => Promise.resolve({ detail: 'Error al obtener las fichas' }),
               })
          );

          const { result } = renderHook(() => Movement({ gameId, userId }));

          // Llamar a fetchGameTokens y verificar que captura el error
          await act(async () => {
               await result.current.fetchGameTokens();
          });

          // Verificar que se ha registrado el error
          expect(console.error).toHaveBeenCalledWith('Error al obtener las fichas del juego:', 'Error al obtener las fichas');
     });
});
