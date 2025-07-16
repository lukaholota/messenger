import React from "react";
import type { ChatInfo } from '../types';
import '../css/ChatInfoModal.css';

interface Props {
    chatInfo: ChatInfo;
    onClose: () => void;
}

export const ChatInfoModal: React.FC<Props> = ({ chatInfo, onClose }) => {
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => {e.stopPropagation()}}>
                <h2>{chatInfo.chat_name}</h2>
                <p>Учасників: {chatInfo.participant_count}</p>
                <ul>
                    {chatInfo.participants.map((user) => (
                        <li key={user.user_id}>{user.display_name}</li>
                    ))}
                </ul>
                <button onClick={onClose}>Закрити</button>
            </div>
        </div>
    )
}