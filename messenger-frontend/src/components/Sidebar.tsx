import React from 'react';

const MenuIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
         stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"/>
        <line x1="3" y1="6" x2="21" y2="6"/>
        <line x1="3" y1="18" x2="21" y2="18"/>
    </svg>
);

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateGroupChat: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen, onClose, onCreateGroupChat
}) => {
  if (!isOpen) return null;

  const handleCreateGroupChat = () => {
    onCreateGroupChat();
    onClose();
  };

  return (
    <>
      <div className="sidebar-backdrop" onClick={onClose}>
        <div className="sidebar">
          <div className="sidebar-header">
            <h3>Menu</h3>
            <button onClick={onClose} className="close-btn">&times;</button>
          </div>
          <ul className="sidebar-menu">
            <li onClick={handleCreateGroupChat}>Create Group Chat</li>
          </ul>
        </div>

      </div>
    </>
  )
}

export { MenuIcon };