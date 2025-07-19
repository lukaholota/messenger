import React, { useState } from 'react';
import type {Message, ChatInfo, User} from "../types";
import { ChatInfoModal } from './ChatInfoModal';
import '../css/ChatWindow.css';

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
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);

  const handleSendMessage = () => {
    sendMessage(chatId, message);
    setMessage('');
  };
  const openChatInfo = () => {
      requestChatInfo(chatId);
      setIsModalOpen(true);
  }

  const isGroup = chatInfo?.is_group;
  const participantMap = new Map<number, User>();
  chatInfo?.participants?.forEach(user =>{
      participantMap.set(user.user_id, user);
  });


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
                          onClick={() => {
                            if (isGroup && msg.user_id === currentUserId) {
                              setSelectedMessage(msg);
                            }
                          }}
                      >
                          <span>{msg.display_name}</span>
                          <div>{msg.content}</div>
                          <div
                              className="timestamp">{new Date(msg.sent_at).toLocaleTimeString()}
                          </div>
                          {msg.user_id === currentUserId && (
                          <span className="read-indicator">
                            {msg.is_read ? '✓✓' : '✓'}
                          </span>
                          )}
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


          {selectedMessage && (
              <div className="read-modal">
                  <h4>Прочитали:</h4>
                  <ul>
                      {selectedMessage.read_at_list.map((entry, idx) => {
                          const [userIdStr, readAt] = Object.entries(entry)[0];
                          const userId = Number(userIdStr)
                          const readBy = participantMap.get(userId)
                          return (
                              <li key={idx}>
                                  👤 {readBy?.display_name} - {readAt}
                              </li>
                          );
                      })};
                  </ul>
                  <button onClick={() => setSelectedMessage(null)}>X</button>
              </div>
          )}
      </div>
  );
};
