import importlib
import logging
from typing import TypedDict

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.memory import MemorySaver

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s | %(levelname)-8s | access: %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        "webapp": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "agents": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "common": {"handlers": ["default"], "level": "INFO", "propagate": False},
    },
}

logging.config.dictConfig(logging_config)


def get_config():
    return {"configurable": {"thread_id": "1"}}


def llm_response_to_graph_response(llm_response):
    """
    Convert the LLM response to a GraphResponse that can be serialized to JSON

    Args:
        llm_response (dict): The LLM response.

    Returns:
        dict: The graph response.
    """
    last_message = llm_response["messages"][-1]
    r = GraphResponse(
        status="completed",
        data={
            "response": last_message.content.strip(),
        },
    )

    return r


"""
Payload for graph responses, with the following fields:
- `status`: status of graph, e.g., "running", "interrupted", "completed", etc
- `data`: The data returned by the server, if any. Depends on the functionality that was called.
"""


class GraphResponse(TypedDict):
    status: str
    data: dict

    def make_instance():
        return GraphResponse(status=None, data={})


class GraphServer:
    graph = None
    app = None

    def __init__(self, graph_module: str):
        memory_checkpointer = MemorySaver()
        workflow = self._load_export_from_string(graph_module)
        self.graph = workflow.compile(checkpointer=memory_checkpointer)

        self.app = FastAPI()
        self._setup_routers()
        # Optionally allow CORS for development
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # can be used to invoke the graph directly
    def invoke_graph(self, input_data):
        return self.graph.invoke(input_data)

    def _load_export_from_string(self, path: str):
        module_path, export_name = path.split(":")
        module = importlib.import_module(module_path)
        return getattr(module, export_name)

    def _setup_routers(self):
        # Graph meta router
        graph_meta_router = APIRouter(prefix="/meta", tags=["graph-meta"])

        @graph_meta_router.get("/state")
        def get_state():
            try:
                # Replace with actual state retrieval logic if available
                state = getattr(self.graph, "state", {})
                return {"state": state}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @graph_meta_router.get("/history")
        def get_history():
            try:
                history = getattr(self.graph, "history", [])
                return {"history": history}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @graph_meta_router.get("/graph")
        def get_graph():
            try:
                return self.graph.get_graph().to_json()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        self.app.include_router(graph_meta_router)

        # Application router
        app_router = APIRouter()

        @app_router.post("/invoke")
        def invoke_graph(payload: dict):
            try:
                result = self.graph.invoke(payload, config=get_config())
                response = llm_response_to_graph_response(result)
                return response

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        self.app.include_router(app_router)

        # Streaming router (mounted at root, no prefix)
        stream_router = APIRouter()

        @stream_router.websocket("/ws")
        async def stream_graph(websocket: WebSocket):
            await websocket.accept()
            try:
                # Receive initial message from client (should be JSON with 'text' or input data)
                request = await websocket.receive_json()
                # Async stream graph events using the supported stream method
                async for event in self.graph.astream(request, config=get_config()):
                    # response = llm_response_to_graph_response(event)

                    response = GraphResponse(status="running")

                    for node_id, value in event.items():
                        response["node_id"] = node_id
                        if isinstance(value, dict) and value.get("messages", []):
                            last_message = value["messages"][-1]
                            if isinstance(last_message, dict) or last_message.type != "ai":
                                continue
                            response["data"] = {"message": f"Response: {node_id}: {last_message.content}"}

                        if "__interrupt__" in node_id:
                            response["status"] = "interrupted"
                            response["data"] = {"message": f"Response: {node_id}: {value[-1].value}"}

                        await websocket.send_json(response)

            except WebSocketDisconnect:
                pass
            except Exception as e:
                await websocket.send_json({"error": str(e)})
            finally:
                await websocket.close()

        self.app.include_router(stream_router)

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the FastAPI server using uvicorn."""
        uvicorn.run(self.app, host=host, port=port)
