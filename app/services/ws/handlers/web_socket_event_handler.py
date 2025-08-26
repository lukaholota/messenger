from app.infrastructure.cache.redis_pubsub import RedisPubSub
from app.schemas.chat import ChatCreate, StartNewChatIn
from app.schemas.chat_read_status import ChatReadStatusUpdate
from app.schemas.contact import ContactCreate
from app.schemas.event import GetChatInfoEvent, ChatInfoSentEvent, \
    GetChatMessagesEvent, ChatMessagesSentEvent, ChatCreatedEvent, \
    SearchResultSentEvent, AddedToContactsEvent, ContactsSentEvent
from app.schemas.message import MessageCreate
from app.schemas.search import SearchIn
from app.services.chat.chat_create_helper import ChatCreateHelper
from app.services.chat.chat_info_service import ChatInfoService
from app.services.contact.contact_service import ContactService
from app.services.message.chat_messages_constructor import \
    ChatMessagesConstructor
from app.services.search.search_service import SearchService
from app.services.ws.chat_read_service import ChatReadService
from app.services.ws.event_sender import EventSender
from app.services.ws.message_web_socket_handler import MessageWebSocketHandler



class WebSocketEventHandler:
    def __init__(
            self,
            message_handler: MessageWebSocketHandler,
            chat_message_constructor: ChatMessagesConstructor,
            chat_read_service: ChatReadService,
            chat_info_service: ChatInfoService,
            event_sender: EventSender,
            search_service: SearchService,
            pubsub: RedisPubSub,
            chat_create_helper: ChatCreateHelper,
            contact_service: ContactService
    ):
        self.message_handler = message_handler
        self.chat_message_constructor = chat_message_constructor
        self.chat_read_service = chat_read_service
        self.chat_info_service = chat_info_service
        self.event_sender = event_sender
        self.search_service = search_service
        self.pubsub = pubsub
        self.chat_create_helper = chat_create_helper
        self.contact_service = contact_service

    async def handle_new_message(
            self, message_in: MessageCreate, user_id: int,
    ):
        await self.message_handler.send_to_mq(user_id, message_in)

    async def handle_read_message(
            self, data_in: ChatReadStatusUpdate, user_id: int
    ):
        await self.chat_read_service.update_read_status(user_id, data_in)

    async def handle_get_chat_info(
            self, data_in: GetChatInfoEvent, user_id: int
    ):
        chat_info = await self.chat_info_service.get_chat_info(
            data_in.chat_id, user_id
        )

        event = ChatInfoSentEvent(data=chat_info)

        await self.event_sender.send_event(event)

    async def handle_get_chat_messages(
            self, data_in: GetChatMessagesEvent, user_id: int
    ):
        messages = await self.chat_message_constructor.construct_chat_messages(
            data_in.chat_id, user_id
        )

        event = ChatMessagesSentEvent(data=messages)

        await self.event_sender.send_event(event)

    async def handle_create_chat(self, data_in: ChatCreate, user_id: int):
        chat_info = await self.chat_create_helper.init_new_chat(
            data_in, user_id
        )

        websocket_event = ChatCreatedEvent(data=chat_info)

        await self.event_sender.send_event(websocket_event)

        return chat_info

    async def handle_search(self, data_in: SearchIn, user_id: int):
        found_users = await self.search_service.search(data_in, user_id)

        event = SearchResultSentEvent(data=found_users)

        await self.event_sender.send_event(event)

    async def handle_start_new_chat(self, data_in: StartNewChatIn, user_id):
        target_user_id = data_in.target_user_id
        chat_create = ChatCreate(
            participant_ids=[user_id, target_user_id],
            is_group=False
        )

        chat_info = await self.handle_create_chat(chat_create, user_id)

        message_in = MessageCreate(
            chat_id=chat_info.chat_id,
            content=data_in.content
        )

        await self.handle_new_message(message_in, user_id)

    async def handle_add_to_contacts(
            self, contact_create: ContactCreate, user_id: int
    ):
        contact_read = await self.contact_service.add_to_contacts(
            contact_create=contact_create, user_id=user_id
        )

        event = AddedToContactsEvent(data=contact_read)

        await self.event_sender.send_event(event)

    async def handle_get_contacts(
            self, user_id: int
    ):
        contacts = await self.contact_service.get_contacts(user_id)

        event = ContactsSentEvent(data=contacts)

        await self.event_sender.send_event(event)

