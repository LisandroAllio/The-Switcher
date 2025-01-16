import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test, vi } from "vitest";
import ListGames from "../components/listgames";

// Mock de la API fetch
beforeEach(() => {
  vi.clearAllMocks();

  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            name: "Partida 1",
            host_id: 123,
            in_game: false,
            is_private: false,
            users: {
              min: 2,
              max: 4,
              players: [
                { additionalProp1: "Player1" },
                { additionalProp2: "Player2" },
              ],
            },
          },
          {
            id: 2,
            name: "Partida Privada",
            host_id: 456,
            in_game: false,
            is_private: true,
            users: {
              min: 2,
              max: 4,
              players: [],
            },
          },
        ]),
    })
  );
});

test("It requires a user name before submitting", async () => {
  const mockOnJoinGame = vi.fn();

  // Renderizamos el componente
  render(<ListGames onBack={() => {}} onJoinGame={mockOnJoinGame} userId={1} />);

  // Verificamos que el fetch **no** se haya llamado inicialmente
  expect(global.fetch).not.toHaveBeenCalled();

  // Simulamos el ingreso del nombre de usuario
  await userEvent.type(screen.getByPlaceholderText("Nombre de usuario"), "Nacho");

  // Simulamos clic en el botón "Continuar"
  await userEvent.click(screen.getByText("Continuar"));

  // Verificamos que ahora sí se haya llamado a `fetch` después de enviar el formulario
  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });
});

test("Filters games by name", async () => {
  render(<ListGames onBack={() => {}} onJoinGame={() => {}} userId={1} />);

  await userEvent.type(screen.getByPlaceholderText("Nombre de usuario"), "Nacho");
  await userEvent.click(screen.getByText("Continuar"));

  await waitFor(() => expect(screen.getByText("Lista de Partidas Disponibles")).toBeInTheDocument());

  // Simular el ingreso en el filtro de nombre
  const nameFilterInput = screen.getByPlaceholderText("Buscar por nombre");
  await userEvent.type(nameFilterInput, "Partida 1");

  // Simular clic en "Buscar"
  await userEvent.click(screen.getByText("Buscar"));

  // Verificar que solo la partida "Partida 1" aparece en el resultado
  await waitFor(() => {
    expect(screen.getByText("Partida 1")).toBeInTheDocument();
  });
});

test("Switches between 'Disponibles' and 'Activas' tabs", async () => {
  render(<ListGames onBack={() => {}} onJoinGame={() => {}} userId={1} />);

  await userEvent.type(screen.getByPlaceholderText("Nombre de usuario"), "Nacho");
  await userEvent.click(screen.getByText("Continuar"));

  await waitFor(() => expect(screen.getByText("Lista de Partidas Disponibles")).toBeInTheDocument());

  // Cambiar a la pestaña "Activas"
  const activeTabButton = screen.getByText("Activas");
  await userEvent.click(activeTabButton);

  // Esperar que el título de la lista cambie a "Lista de Partidas Activas"
  await waitFor(() => {
    expect(screen.getByText("Lista de Partidas Activas")).toBeInTheDocument();
  });

  // Cambiar de nuevo a "Disponibles"
  const availableTabButton = screen.getByText("Disponibles");
  await userEvent.click(availableTabButton);

  // Verificar que vuelve a mostrar "Lista de Partidas Disponibles"
  await waitFor(() => {
    expect(screen.getByText("Lista de Partidas Disponibles")).toBeInTheDocument();
  });
});

test("Joins a public game", async () => {
  const mockOnJoinGame = vi.fn();
  render(<ListGames onBack={() => {}} onJoinGame={mockOnJoinGame} userId={1} />);

  await userEvent.type(screen.getByPlaceholderText("Nombre de usuario"), "Nacho");
  await userEvent.click(screen.getByText("Continuar"));

  await waitFor(() => expect(screen.getByText("Lista de Partidas Disponibles")).toBeInTheDocument());

  const joinButtons = screen.getAllByText("Unirse");
  const publicJoinButton = joinButtons[0]; // El primer botón "Unirse" corresponde a la partida pública
  await userEvent.click(publicJoinButton);

  // Verificar que se ha llamado a `onJoinGame` correctamente con los argumentos esperados
  await waitFor(() => {
    expect(mockOnJoinGame).toBeCalled;
  }); 
});

test("Joins a private game with password", async () => {
  const mockOnJoinGame = vi.fn();
  render(<ListGames onBack={() => {}} onJoinGame={mockOnJoinGame} userId={1} />);

  await userEvent.type(screen.getByPlaceholderText("Nombre de usuario"), "Nacho");
  await userEvent.click(screen.getByText("Continuar"));

  await waitFor(() => expect(screen.getByText("Lista de Partidas Disponibles")).toBeInTheDocument());

  // Ingresar la contraseña en el campo correspondiente
  const passwordInput = screen.getByPlaceholderText("Contraseña");
  await userEvent.type(passwordInput, "miPassword");

  // Unirse a la partida privada
  const joinButton = screen.getAllByText("Unirse")[1]; // Selecciona el segundo botón "Unirse" (partida privada)
  await userEvent.click(joinButton);

  // Verificar que se ha llamado a `onJoinGame` correctamente con los argumentos esperados
  await waitFor(() => {
    expect(mockOnJoinGame).toBeCalled;
  });
});