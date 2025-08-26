import React, {useEffect, useState} from 'react';
import type {ChatOverview, SearchUser} from "../types";
import {MenuIcon} from "./Sidebar";

export const ChatList: React.FC<{
  chatOverviewList: ChatOverview[];
  currentChatId: number | null;
  onSelectChat: (chatId: number) => void;
  onSelectUser: (user: SearchUser) => void;
  search: (prompt: string) => void;
  searchResults: SearchUser[];
  setSearchResults: React.Dispatch<React.SetStateAction<SearchUser[]>>;
  onInitiateAddContact: (user: SearchUser) => void;
  onMenuClick: () => void;
}> = (
  {
    chatOverviewList,
    currentChatId,
    onSelectChat,
    onSelectUser,
    search,
    searchResults,
    setSearchResults,
    onInitiateAddContact,
    onMenuClick,
  }
) => {
  const [query, setQuery] = useState<string>('')
  useEffect(() => {
    if (query.length > 0) {
      search(query);
    } else {
      setSearchResults([]);
    }
  }, [query, search, setSearchResults]);

  const SearchIcon = () => (
    <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
      <path
        fillRule="evenodd"
        d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
        clipRule="evenodd"
      />
    </svg>
  );

  const UserPlusIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
         stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="8.5" cy="7" r="4"/>
      <line x1="20" y1="8" x2="20" y2="14"/>
      <line x1="17" y1="11" x2="23" y2="11"/>
    </svg>
  );

  const UserCheckIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
         stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="8.5" cy="7" r="4"/>
      <polyline points="17 11 19 13 23 9"/>
    </svg>
  );

  const Avatar  = (display_name: string) => (
    <div className="avatar-placeholder"
         style={{backgroundColor: '#FFD580'}}>
      {display_name.charAt(0)}
    </div>
  )

  const handleAddToContacts = (e: React.MouseEvent, user: SearchUser) => {
    e.stopPropagation();
    onInitiateAddContact(user);
  }

  return (
    <div className="chat-list-container">
      <div className="chat-list-header">
        <button onClick={onMenuClick} className="menu-btn"><MenuIcon/></button>
        <div className="search-bar">
          <span className="search-icon"><SearchIcon/></span>
          <input
            type="text"
            placeholder="Search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </div>

      {searchResults?.length > 0 ? (
          <ul className="search-results">
            <p>Found users:</p>
            {searchResults.map((user) => (
              <li
                key={user.user_id}
                className={`search-result-item ${user.is_contact ? 'is-contact' : ''}`}
                onClick={() => {
                  onSelectUser(user)
                }}
              >
                {Avatar(user.display_name)}
                <div className="chat-details">
                  <span className="chat-name">{user.display_name}</span>
                  <span className="chat-username">@{user.username}</span>
                </div>
                <div className="contact-action">
                  {user.is_contact ? (
                    <span className="tooltip" data-tooltip="Already in contacts">
                      <UserCheckIcon/>
                    </span>
                  ) : (
                    <button onClick={
                      (e) =>
                        handleAddToContacts(e, user)}
                        className="add-contact-btn">
                      <UserPlusIcon/>
                    </button>
                    )
                  }
                </div>
              </li>
            ))}
          </ul>
        )

        : (
          <ul className="chat-list">
            {chatOverviewList.map((chat) => (
              <li
                key={chat.chat_id}
                className={`chat-list-item ${chat.chat_id === currentChatId ? 'active' : ''}`}
                onClick={() => onSelectChat(chat.chat_id)}
              >
                {Avatar(chat.chat_name)}

                <div className="chat-details">
                  <div className="chat-name-time">
                    <span className="chat-name">{chat.chat_name}</span>

                    <span className="chat-timestamp">{
                      chat.last_message
                        ? new Date(chat.last_message.sent_at).toLocaleTimeString([],
                          {hour: '2-digit', minute: '2-digit'})
                        : ''
                    }
                </span>
                  </div>
                  <div className="last-message-badge">
                    <p className="last-message">
                      {chat.last_message ? chat.last_message.content : 'No messages yet'}
                    </p>
                    {chat.unread_count > 0 && (
                      <span className="unread-badge">{chat.unread_count}</span>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
    </div>
  );
};