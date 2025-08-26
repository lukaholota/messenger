import React, {useEffect, useRef, useState} from 'react';
import type {
  Message,
  ChatInfo,
  User,
  SearchUser,
  NewMessagePayload
} from "../types";
import { ChatInfoModal } from './ChatInfoModal';

interface ChatWindowBaseProps {
  currentUserId: number;
  sendMessage: (payload: NewMessagePayload) => void;
}

interface ExistingChatProps extends ChatWindowBaseProps {
  type: 'existing';
  chatId: number;
  chatName: string;
  messages: Message[];
  chatInfo: ChatInfo | null;
  requestChatInfo: (chatId: number) => void;
}

interface ProvisionalChatProps extends ChatWindowBaseProps {
  type: 'provisional';
  targetUser: SearchUser;
  messages: Message[];
}

type ChatWindowProps = ExistingChatProps | ProvisionalChatProps

export const ChatWindow: React.FC<ChatWindowProps> = (props) => {
  const [message, setMessage] = useState('');
  const [isInfoModalOpen, setIsInfoModalOpen] = useState(false);
  const [isReadModalOpen, setIsReadModalOpen] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const SendIcon = () => (
    <svg viewBox="0 0 24 24" width="24" height="24" fill="white">
      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
    </svg>
  );
  const DoubleTickIcon = ({ color }: { color: string }) => (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 18" width="18" height="18">
          <path fill={color} d="M17.394 4.646l-11.05 11.05-5.688-5.688 1.414-1.414 4.274 4.274 9.636-9.636 1.414 1.414z"/>
          <path fill={color} d="M12.394 4.646l-6.636 6.636-2.864-2.864 1.414-1.414 1.45 1.45 5.222-5.222 1.414 1.414z"/>
      </svg>
  );
  const SingleTickIcon = ({ color }: { color: string }) => (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 18" width="18" height="18">
          <path fill={color} d="M17.618 5.077l-10 10-4.695-4.695 1.414-1.414 3.281 3.281 8.586-8.586z"/>
      </svg>
  );

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [props.messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    if (props.type === 'existing') {
        props.sendMessage({
          type: 'existing_chat',
          chatId: props.chatId,
          content: message
        });
    } else if (props.type === 'provisional') {
      props.sendMessage({
        type: 'new_chat',
        targetUserId: props.targetUser.user_id,
        content: message
      });
    }

    setMessage('');
  };

  const openChatInfo = () => {
    if (props.type === 'existing') {
      props.requestChatInfo(props.chatId);
      setIsInfoModalOpen(true);
    }
  };

  const openReadInfo = (msg: Message) => {
    if (props.type === 'existing') {
      if (props.chatInfo?.is_group && msg.user_id === props.currentUserId) {
        setSelectedMessage(msg);
        setIsReadModalOpen(true);
      }
    }
  };

  const participantMap = new Map<number, User>();
  if (props.type === 'existing') {
  props.chatInfo?.participants?.forEach(user => {
    participantMap.set(user.user_id, user);
  });
  }

  const chatName = props.type === 'existing'
    ? props.chatName
    : props.targetUser.display_name;

  const onlineStatus = props.type === 'existing'
    ? props.chatInfo?.is_group ? `${props.chatInfo.participant_count} members` : 'online'
    : ''
  ;


  return (
    <div className="chat-window">
      <div className="chat-header" onClick={openChatInfo}>
        <div className="avatar-placeholder" style={{ backgroundColor: '#A0C3D2' }}>
          {chatName.charAt(0)}
        </div>
        <div className="chat-header-info">
          <h2>{chatName}</h2>
          <p>{onlineStatus}</p>
        </div>
      </div>

      <div className="messages-area">
        {props.messages.map((msg) => (
          <div
            key={msg.message_id}
            className={`message-container ${msg.user_id === props.currentUserId ? 'outgoing' : 'incoming'}`}
          >
            <div className="message-bubble" onClick={() => openReadInfo(msg)}>
              {props.type === 'existing' && props.chatInfo?.is_group && msg.user_id !== props.currentUserId && (
                <div className="sender-name">{msg.display_name}</div>
              )}
              <div className="message-content">{msg.content}</div>
              <div className="message-meta">
                    <span className="timestamp">{new Date(msg.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                {msg.user_id === props.currentUserId && (
                  <span className="read-indicator">
                    {msg.is_read ? <DoubleTickIcon color="#4FC3F7" /> : <SingleTickIcon color="#9E9E9E" />}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form className="input-area" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Message"
        />
        <button type="submit" className="send-button"><SendIcon /></button>
      </form>

      {props.type === 'existing' && isInfoModalOpen && props.chatInfo && (
        <ChatInfoModal chatInfo={props.chatInfo} onClose={() => setIsInfoModalOpen(false)} />
      )}

      {props.type === 'existing' && isReadModalOpen && selectedMessage && (
        <div className="modal-overlay" onClick={() => setIsReadModalOpen(false)}>
          <div className="modal-content read-modal" onClick={e => e.stopPropagation()}>
            <h4>Read by:</h4>
            <ul>
              {selectedMessage.read_at_list[0] ? (
                selectedMessage.read_at_list.map((entry, idx) => {
                  const [userIdStr, readAt] = Object.entries(entry)[0];
                  const userId = Number(userIdStr);
                  if (userId !== props.currentUserId && readAt) {
                    const readBy = participantMap?.get(userId);
                    const formattedTime = new Date(readAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    return (
                      <li key={idx}>
                        <div className="avatar-placeholder small" style={{ backgroundColor: '#A0C3D2' }}>{readBy?.display_name.charAt(0)}</div>
                        <span>{readBy?.display_name}</span>
                        <span className="read-at-time">{formattedTime}</span>
                      </li>
                    );
                  }
                  return null;
                })
              ) : (
                <li>No one has read this message yet.</li>
              )}
            </ul>
            <button onClick={() => setIsReadModalOpen(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};
