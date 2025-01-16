import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import Chat from "/src/components/chat.jsx";

describe("Chat Component", () => {
  const mockFetchMessages = vi.fn();
  const mockAddMessage = vi.fn();
  const mockClearUnreadMessages = vi.fn();

  const mockMessages = [
    { id: 1, name: "User1", content: "Hello" },
    { id: 2, name: "User2", content: "Hi there" },
  ];

  const defaultProps = {
    gameId: 1,
    userId: "User1",
    messages: mockMessages,
    fetchMessages: mockFetchMessages,
    addMessage: mockAddMessage,
    hasUnreadMessages: true,
    clearUnreadMessages: mockClearUnreadMessages,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });


  // it("calls fetchMessages and clearUnreadMessages when opening chat", () => {
  //   render(<Chat {...defaultProps} />);
  //   const toggleButton = screen.getByRole("button", { name: "💬" });

  //   // Open chat
  //   fireEvent.click(toggleButton);

  //   expect(mockFetchMessages).toBeCalled();
  //   expect(mockClearUnreadMessages).toBeCalled();
  // });

  it("displays messages passed as props", () => {
    render(<Chat {...defaultProps} />);
    fireEvent.click(screen.getByRole("button", { name: "💬" }));

    expect(screen.getByText("User1:")).toBeInTheDocument();
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("User2:")).toBeInTheDocument();
    expect(screen.getByText("Hi there")).toBeInTheDocument();
  });

  // it("calls the sendMessage function when clicking Enviar", async () => {
  //   render(<Chat {...defaultProps} />);
  //   fireEvent.click(screen.getByRole("button", { name: "💬" }));

  //   const input = screen.getByPlaceholderText("Escribe un mensaje...");
  //   const sendButton = screen.getByRole("button", { name: "Enviar" });

  //   fireEvent.change(input, { target: { value: "Test message" } });
  //   fireEvent.click(sendButton);

  //   expect(mockFetchMessages).toHaveBeenCalledTimes(1); 
  // });

});
