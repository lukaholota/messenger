import React, { useState } from 'react';
import type {Message, ChatInfo} from "../types";
import { ChatInfoModal } from './ChatInfoModal';

interface ChatWindowProps {
  chatId: number;
  chatName: string;
  currentUserId: number
  sendMessage: (chatId: number, message: string) => void;
  messages: Message[];
  chatInfo: ChatInfo | null;
  requestChatInfo: (chatId: number) => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
    chatId, chatName, currentUserId, sendMessage, messages, chatInfo, requestChatInfo
}) => {
  const [message, setMessage] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleSendMessage = () => {
    sendMessage(chatId, message);
    setMessage('');
  };
  const openChatInfo = () => {
      requestChatInfo(chatId);
      setIsModalOpen(true);
  }

  return (
      <div>
          <div className="chat-header" onClick={() => openChatInfo()}>
              <h2>Chat {chatName}</h2>
              <p>{chatInfo?.participant_count ?? ''} учасників</p>
          </div>

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

          {isModalOpen && chatInfo && (
              <ChatInfoModal chatInfo={chatInfo} onClose={() => setIsModalOpen(false)} />
          )}
      </div>
  );
};
