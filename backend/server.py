# flake8: noqa: E402
import asyncio
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint

# Needed this early so that subsequent imports can use it
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv(verbose=True)

from agents.langgraphapp import main_graph
from common.analytics import listen_for_receipt_changes
from common.logging import configure_logging
from common.server.analytics_router import analytics_router
from common.server.recipes_router import recipes_router
from common.server.upload_router import upload_router

configure_logging(logging.DEBUG)


# required for the async mongo client
@asynccontextmanager
async def lifespan(app):
    loop = asyncio.get_event_loop()
    task = loop.create_task(listen_for_receipt_changes())
    yield
    task.cancel()


# instantiate the FastAPI app with a lifespan context manager
app = FastAPI(lifespan=lifespan)

# Register the application routers with API endpoints
app.include_router(upload_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(recipes_router, prefix="/api")

# CopilotKit integration
sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="mighty_assistant",
            graph=main_graph,
        )
    ],
)
add_fastapi_endpoint(app, sdk, "/copilotkit", use_thread_pool=False)


def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=["agents", "common", "tools"],
    )


if __name__ == "__main__":
    main()
