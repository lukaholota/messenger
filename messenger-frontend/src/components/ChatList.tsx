import React from 'react';

interface ChatListProps {
  chatOverviewList: any[];
  setCurrentChatId: React.Dispatch<React.SetStateAction<string | null>>;
}

export const ChatList: React.FC<ChatListProps> = ({ chatOverviewList, setCurrentChatId }) => {
  return (
    <div>
      <h2>Chats</h2>
      <ul>
        {chatOverviewList.map((chat) => (
          <li key={chat.id} onClick={() => setCurrentChatId(chat.id)}>
            {chat.name}
          </li>
        ))}
      </ul>
    </div>
  );
};
