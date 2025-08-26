from enum import Enum

class ClientToServerEvent(str, Enum):
    NEW_MESSAGE = 'new_message'
    READ_MESSAGE = 'read_message'
    GET_CHAT_INFO = 'get_chat_info'
    GET_CHAT_MESSAGES = 'get_chat_messages'
    CREATE_CHAT = 'create_chat'
    SEARCH = 'search'
    START_NEW_CHAT = 'start_new_chat'
    ADD_TO_CONTACTS = 'add_to_contacts'
    GET_CONTACTS = 'get_contacts'


class ServerToClientEvent(str, Enum):
    MESSAGE_SENT = 'message_sent'
    READ_STATUS_UPDATED = 'read_status_updated'
    UNDELIVERED_MESSAGES_SENT = 'undelivered_messages_sent'
    CHAT_OVERVIEW_LIST_SENT = 'chat_overview_list_sent'
    CHAT_INFO_SENT = 'chat_info_sent'
    CHAT_MESSAGES_SENT = 'chat_messages_sent'
    CHAT_CREATED = 'chat_created'
    SEARCH_RESULT_SENT = 'search_result_sent'
    NEW_CHAT_SENT = 'new_chat_sent'
    ADDED_TO_CONTACTS = 'added_to_contacts'
    CONTACTS_SENT = 'contacts_sent'
