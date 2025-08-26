import { ChatList } from './components/ChatList';
import { ChatWindow } from './components/ChatWindow';
import { useWebSocket } from './hooks/useWebSocket';
import { getUserIdFromToken } from './utils/auth';
import React, {useState, useEffect, useMemo} from "react";
import type {SearchUser} from "./types";
import {AddContactModal} from "./components/AddContactModal";
import {Sidebar} from "./components/Sidebar";

const ChatApp: React.FC<{ accessToken: string }> = ({ accessToken }) => {
  const [currentChatId, setCurrentChatId] = useState<number | null>(null);
  const [provisionalChatUser, setProvisionalChatUser] = useState<SearchUser | null>(null);
  const [contactToAdd, setContactToAdd] = useState<SearchUser | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const currentUserId = getUserIdFromToken(accessToken);

  const {
    sendMessage,
    messagesByChat,
    chatOverviewList,
    chatInfo,
    requestChatInfo,
    requestChatMessages,
    search,
    searchResults,
    setSearchResults,
    newlyCreatedChatInfo,
    contacts,
    getContacts,
    addToContacts,
    notification
  } = useWebSocket();

  useEffect(() => {
    if (currentChatId != null) {
      requestChatMessages(currentChatId);
    }
  }, [currentChatId, requestChatMessages]);

  const selectedChatMessages = useMemo(() => {
      return currentChatId ? (messagesByChat[currentChatId] || []) : [];
  }, [currentChatId, messagesByChat]);

  const chatWindowProps = useMemo(() => {
    if (currentChatId) {
      const selectedChat = chatOverviewList.find(chat => chat.chat_id === currentChatId);
      return {
        type: 'existing' as const,
        chatId: currentChatId,
        chatName: selectedChat?.chat_name ?? '',
        messages: selectedChatMessages,
        chatInfo: chatInfo,
        requestChatInfo: requestChatInfo
      };
    }
    if (provisionalChatUser) {
      return {
        type: 'provisional' as const,
        messages: [],
        targetUser: provisionalChatUser,
      }
    }
    return null;
  }, [
    currentChatId,
    provisionalChatUser,
    chatOverviewList,
    messagesByChat,
    chatInfo,
    selectedChatMessages,
    requestChatInfo
    ]
  )

  const handleSelectChat = (chatId: number) => {
    setCurrentChatId(chatId)
    setProvisionalChatUser(null)
  }
  const handleSelectUser = (user: SearchUser) =>  {
    setProvisionalChatUser(user);
    setCurrentChatId(null);
    setSearchResults([]);
  }

  const handleConfirmAddContact = (contact_id: number, name: string) => {
    addToContacts(contact_id, name);
    setContactToAdd(null);
  }

  const handleCreateGroupChat = () => {
    console.log("Opening create group chat modal...")
    getContacts();
  }

  useEffect(() => {
    if (newlyCreatedChatInfo && provisionalChatUser) {
      const doesChatBelongToUser = newlyCreatedChatInfo.participants.some(
        p => p.user_id === provisionalChatUser.user_id
      );

      if (doesChatBelongToUser) {
        setProvisionalChatUser(null);
        setCurrentChatId(newlyCreatedChatInfo.chat_id)
    }}

  }, [newlyCreatedChatInfo, provisionalChatUser])

  return (
    <div className="app">
      {notification && <div className="notification">{notification}</div>}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onCreateGroupChat={handleCreateGroupChat}
      />
      <div className="chat-sidebar">
        <ChatList
            chatOverviewList={chatOverviewList}
            currentChatId={currentChatId}
            onSelectChat={handleSelectChat}
            onSelectUser={handleSelectUser}
            search={search}
            searchResults={searchResults}
            setSearchResults={setSearchResults}
            onInitiateAddContact={(user) => setContactToAdd(user)}
            onMenuClick={() => setIsSidebarOpen(true)}
        />
      </div>
      <div className="add-contact-modal">
        <AddContactModal
          user={contactToAdd}
          onClose={() => setContactToAdd(null)}
          onConfirm={handleConfirmAddContact}
        />

      </div>
      <div className="chat-window">
        {chatWindowProps && currentUserId !== null ? (
          <ChatWindow
            {...chatWindowProps}
            currentUserId={currentUserId}
            sendMessage={sendMessage}
          />
        ) : (
          <div>Select a chat</div>
        )}
      </div>
    </div>
  );
};

export default ChatApp;
