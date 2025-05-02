from typing import List

from copilotkit.state import CopilotKitState
from langgraph.graph import START, StateGraph

from agents.chat import ChatFlow, ChatState
from agents.common import make_classifier
from agents.mealplanner import MealPlannerFlow, MealPlannerState
from agents.receiptanalyzer import ReceiptAnalyzerFlow, ReceiptState


# overall global state
class GlobalState(CopilotKitState):
    last_receipt: None
    last_meal_plan: None
    last_shopping_list: None
    items_lookup: List[dict] = None

    def make_instance():
        return GlobalState(messages=[], last_meal_plan=None, last_shopping_list=None, last_receipt=None)


class MainGraph:
    def __init__(self, config=None):
        self.config = config

    def as_subgraph(self):
        # chat graph
        chat_flow = ChatFlow()
        chat_graph = chat_flow.as_subgraph().compile()

        # meal planner graph
        meal_planner_flow = MealPlannerFlow()
        meal_planner_graph = meal_planner_flow.as_subgraph().compile()

        # receipt processing graph
        receipt_processing_flow = ReceiptAnalyzerFlow()
        receipt_processing_graph = receipt_processing_flow.as_subgraph().compile()

        main_flow = StateGraph(state_schema=GlobalState)

        def chat_graph_node(global_state: GlobalState) -> dict:
            # initialize the new state
            chat_state = ChatState.make_instance()
            chat_state["messages"] = global_state["messages"].copy()
            chat_state["input"] = global_state["messages"][-1]

            # Run the chat_graph with the converted state
            chat_result = chat_graph.invoke(chat_state, config=self.config)

            # let langgraph update the state with the new messages
            return {
                "messages": chat_result["messages"],
                "items_lookup": chat_result["items"],
            }

        def meal_planner_graph_node(global_state: GlobalState) -> dict:
            # initialize the new state
            meal_planner_state = MealPlannerState.make_instance()
            meal_planner_state["messages"] = global_state["messages"].copy()

            # Run the meal_planner with the converted state
            meal_planner_result = meal_planner_graph.invoke(meal_planner_state, config=self.config)

            # let langgraph update the state with the new messages
            return {
                "last_meal_plan": meal_planner_result["plan"],
                "last_shopping_list": meal_planner_result["shopping_list"],
                "messages": meal_planner_result["messages"],
            }

        def receipt_processing_graph_node(global_state: GlobalState) -> dict:
            # initialize the new state and harcode the image path for now
            receipt_processing_state = ReceiptState.make_instance()
            receipt_processing_state["receipt_image_path"] = "./data/samples/receipt_sample_1_small.jpg"

            # Run the meal_planner with the converted state
            receipt_processing_result = receipt_processing_graph.invoke(receipt_processing_state, config=self.config)

            # let langgraph update the state with the new messages
            return {
                "messages": receipt_processing_result["messages"],
                "last_receipt": receipt_processing_result["receipt"],
            }

        # main_flow.add_node("chat", chat_graph)
        main_flow.add_node("chat", chat_graph_node)
        main_flow.add_node("meal_planner", meal_planner_graph_node)
        main_flow.add_node("receipt_processing", receipt_processing_graph_node)

        # Routing configuration for the decider, as a dictionary:
        # { "target node": "routing description, gets appended to the prompt for the LLM to decide." }
        classifier_routes = {
            "meal_planner": "If the message is about meal planning. Example: I want to plan my meals for the week.",
            "receipt_processing": "If the message is a request to upload, scan or process a new receipt file, and only about that. Examples: I want to upload a receipt or can you help me process a receipt?",
            "chat": "Everything else, including questions about prices, or past receipts. Example: I want to chat with you.",
        }
        main_flow.add_conditional_edges(START, make_classifier(routing_map=classifier_routes, default_node="chat"))

        return main_flow
