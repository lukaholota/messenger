import React, { useEffect, useState } from 'react';
import { Login } from './components/Login';
import { ChatList } from './components/ChatList';
import { ChatWindow } from './components/ChatWindow';
import { useWebSocket } from './hooks/useWebSocket';
import './index.css';


const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentChatId, setCurrentChatId] = useState<number | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(localStorage.getItem('access_token'));

  const { sendMessage, messages, chatOverviewList } = useWebSocket();

  // Check for token existence
  useEffect(() => {
    if (accessToken) {
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
  }, [accessToken]);

  if (!isAuthenticated) {
    return <Login setAccessToken={setAccessToken} />;
  }

  return (
    <div className="app">
      <div className="chat-sidebar">
        <ChatList chatOverviewList={chatOverviewList} setCurrentChatId={setCurrentChatId} />
      </div>
      <div className="chat-window">
        {currentChatId ? (

          <ChatWindow chatId={currentChatId} sendMessage={sendMessage} messages={messages} />
        ) : (
          <div>Select a chat</div>
        )}
      </div>
    </div>
  );
};

export default App;
