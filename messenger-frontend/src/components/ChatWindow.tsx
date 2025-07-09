import React, { useState } from 'react';

interface ChatWindowProps {
  chatId: string;
  sendMessage: (chatId: string, message: string) => void;
  messages: any[];
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ chatId, sendMessage, messages }) => {
  const [message, setMessage] = useState('');

  const handleSendMessage = () => {
    sendMessage(chatId, message);
    setMessage('');
  };

  return (
    <div>
      <h2>Chat {chatId}</h2>
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx}>
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message"
      />
      <button onClick={handleSendMessage}>Send</button>
    </div>
  );
};
