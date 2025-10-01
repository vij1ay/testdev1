# api/websocket.py
import traceback
import asyncio
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import importlib
from app_logger import logger
from websocket.manager import WebSocketManager
# Ensure handlers are imported so they can be found
from websocket.handlers import chat_handler

handler_map = {
    "chat": chat_handler,
    # Add other handlers here as needed
}

router = APIRouter(prefix="/ws", tags=["WebSocket"])
ws_manager = WebSocketManager()


def get_handler_module(module_name: str):
    """Dynamically import a handler module from the websocket.handlers package."""
    try:
        return handler_map.get(module_name)
    except Exception as e:
        logger.error(
            f"Error importing handler module '{module_name}': {str(e)}")
        return None


def validate_user(user_id: str):
    # Placeholder for user validation logic
    # In a real application, check against a database or authentication service
    # valid_users = {"user1", "user2", "user3"}
    # return user_id in valid_users
    return True  # For now, assume all users are valid


@router.websocket("/{handler}/{user_id}/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, handler: str, user_id: str, thread_id: str):
    print("\n\nwebsocket_endpoint >> ", handler,
          user_id, thread_id, websocket.app)
    if not validate_user(user_id):
        await websocket.close(code=1008)
    try:
        print("\n\nhandler >> ", handler)
        module = get_handler_module(handler)
        if not module:
            await websocket.accept()
            await websocket.send_text(f"Handler '{handler}' not found.")
            await websocket.close(code=1003)
            return

        if not hasattr(module, "handle"):
            await websocket.accept()
            await websocket.send_text(f"Handler '{handler}' is invalid.")
            await websocket.close(code=1003)
            return

        await ws_manager.accept(user_id, thread_id, websocket)
        try:
            session = module.conversation_mgr.get_session(thread_id)
            previous_messages = session.get("messages", []) if session else []
            print("previous_messages >>>> ", len(previous_messages))
            if previous_messages:
                await ws_manager.send_message(
                    thread_id,
                    {
                        "type": "previous_messages",
                        "message_list": previous_messages,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
        except Exception as e:
            logger.error(f"Error retrieving previous messages: {str(e)}")
        try:
            # Keep connection open and handle messages
            while True:
                data = await websocket.receive_json()
                logger.info(
                    f"Received message on thread {thread_id}: {data}",
                )
                # validate thread ID, if not valid, send error and close connection
                # Revalidate thread ID with each message
                # valid_thread_result = await thread_service.validate_thread_id(user_id, thread_id)
                # Placeholder for actual validation
                valid_thread_result = {"is_valid": True}
                if not valid_thread_result.get("is_valid", False):
                    # Thread ID has expired during the session
                    response = {
                        "type": "error",
                        "message": "Thread ID has expired. Please request a new thread ID.",
                        "code": "THREAD_EXPIRED",
                    }
                    await ws_manager.send_message(thread_id, response)
                    break

                # Call the handler’s entrypoint
                await module.handle(websocket.app, thread_id, user_id, data)
                # Prevent tight loop if handler is too fast
                await asyncio.sleep(0.5)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for thread {thread_id}")
            await ws_manager.disconnect(thread_id)
        finally:
            # Ensure we clean up the connection
            await ws_manager.disconnect(thread_id)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {handler}/{user_id}/{thread_id}")
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
        print(f"Error traceback: {traceback.format_exc()}")
        await websocket.close(code=1011)
