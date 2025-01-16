import React, { useState, useEffect } from "react";
import "./chat.css";

const Chat = ({ gameId, userId, messages,fetchMessages, addMessage, hasUnreadMessages, clearUnreadMessages }) => {
     const [newMessage, setNewMessage] = useState("");
  const [isChatOpen, setIsChatOpen] = useState(false);


  const sendMessage = async () => {
    if (newMessage.trim()) {
      try {
        const response = await fetch(
          `http://localhost:8000/game/${gameId}/user/${userId}/message`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              user_id: userId,
              game_id: gameId,
              content: newMessage,
            }),
          }
        );

        if (response.ok) {
          setNewMessage("");
          fetchMessages(); 
        } else {
          console.error("Failed to send message");
        }
      } catch (error) {
        console.error("Error sending message:", error);
      }
    }
  };

  useEffect(() => {
     if (isChatOpen) {
       clearUnreadMessages();
     }
   }, [isChatOpen, fetchMessages, clearUnreadMessages]);

  useEffect(() => {
     if (hasUnreadMessages && messages.length > 0) {
       const lastMessage = messages[messages.length - 1];
       if (lastMessage.userId === userId) {
         clearUnreadMessages(); 
       }
     }
   }, [messages, hasUnreadMessages, userId, clearUnreadMessages]);

  return (
    <div className="chat-container">
      <button className="chat-toggle" onClick={() => setIsChatOpen(!isChatOpen)}>
        💬
        {hasUnreadMessages && !isChatOpen && <span className="unread-indicator"></span>}
      </button>

      {isChatOpen && (
        <div className="chat-window">
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className="chat-message">
                <strong>{msg.name}:</strong> {msg.content || "Mensaje vacío"}
                </div>
            ))}
          </div>
          <div className="chat-input">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Escribe un mensaje..."
            />
            <button onClick={sendMessage}>Enviar</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;
