from enum import Enum

class ClientToServerEvent(str, Enum):
    NEW_MESSAGE = 'new_message'
    READ_MESSAGE = 'read_message'


class ServerToClientEvent(str, Enum):
    MESSAGE_SENT = 'message_sent'
    READ_STATUS_UPDATED = 'read_status_updated'
    UNDELIVERED_MESSAGES_SENT = 'undelivered_messages_sent'
    CHAT_OVERVIEW_LIST_SENT = 'chat_overview_list_sent'
