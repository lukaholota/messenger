export type ServerToClientEvent =
  | 'message_sent'
  | 'read_status_updated'
  | 'undelivered_messages_sent'
  | 'chat_overview_list_sent'
  | 'chat_sent';
