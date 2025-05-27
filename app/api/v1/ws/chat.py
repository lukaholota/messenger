from fastapi import APIRouter, WebSocket
from pydantic_core import ValidationError
from starlette.websockets import WebSocketDisconnect

from app.api.dependencies.auth import get_current_user_id_ws
from app.db.session import get_lifespan_db
from app.infrastructure.cache.connection import get_lifespan_redis_client
from app.infrastructure.exceptions.websocket import WebSocketException
from app.schemas.message import MessageCreate
from app.services.ws.web_socket_service_container import WebSocketServiceContainer
from app.services.ws.chat_web_socket_service import ChatWebSocketService

router = APIRouter()


@router.websocket('/ws/chat')
async def chat_websocket(
        websocket: WebSocket,
):
    try:
        await websocket.accept()

        async with (
            get_lifespan_db() as db,
            get_lifespan_redis_client() as redis_client
        ):
            container = WebSocketServiceContainer(db, redis_client)

            access_token = websocket.query_params.get('access_token')
            if not access_token:
                raise WebSocketException('no access token provided')

            current_user_id = await get_current_user_id_ws(
                token=access_token,
                user_repository=container.user_repository,
                redis_token_blacklist_service=await container.
                    get_redis_token_blacklist_service(),
                redis=container.redis,
            )
            service = ChatWebSocketService(
                websocket=websocket,
                connection_manager=await container.
                    get_chat_websocket_connection_manager(),
                subscription_service=await container.
                    get_redis_chat_subscription_service(),
                message_handler=await container.
                    get_message_websocket_handler(),
                chat_repository=container.chat_repository,
            )

            await service.start(current_user_id)

            while True:
                data = await websocket.receive_json()
                try:
                    message_in = MessageCreate(
                        chat_id=data.get('chat_id'),
                        content=data.get('content')
                    )
                except ValidationError as e:
                    raise WebSocketException(str(e))

                await service.handle_message(current_user_id, message_in)
    except WebSocketException as e:
        await websocket.send_json({
            'type': 'error',
            'message': e.message
        })
        await websocket.close()
    except WebSocketDisconnect:
      await service.stop(current_user_id)
