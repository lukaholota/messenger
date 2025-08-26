import React from "react";
import type { ChatInfo } from '../types';

interface Props {
    chatInfo: ChatInfo;
    onClose: () => void;
}

export const ChatInfoModal: React.FC<Props> = ({ chatInfo, onClose }) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{chatInfo.chat_name}</h2>
          <p>{chatInfo.participant_count} members</p>
        </div>
        <ul className="participants-list">
          {chatInfo.participants.map((user) => (
            <li key={user.user_id}>
                <div className="avatar-placeholder small" style={{ backgroundColor: '#A0C3D2' }}>{user.display_name.charAt(0)}</div>
                <span>{user.display_name}</span>
            </li>
          ))}
        </ul>
        <button className="close-button" onClick={onClose}>Close</button>
      </div>
    </div>
  );
};