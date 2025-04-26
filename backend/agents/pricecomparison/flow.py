import logging
import uuid
from typing import Dict

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition

from agents.common import CustomToolNode
from agents.pricecomparison.agent import PriceComparisonAgent, PriceComparisonState
from agents.pricecomparison.price_lookup_tools import get_tools


class PriceComparisonFlow:
    """
    Manages the chat session and handles the conversation flow. Based on StateGraph, uses MemorySaver to save the state.
    """

    graph: StateGraph
    config: Dict

    def __init__(self, config: Dict = None):
        self.initialize()
        if config is None:
            config = {"configurable": {"thread_id": uuid.uuid4()}}
            logging.getLogger(__name__).info(f"Using default PriceComparisonFlow configuration: {config}")
        self.config = config

    def initialize(self):
        logger = logging.getLogger(__name__)
        logger.info("PriceComparisonFlow initialized")
        memory = MemorySaver()
        chat_agent = PriceComparisonAgent()
        workflow = StateGraph(state_schema=PriceComparisonState)
        workflow.add_node("lookup_agent", chat_agent.run)
        tool_node = CustomToolNode(tools=get_tools())
        workflow.add_node("tools", tool_node.run)
        workflow.add_edge(START, "lookup_agent")
        workflow.add_edge("tools", "lookup_agent")
        workflow.add_conditional_edges("lookup_agent", tools_condition)
        self.graph = workflow.compile(checkpointer=memory)

    def run(self, item: str):
        initial_state = PriceComparisonState(messages=[HumanMessage(content=f"Look up the price of {item}")])
        response = self.graph.invoke(initial_state, config=self.config)
        logging.getLogger(__name__).debug(f"Response: {response}")
        return response
