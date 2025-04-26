import logging
import uuid
from datetime import datetime
from typing import Dict

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import tools_condition

from agents.common import CustomToolNode
from agents.models import OpenAIModel
from agents.tools import price_lookup_tools, receipttools

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
        self.model = model.bind_tools(receipttools.get_tools() + price_lookup_tools.get_tools())

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


class NotDefinedNode:
    """
    A node that is not defined. This is a placeholder for the graph.
    """

    def __init__(self):
        logger.info("NotDefinedNode initialized")

    def run(self, state: ChatState) -> ChatState:
        logger.info(f"NotDefinedNode run invoked with state: {state}")
        return state


class MessageClassifier:
    """
    Classifies messages as 'upload', 'chat', or 'planner' using an LLM. Reuses the model and prompt for efficiency.
    """

    model_executor: None

    def __init__(self):
        model = OpenAIModel(use_cache=False).get_model()
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        """
                    Classify the following user message as one of: 'upload', 'chat', or 'planner' based on the following criteria:
                    1. if the message is a request to upload, scan or process a receipt file, classify it as 'upload'.
                    2. if the message is about meal planning, classify it as "planner".
                    3. anything else should be classified as "chat" by defaults.

                    Reply with only one of these words. Do not include anything else in your response.
                    """
                    )
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        self.model_executor = prompt | model
        logger.info("MessageClassifier initialized")

    def classify(self, message: str) -> str:
        logger.info(f"MessageClassifier classify invoked with message: {message}")
        result = self.model_executor.invoke({"messages": [HumanMessage(content=message)]})
        value = result.content.strip().lower()
        logger.info(f"MessageClassifier result: {result}")
        return value


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
        self.classifier = MessageClassifier()
        self.initialize()

        # Create a default config if none is provided
        if config is None:
            config = {"configurable": {"thread_id": uuid.uuid4()}}
            logger.info(f"Using default ChatManager configuration: {config}")

        self.config = config

    def classify_message(self, state: ChatState) -> str:
        logger.info("classify_message called with state: %s", state)
        message = state["messages"][-1].content
        value = self.classifier.classify(message)
        logger.info(f"Classified message '{message}' as '{value}'")
        if value == "upload":
            return "receipt"
        elif value == "chat":
            return "chat_agent"
        elif value == "planner":
            return "planner"
        else:
            return "chat_agent"  # fallback

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

        tool_node = CustomToolNode(tools=receipttools.get_tools() + price_lookup_tools.get_tools())
        workflow.add_node("tools", tool_node.run)

        # Add placeholder nodes for receipt and planner
        workflow.add_node("receipt", NotDefinedNode().run)
        workflow.add_node("planner", NotDefinedNode().run)

        # Conditional routing at START
        workflow.add_conditional_edges(START, self.classify_message)

        # Add the rest of the edges
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
