import React, {useEffect, useState} from 'react';
import type { SearchUser } from '../types';

interface AddContactModalProps {
  user: SearchUser | null;
  onClose: () => void;
  onConfirm: (contactId: number, name: string) => void;
}

export const AddContactModal: React.FC<AddContactModalProps> = (
  { user, onClose, onConfirm }
) => {
  const [name, setName] = useState('');

  useEffect(() => {
    if (user) {
      setName(user.display_name)
    }
  }, [user]);

  if (!user) {
    return null;
  }

  const handleConfirm = () => {
    if (name.trim()) {
      onConfirm(user.user_id, name.trim())
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <h4>Add to Contacts</h4>
        <p>You are adding <strong>{user.username}</strong> to your contacts</p>
        <div className="form-group">
          <label htmlFor="contactName">Contact Name</label>
          <input
            id="contactName"
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Enter name for contact"
          />
        </div>
        <div className="modal-actions">
          <button onClick={onClose} className="btn-secondary">Cancel</button>
          <button onClick={handleConfirm} disabled={!name.trim()}
                  className="btn-primary">Save
          </button>
        </div>
      </div>
    </div>
  )
}