from fastapi import APIRouter, WebSocket
from pydantic_core import ValidationError
from starlette.websockets import WebSocketDisconnect, WebSocketState

from app.api.dependencies.auth import get_current_user_id_ws
from app.db.session import get_lifespan_db
from app.infrastructure.cache.connection import get_lifespan_redis_client
from app.infrastructure.exceptions.websocket import WebSocketException
from app.schemas.event import WebSocketEvent
from app.services.ws.web_socket_service_container import WebSocketServiceContainer
from app.services.ws.chat_web_socket_service import ChatWebSocketService
from logging import getLogger

logger = getLogger(__name__)
router = APIRouter()


@router.websocket('/ws/chat')
async def chat_websocket(
        websocket: WebSocket,
):
    current_user_id = None
    chat_service = None
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
                redis_token_blacklist_service=container.
                    redis_token_blacklist_service,
                redis=container.redis,
            )

            chat_service = ChatWebSocketService(
                websocket=websocket,
                subscription_service=container.redis_chat_subscription_service,
                message_delivery_service=container.message_delivery_service,
                chat_query_service=container.chat_query_service,
                chat_overview_service=container.chat_overview_service,
                message_handler=container.message_websocket_handler,
                chat_read_service=container.chat_read_service,
            )

            await chat_service.start(current_user_id)

            while True:
                try:
                    data_in = await websocket.receive_json()

                    if not data_in:
                        continue

                    websocket_event = WebSocketEvent(**data_in)

                    await chat_service.websocket_dispatcher.dispatch(
                        current_user_id, websocket_event
                    )
                except WebSocketDisconnect:
                    logger.info(
                        f"WebSocket disconnected for user {current_user_id}")
                    break
                except ValidationError as e:
                    await websocket.send_json({
                        'type': 'error',
                        'message': f'Invalid message format: {e}'
                    })
                except WebSocketException as e:
                    await websocket.send_json({
                        'type': 'error',
                        'message': e.message
                    })
                except Exception as e:
                    logger.error(f'An unexpected exception occurred: {e}',
                                 exc_info=True
                                 )
                    await websocket.send_json({
                        'type': 'error',
                        'message': f'An unexpected error '
                                   f'occurred processing your message'
                    })
    except WebSocketException as e:
        logger.warning(f"WebSocket connection failed: {e.message}")
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {current_user_id}")
        return
    except Exception as e:
        logger.error(f'Critical exception occurred: {e}')
    finally:
        logger.info(f"Cleaning up resources for user {current_user_id}.")
        if chat_service:
            await chat_service.stop()
        if not websocket.client_state == WebSocketState.DISCONNECTED:
            await websocket.close()
