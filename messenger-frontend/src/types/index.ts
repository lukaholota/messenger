export interface Message {
  message_id: number;
  content: string;
  sent_at: string;  // ISO datetime string (from FastAPI)
  user_id: number;
  chat_id: number;
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
  | 'chat_info_sent';

export interface IncomingMessage {
  event: ServerToClientEvent;
  data: unknown;
}
