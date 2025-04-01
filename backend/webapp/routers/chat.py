import logging
import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from pydantic import BaseModel

from agents.chat import ChatManager

# Create a module-specific logger
logger = logging.getLogger("webapp.routers.chat")


# Define request and response models
class ChatMessage(BaseModel):
    role: str  # "user", "assistant", or "tool"
    content: str
    tool_call_id: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    chat_id: str
    history: List[ChatMessage]


# Create a router for chat endpoints
router = APIRouter(prefix="/api/chat", tags=["chat"])

# Store active chat sessions with their configurations and ChatManager instances
chat_sessions: Dict[str, Dict] = {}


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the chatbot and get a response.
    If chat_id is not provided, a new chat session will be created.
    """
    # Get or create chat ID and configuration
    chat_id = request.chat_id
    if not chat_id:
        # Create a new chat session with a unique ID
        chat_id = str(uuid.uuid4())

        # Create configuration for the new chat session
        config = {"configurable": {"thread_id": chat_id}}

        # Create a new ChatManager instance for this session
        chat_manager = ChatManager(config=config)

        # Store the session data
        chat_sessions[chat_id] = {"config": config, "history": [], "chat_manager": chat_manager}

        logger.info(f"Created new chat session with ID: {chat_id}")
    elif chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Add user message to history
    user_message = ChatMessage(role="user", content=request.message)
    chat_sessions[chat_id]["history"].append(user_message)

    try:
        # Get the ChatManager instance for this session
        chat_manager = chat_sessions[chat_id]["chat_manager"]

        # Process the message with the session's ChatManager
        response = chat_manager.run(message=request.message)

        # Extract the assistant's response from the last message
        assistant_response = ""
        history = []

        # Convert LangChain messages to our ChatMessage format
        for msg in response["messages"]:
            if isinstance(msg, HumanMessage):
                history.append(ChatMessage(role="user", content=msg.content))
            elif isinstance(msg, AIMessage):
                history.append(ChatMessage(role="assistant", content=msg.content))
                # Get the last assistant message as the response
                assistant_response = msg.content
            elif isinstance(msg, ToolMessage):
                history.append(ChatMessage(role="tool", content=msg.content, tool_call_id=msg.tool_call_id))

        # Update the session history
        chat_sessions[chat_id]["history"] = history

        # Return the response with chat history
        return ChatResponse(message=assistant_response, chat_id=chat_id, history=history)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/history/{chat_id}", response_model=List[ChatMessage])
async def get_chat_history(chat_id: str):
    """
    Get the chat history for a specific chat session.
    """
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return chat_sessions[chat_id]["history"]


@router.delete("/session/{chat_id}")
async def delete_chat_session(chat_id: str):
    """
    Delete a chat session.
    """
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")

    del chat_sessions[chat_id]
    return {"message": "Chat session deleted successfully"}
