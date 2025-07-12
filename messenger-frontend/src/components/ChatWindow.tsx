import React, { useState } from 'react';
import type {Message} from "../types";

interface ChatWindowProps {
  chatId: number;
  chatName: string;
  currentUserId: number
  sendMessage: (chatId: number, message: string) => void;
  messages: Message[];
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ chatId, chatName, currentUserId,sendMessage, messages }) => {
  const [message, setMessage] = useState('');

  const handleSendMessage = () => {
    sendMessage(chatId, message);
    setMessage('');
  };

  return (
      <div>
          <h2>Chat {chatName}</h2>
          <div className="messages">
              {messages
                  .filter((msg) => msg.chat_id === chatId)
                  .map((msg, idx) => (
                      <div
                          key={idx}
                          className={`message ${msg.user_id === currentUserId ? 'outgoing' : 'incoming'}`}
                      >
                          <div>{msg.content}</div>
                          <div
                              className="timestamp">{new Date(msg.sent_at).toLocaleTimeString()}</div>
                      </div>
                  ))}
          </div>
          <div className="input-area">
              <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Type a message"
              />
              <button onClick={handleSendMessage}>➤</button>
          </div>
      </div>
          );
          };
