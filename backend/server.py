import logging
import os

import uvicorn
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from dotenv import load_dotenv
from fastapi import FastAPI

from agents.langgraphapp import main_graph
from common.logging import configure_logging

load_dotenv()


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

add_fastapi_endpoint(app, sdk, "/copilotkit", use_thread_pool=False)


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}


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
