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
from agents.tools import price_lookup_tools

logger = logging.getLogger(__name__)

"""
This agent implements a flow to perform price comparison against other grocers, to determine if there could be cost
savings for a given product elsewhere.

1. A product is provided (beginning of the flow)
2. An LLM is used to normalize the item description so that it's easier to find
3. The item is looked up in one (or more) grocer sites, matching or comparable items are returned, alongside price (via a tool)
4. The LLM figures out if an item would have been cheaper taken into consideration package size, discounts, etc, and returns a recommendation
"""


class PriceComparisonState(MessagesState):
    """
    Name of the item to compare prices for. This is set by the user at the beginning of the flow.
    """

    item_to_compare: str = None


class PriceComparisonAgent:
    # Keeps track of the LLM model
    model: None

    def __init__(self):
        logger.info("PriceComparisonAgent initialized")
        model = OpenAIModel(use_cache=False).get_model()

        # bind with tools and keep in the class
        self.model = model.bind_tools(price_lookup_tools.get_tools())

    def get_primary_assistant_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                    You are a price comparison assistant that can use tools look up prices in other grocer sites,
                    and then figure out if a given item could have been cheaper elsewhere taking into account
                    package size, product description, price per unit.\nCurrent time: {time}.
                    """
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(time=datetime.now)

    def run(self, state: PriceComparisonState) -> PriceComparisonState:
        # todo: check if this will scale during repeated invocations
        logger.info(f"PriceComparisonState run invoked with state: {state}")

        model_executor = self.get_primary_assistant_prompt() | self.model

        result = model_executor.invoke(state["messages"])
        logger.info(f"LLM invoke result: {result}")
        state["messages"].append(result)

        logger.info(f"PriceComparisonState result returned: {state}")
        return state


class PriceComparisonManager:
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
            logger.info(f"Using default PriceComparisonManager configuration: {config}")

        self.config = config

    def initialize(self):
        """
        Initialize all instance objects
        """
        logger.info("PriceComparisonManager initialized")

        # memory checkpointer
        memory = MemorySaver()

        # build graph and edges
        chat_agent = PriceComparisonAgent()
        # needs to be StateGraph so that the chatbot remembers previous interactions
        workflow = StateGraph(state_schema=PriceComparisonState)
        workflow.add_node("lookup_agent", chat_agent.run)

        tool_node = CustomToolNode(tools=price_lookup_tools.get_tools())
        workflow.add_node("tools", tool_node.run)

        workflow.add_edge(START, "lookup_agent")
        workflow.add_edge("tools", "lookup_agent")
        workflow.add_conditional_edges("lookup_agent", tools_condition)

        self.graph = workflow.compile(checkpointer=memory)

    def run(self, item: str):
        """
        Add the message to the state, and invoke
        """
        initial_state = PriceComparisonState(messages=[HumanMessage(content=f"Look up the price of {item}")])
        response = self.graph.invoke(initial_state, config=self.config)
        logger.debug(f"Response: {response}")
        return response
