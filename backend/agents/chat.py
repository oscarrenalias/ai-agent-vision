import logging
import uuid
from datetime import datetime
from typing import Dict

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import tools_condition

from agents.tools import price_lookup_tools, receipttools, simpletools

from .models import OpenAIModel

logger = logging.getLogger(__name__)


class ChatState(MessagesState):
    pass


class ChatAgent:
    # Keeps track of the LLM model
    model: None

    def __init__(self):
        logger.info("Chat initialized")
        model = OpenAIModel(use_cache=False).get_model()

        # bind with tools and keep in the class
        self.model = model.bind_tools(simpletools.get_tools() + receipttools.get_tools() + price_lookup_tools.get_tools())

    def get_primary_assistant_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="You are a helfpul assistant that can use tools to perform requests.\nCurrent time: {time}."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(time=datetime.now)

    def run(self, state: ChatState) -> ChatState:
        # todo: check if this will scale during repeated invocations
        logger.info(f"ChatAgent run invoked with state: {state}")

        model_executor = self.get_primary_assistant_prompt() | self.model

        result = model_executor.invoke(state["messages"])
        logger.info(f"LLM invoke result: {result}")
        state["messages"].append(result)

        logger.info(f"ChatState result returned: {state}")
        return state


class CustomToolNode:
    """Custom tool executor that preserves message history."""

    def __init__(self, tools):
        logger.info(f"CustomToolNod initialized with tools: {tools}")
        self.tools = tools

    def run(self, state: ChatState) -> ChatState:
        """Execute tools while preserving all messages in state."""
        # Get the last message which should contain tool calls
        last_message = state["messages"][-1]
        logger.info(f"CustomToolNode processing {len(last_message.tool_calls)} tool calls")

        # process each tool call and record their results in the messages
        tools_by_name = {tool.name: tool for tool in self.tools}
        for tool_call in last_message.tool_calls:
            tool = tools_by_name[tool_call["name"]]
            tool_msg = tool.invoke(tool_call["args"])
            logger.info(f"Tool call {tool_call['name']}, result: {tool_msg}")
            state["messages"].append(ToolMessage(content=tool_msg, tool_call_id=tool_call["id"]))

        logger.info(f"Tool execution complete. State now has {len(state['messages'])} messages")
        return state


class ChatManager:
    """
    Manages the chat session and handles the conversation flow. Based on StateGraph, uses MemorySaver to save the state.
    """

    graph: StateGraph

    """
    The configuration dict for the ChatManager. It is passed as is to the StateGraph when invoking.
    """
    config: Dict

    def __init__(self, config: Dict = None):
        self.initialize()

        # Create a default config if none is provided
        if config is None:
            config = {"configurable": {"thread_id": uuid.uuid4()}}
            logger.info(f"Using default ChatManager configuration: {config}")

        self.config = config

    def initialize(self):
        """
        Initialize all instance objects
        """
        logger.info("ChatManager initialized")

        # memory checkpointer
        memory = MemorySaver()

        # build graph and edges
        chat_agent = ChatAgent()
        # needs to be StateGraph so that the chatbot remembers previous interactions
        workflow = StateGraph(state_schema=ChatState)
        workflow.add_node("chat_agent", chat_agent.run)

        tool_node = CustomToolNode(tools=simpletools.get_tools() + receipttools.get_tools() + price_lookup_tools.get_tools())
        workflow.add_node("tools", tool_node.run)

        workflow.add_edge(START, "chat_agent")
        workflow.add_edge("tools", "chat_agent")
        workflow.add_conditional_edges("chat_agent", tools_condition)

        self.graph = workflow.compile(checkpointer=memory)

    def run(self, message: str):
        """
        Add the message to the state, and invoke
        """
        initial_state = ChatState(messages=[HumanMessage(content=message)])
        response = self.graph.invoke(initial_state, config=self.config)
        logger.debug(f"Response: {response}")
        return response
