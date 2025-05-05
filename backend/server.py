import logging
import os

import uvicorn
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from dotenv import load_dotenv
from fastapi import FastAPI

from agents.langgraphapp import main_graph
from common.logging import configure_logging
from common.server.upload_router import upload_router

load_dotenv(verbose=True)


configure_logging(logging.DEBUG)

app = FastAPI()
sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="mighty_assistant",
            graph=main_graph,
        )
    ],
)

# CopilotKit integration
add_fastapi_endpoint(app, sdk, "/copilotkit", use_thread_pool=False)

# Register the upload router
app.include_router(upload_router, prefix="/api")


def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
