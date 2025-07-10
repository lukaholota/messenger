import React from 'react';

interface ChatListProps {
  chatOverviewList: any[];
  setCurrentChatId: React.Dispatch<React.SetStateAction<number | null>>;
}

export const ChatList: React.FC<ChatListProps> = ({ chatOverviewList, setCurrentChatId }) => {
  return (
      <div>
          <h2>Chats</h2>
          <ul>
              {chatOverviewList.map((chat) => (
                  <li key={chat.chat_id}
                      onClick={() => setCurrentChatId(chat.chat_id)}>
                      <span className="chat-name">{chat.chat_name}</span>
                      {chat.unread_count > 0 && (
                          <span
                              className="unread-badge">{chat.unread_count}</span>
                      )}
                  </li>
              ))}
          </ul>
      </div>
  );
};
