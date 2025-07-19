export interface Message {
  message_id: number;
  chat_id: number;
  user_id: number;
  content: string;
  is_read: boolean;
  read_at_list: Record<number, string | null>[]; // [{1: "2024-07-16T13:00:00Z"}, {2: null}]
  display_name: string;
  sent_at: string; // Не забудь це поле, якщо ще не було
}

export interface MessageInChatOverview {
  sent_at: string;
  content: string;
  display_name: string;
}

export interface ChatOverview {
  chat_id: number;
  chat_name: string;
  last_message: MessageInChatOverview;
  unread_count: number;
}

export interface User {
  user_id: number;
  display_name: string;
}

export interface ChatInfo {
  chat_id: number;
  chat_name: string;
  participants: User[]
  participant_count: number;
  is_group: boolean;
}



export type ServerToClientEvent =
  | 'message_sent'
  | 'read_status_updated'
  | 'undelivered_messages_sent'
  | 'chat_overview_list_sent'
  | 'chat_info_sent'
  | 'chat_messages_sent'

export interface IncomingMessage {
  event: ServerToClientEvent;
  data: unknown;
}
