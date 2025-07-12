import React, { useEffect, useState } from 'react';
import { Login } from './components/Login';
import { ChatList } from './components/ChatList';
import { ChatWindow } from './components/ChatWindow';
import { useWebSocket } from './hooks/useWebSocket';
import { getUserIdFromToken } from './utils/auth';
import './index.css';

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentChatId, setCurrentChatId] = useState<number | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);

  const { sendMessage, messages, chatOverviewList } = useWebSocket();

  useEffect(() => {
    if (accessToken) {
      setIsAuthenticated(true);
      const userId = getUserIdFromToken(accessToken);
      if (userId) {
        setCurrentUserId(userId);
      }
    } else {
      setIsAuthenticated(false);
    }
  }, [accessToken]);

  if (!isAuthenticated) {
    return <Login setAccessToken={setAccessToken} />;
  }

  const selectedChat = chatOverviewList.find(chat => chat.chat_id === currentChatId);
  const chatName = selectedChat ? selectedChat.chat_name : '';

  return (
    <div className="app">
      <div className="chat-sidebar">
        <ChatList chatOverviewList={chatOverviewList} setCurrentChatId={setCurrentChatId} />
      </div>
      <div className="chat-window">
        {currentChatId && currentUserId !== null ? (
          <ChatWindow
            chatId={currentChatId}
            chatName={chatName}
            currentUserId={currentUserId}
            sendMessage={sendMessage}
            messages={messages}
          />
        ) : (
          <div>Select a chat</div>
        )}
      </div>
    </div>
  );
};

export default App;
