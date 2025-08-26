import React, { useState } from 'react';
import type { Contact } from '../types';

interface CreateGroupChatModalProps {
  isOpen: boolean;
  onClose: () => void;
  contacts: Contact[] | null;
  onCreate: (name: string, userIds: number[]) => void;
  currentUserId: number;
}

export const CreateGroupChatModal: React.FC<CreateGroupChatModalProps> = (
  { isOpen, onClose, contacts, onCreate, currentUserId }
) => {
  const [groupName, setGroupName] = useState('');
  const [selectedContacts, setSelectedContacts] = useState<Contact[]>([]);

  if (!isOpen) return null;

  const handleSelectContact = (contact: Contact) => {
    if (!selectedContacts.some(c => c.contact_id === contact.contact_id)) {
      setSelectedContacts([...selectedContacts, contact]);
    }
  };

  const handleRemoveContact = (contact: Contact) => {
    setSelectedContacts(
      selectedContacts.filter(c => c.contact_id !== contact.contact_id)
    )
  };

  const handleCreate = () => {
    if (groupName.trim()) {
      const userIds = [...selectedContacts.map(c => c.contact_id), currentUserId]
      onCreate(groupName, userIds)
      setGroupName('');
      setSelectedContacts([]);
      onClose();
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <h3>Create Group Chat</h3>
        <input
          type="text"
          placeholder="Group name"
          value={groupName}
          onChange={(e) => setGroupName(e.target.value)}
        />
        <div className="selected-contacts">
          {selectedContacts.map(c => (
            <div key={c.contact_id} className="selected-contact-chip">

            </div>
            )
          )}
        </div>
      </div>


    </div>
  )
}