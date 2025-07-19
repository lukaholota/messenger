import { ChatList } from './components/ChatList';
import { ChatWindow } from './components/ChatWindow';
import { useWebSocket } from './hooks/useWebSocket'; // Залишаємо імпорт
import { getUserIdFromToken } from './utils/auth';
import React, {useState, useEffect} from "react";

const ChatApp: React.FC<{ accessToken: string }> = ({ accessToken }) => {
  const [currentChatId, setCurrentChatId] = useState<number | null>(null);
  const currentUserId = getUserIdFromToken(accessToken);

  const {
      sendMessage,
      messages,
      chatOverviewList,
      chatInfo,
      requestChatInfo,
      requestChatMessages
  } = useWebSocket();

  useEffect(() => {
    if (currentChatId != null) {
      requestChatInfo(currentChatId);
      requestChatMessages(currentChatId);
    }
  }, [currentChatId]);

  const selectedChat = chatOverviewList.find(chat => chat.chat_id === currentChatId);
  const chatName = selectedChat?.chat_name ?? '';

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
            chatInfo={chatInfo}
            requestChatInfo={requestChatInfo}
          />
        ) : (
          <div>Select a chat</div>
        )}
      </div>
    </div>
  );
};

export default ChatApp;
