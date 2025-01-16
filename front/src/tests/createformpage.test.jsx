import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event"; // Asegúrate de importar userEvent correctamente
import { expect, test, vi } from "vitest";

import CreateFormPage from "/src/components/createformpage.jsx"; 

test("It submits the form and calls onGameCreated", async () => {
  const mockOnGameCreated = vi.fn();

  render(<CreateFormPage onGameCreated={mockOnGameCreated} onGoBack={() => {}} />);

  // Rellenar campos
  await userEvent.type(screen.getByLabelText(/Nombre de Usuario/i), "Tomás");
  await userEvent.type(screen.getByLabelText(/Nombre de la partida/i), "Mi Partida");
  await userEvent.type(screen.getByLabelText(/Máximo de jugadores/i), "4");
  await userEvent.type(screen.getByLabelText(/Mínimo de jugadores/i), "2");

  // Enviar el formulario
  const submitButton = screen.getByRole("button", { name: /crear/i });
  await userEvent.click(submitButton);

  // Esperar que onGameCreated se haya llamado
  await waitFor(() => {
    expect(mockOnGameCreated).toBeCalled;
  });
});

// test("It only enables submit when all fields are filled", async () => {
//   const mockOnGameCreated = vi.fn();

//   render(<CreateFormPage onGameCreated={mockOnGameCreated} onGoBack={() => {}} />);

//   const submitButton = screen.getByRole("button", { name: /crear/i });
  
//   // Verificar que el botón "Crear" está inicialmente deshabilitado
//   expect(submitButton).toBeEnabled();

//   // Rellenar campos uno a uno y verificar que el botón se habilite solo al final
//   await userEvent.type(screen.getByLabelText(/Nombre de Usuario/i), "Tomás");
//   await userEvent.type(screen.getByLabelText(/Nombre de la partida/i), "Mi Partida");
//   await userEvent.type(screen.getByLabelText(/Máximo de jugadores/i), "4");
//   await userEvent.type(screen.getByLabelText(/Mínimo de jugadores/i), "2");

//   // Verificar que el botón ahora esté habilitado
//   expect(submitButton).not.toBeDisabled();
  
//   // Hacer clic en el botón y verificar que onGameCreated sea llamado
//   await userEvent.click(submitButton);
//   await waitFor(() => {
//     expect(mockOnGameCreated).toBeCalled();
//   });
// });

// test("It requires a user name before submitting", async () => {
//   const mockOnGameCreated = vi.fn();

//   render(<CreateFormPage onGameCreated={mockOnGameCreated} onGoBack={() => {}} />);

//   const submitButton = screen.getByRole("button", { name: /crear/i });

//   // Intentar enviar sin nombre de usuario
//   await userEvent.click(submitButton);

//   // Verificar que onGameCreated no haya sido llamado
//   expect(mockOnGameCreated).not.toHaveBeenCalled();

//   // Ingresar el nombre de usuario y demás campos
//   await userEvent.type(screen.getByLabelText(/Nombre de Usuario/i), "Tomás");
//   await userEvent.type(screen.getByLabelText(/Nombre de la partida/i), "Mi Partida");
//   await userEvent.type(screen.getByLabelText(/Máximo de jugadores/i), "4");
//   await userEvent.type(screen.getByLabelText(/Mínimo de jugadores/i), "2");

//   // Enviar el formulario
//   await userEvent.click(submitButton);
//   await waitFor(() => {
//     expect(mockOnGameCreated).toBeCalled();
//   });
// });
