# main.py
import json
import webbrowser
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from app_logger import logger
from agent_tools.planner import create_planner_graph
from utils import get_redis_instance, get_redis_async_instance, environment
import websocket
from config import COMPANY_NAME, CHATBOT_NAME, COMPANY_MOTO

# Added imports for Redis checkpointer
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.checkpoint.memory import MemorySaver

redis_client = get_redis_instance()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    if environment.get("REDIS_HOST", ""):
        try:
            # 1. Initialize Redis Checkpointer for LangGraph if enabled
            async_redis_cli = get_redis_async_instance()

            # 2. Instantiate AsyncRedisSaver with the connection object
            checkpointer = AsyncRedisSaver(redis_client=async_redis_cli)

            # 3. Call asetup() to initialize indices
            await checkpointer.asetup()

        except Exception as e:
            logger.error(f"Failed to initialize Redis Checkpointer: {str(e)}")
            # Decide how to handle failure: exit, raise, or fallback?
            # For now, we'll log and continue without a checkpointer
            checkpointer = None
            if async_redis_cli:
                await async_redis_cli.aclose()
                async_redis_cli = None
            logger.info(
                "Redis Checkpointing Errored. Using MemorySaver.")
            checkpointer = MemorySaver()  # type: ignore

    else:
        logger.info("Redis Checkpointing is disabled. Using MemorySaver.")
        checkpointer = MemorySaver()  # type: ignore

    # Initialize the planner graph *after* checkpointer setup
    # Pass the checkpointer instance (or None) to the graph creation function

    app.state.planner_graph = create_planner_graph(checkpointer=checkpointer)
    logger.info("Planner graph initialized")

    yield  # Application runs here

    # --- Cleanup ---
    logger.info("Shutting down application")
    if async_redis_cli:
        await async_redis_cli.close()
        logger.info("Redis connection closed.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        graph: The ChatbotRagRetrieval instance to be used by the app.

    Returns:
        FastAPI: The configured FastAPI application.
    """

    app = FastAPI(
        title="MultiAgent Boilerplate API",
        description="API for interacting with the MultiAgent Boilerplate",
        version="1.0.0",
        lifespan=lifespan  # Register the lifespan context manager
    )

    # Serve static files from assets directory
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")

    @app.get("/", response_class=HTMLResponse)
    async def serve_chat() -> HTMLResponse:
        """Serve the chat interface HTML page.

        Returns:
            HTMLResponse: The rendered chat interface HTML
        """
        with open("assets/chat.html", "r", encoding="utf-8") as f:
            content = f.read()
            content = content.replace("@@@company_name@@@", COMPANY_NAME)
            content = content.replace("@@@chatbot_name@@@", CHATBOT_NAME)
            content = content.replace("@@@company_moto@@@", COMPANY_MOTO)
            return HTMLResponse(content=content)

    app.include_router(websocket.router)

    @app.get("/leads_generated", response_class=HTMLResponse)
    async def serve_leads_generated() -> HTMLResponse:
        """Serve the leads generated HTML page.

        Returns:
            HTMLResponse: The rendered leads generated HTML
        """
        with open("assets/leads_generated.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    @app.get("/get_lead_datalist", response_class=JSONResponse)
    async def get_lead_datalist() -> JSONResponse:
        """Serve the leads generated HTML page.

        Returns:
            HTMLResponse: The rendered leads generated HTML
        """
        leads = redis_client.hgetall("leads_generated")
        # return json response
        ret = []
        for lead in leads:
            ret.append(json.loads(redis_client.hget("leads_generated", lead)))
        return JSONResponse(content=ret)

    app.include_router(websocket.router)

    for route in app.routes:
        # REST has .methods, WS doesn't
        methods = getattr(route, "methods", ["WEBSOCKET"])
        print(f"{methods} -> {route.path}")

    return app


def main() -> None:
    """Initialize and start the multiagent server.

    This function:
    1. Creates the Websocket instance
    2. Initializes the FastAPI application
    3. Opens the chat interface in the default web browser
    4. Starts the uvicorn server
    """
    # Initialize the Websocket instance
    # graph = ChatbotRagRetrieval()
    # Create the FastAPI application
    # fastapi_app = create_app(graph)
    webserver_port = 8000
    fastapi_app = create_app()

    # Open chat interface in browser
    # webbrowser.open(f'http://localhost:{webserver_port}')

    # Start the server
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=webserver_port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
