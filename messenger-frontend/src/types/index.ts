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

export type ServerToClientEvent =
  | 'message_sent'
  | 'read_status_updated'
  | 'undelivered_messages_sent'
  | 'chat_overview_list_sent'
  | 'chat_sent';

export interface IncomingMessage {
  event: ServerToClientEvent;
  data: unknown;
}
