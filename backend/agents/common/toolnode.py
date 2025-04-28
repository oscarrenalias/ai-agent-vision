import logging

from langchain_core.messages import ToolMessage
from langgraph.graph import MessagesState
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class CustomToolNode:
    """Custom tool executor that preserves message history."""

    def __init__(self, tools):
        logger.info(f"CustomToolNode initialized with tools: {tools}")
        self.tools = tools

    def run(self, state: BaseModel) -> BaseModel:
        """Execute tools while preserving all messages in state."""
        # Get the last message which should contain tool calls
        last_message = state.messages[-1]
        logger.info(f"CustomToolNode processing {len(last_message.tool_calls)} tool calls")

        # process each tool call and record their results in the messages
        tools_by_name = {tool.name: tool for tool in self.tools}
        for tool_call in last_message.tool_calls:
            tool = tools_by_name[tool_call["name"]]
            tool_msg = tool.invoke(tool_call["args"])
            logger.info(f"Tool call {tool_call['name']}, result: {tool_msg}")
            state.messages.append(ToolMessage(content=tool_msg, tool_call_id=tool_call["id"]))

        logger.info(f"Tool execution complete. State now has {len(state.messages)} messages")
        return state


def make_tool_node(messages_key: str, tools: list):
    def tool_node(state: MessagesState) -> dict:
        """Execute tools while preserving all messages in state."""
        # Get the last message which should contain tool calls
        last_message = state["messages"][-1]
        logger.info(f"Processing {len(last_message.tool_calls)} tool calls")

        # process each tool call and record their results in the messages
        tools_by_name = {tool.name: tool for tool in tools}
        messages = []
        for tool_call in last_message.tool_calls:
            tool = tools_by_name[tool_call["name"]]
            tool_msg = tool.invoke(tool_call["args"])
            logger.debug(f"Tool call {tool_call['name']}, result: {tool_msg}")
            messages.append(ToolMessage(content=tool_msg, tool_call_id=tool_call["id"]))

        logger.info(f"Tool execution complete. State now has {len(messages)} messages")

        return {messages_key: messages}

    return tool_node
