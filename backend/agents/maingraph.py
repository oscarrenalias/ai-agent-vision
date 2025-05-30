import logging
from typing import List

from copilotkit import CopilotKitState
from langgraph.graph import START, StateGraph

from agents.chat import ChatFlow, ChatState
from agents.common import make_classifier
from agents.mealplanner import MealPlannerFlow, MealPlannerState
from agents.receiptanalyzer import ReceiptState
from agents.receiptanalyzer.receiptanalysis import ReceiptAnalysisFlow
from agents.recipes.recipeflow import RecipeFlow, RecipeState

logger = logging.getLogger(__name__)


# overall global state
class GlobalState(CopilotKitState):
    last_receipt: None
    last_meal_plan: None
    last_shopping_list: None
    items_lookup: List[dict] = None
    image_file_path: str = None

    def make_instance():
        return GlobalState(messages=[], last_meal_plan=None, last_shopping_list=None, last_receipt=None, image_file_path=None)


class MainGraph:
    def __init__(self, config=None):
        self.config = config

    def as_subgraph(self):
        # chat graph
        chat_flow = ChatFlow()
        chat_graph = chat_flow.as_subgraph().compile()

        # meal planner graph
        meal_planner_graph = MealPlannerFlow().as_subgraph().compile()
        # receipt processing graph
        receipt_analysis_graph = ReceiptAnalysisFlow().as_subgraph().compile()
        # recipe analysis graph
        recipe_handler_graph = RecipeFlow().as_subgraph().compile()

        main_flow = StateGraph(state_schema=GlobalState)

        async def chat_graph_node(global_state: GlobalState) -> dict:
            # initialize the new state
            chat_state = ChatState.make_instance()
            chat_state["messages"] = global_state["messages"].copy()
            chat_state["input"] = global_state["messages"][-1]

            # Run the chat_graph with the converted state
            chat_result = await chat_graph.ainvoke(chat_state, config=self.config)

            # let langgraph update the state with the new messages
            return {
                "messages": chat_result["messages"],
                "items_lookup": chat_result["items"],
            }

        async def meal_planner_graph_node(global_state: GlobalState) -> dict:
            # initialize the new state
            meal_planner_state = MealPlannerState.make_instance()
            meal_planner_state["messages"] = global_state["messages"].copy()

            # Run the meal_planner with the converted state
            meal_planner_result = await meal_planner_graph.ainvoke(meal_planner_state, config=self.config)

            # let langgraph update the state with the new messages
            return {
                "last_meal_plan": meal_planner_result["plan"],
                "last_shopping_list": meal_planner_result["shopping_list"],
                "messages": meal_planner_result["messages"],
            }

        async def recipe_handler_graph_node(global_state: GlobalState) -> dict:
            state = RecipeState.make_instance()
            state["messages"] = global_state["messages"].copy()
            result = await recipe_handler_graph.ainvoke(state, config=self.config)

            return {"messages": result["messages"]}

        async def receipt_processing_graph_node(global_state: GlobalState) -> dict:
            # initialize the new state and harcode the image path for now
            receipt_processing_state = ReceiptState.make_instance()

            receipt_processing_state["receipt_image_path"] = global_state.get("image_file_path", "")

            logger.info(f"Image file path: {receipt_processing_state['receipt_image_path']}")

            # Run the meal_planner with the converted state
            receipt_processing_result = await receipt_analysis_graph.ainvoke(receipt_processing_state, config=self.config)

            # let langgraph update the state with the new messages
            return {
                "messages": receipt_processing_result["messages"],
                "last_receipt": receipt_processing_result["receipt"],
            }

        # main_flow.add_node("chat", chat_graph)
        main_flow.add_node("chat", chat_graph_node)
        # main_flow.add_node("meal_planner", meal_planner_graph_node)
        main_flow.add_node("receipt_processing", receipt_processing_graph_node)
        main_flow.add_node("recipe_handler", recipe_handler_graph_node)

        # Routing configuration for the decider, as a dictionary:
        # { "target node": "routing description, gets appended to the prompt for the LLM to decide." }
        classifier_routes = {
            "meal_planner": "If the message is about meal planning. Example: I want to plan my meals for the week.",
            "receipt_processing": """If the message is a request to upload, scan or process a new receipt file, and only about that. Examples: I want to upload a receipt or can you help me process a receipt?""",
            "recipe_handler": """If the message looks like a recipe and the user is asking for help extracting a recipe or saving a recipe.
            Example: 'I want to extract a recipe from this text', 'please help me extract a recipe from a web site or URL', or 'can you save this recipe?""",
            "chat": """Everything else, including:
             - questions about prices. Example: 'how much does a banana cost?'
             - searching for recipes. Example: 'can you find recipes with cinnamon?¡
             - past groceries receipts, or questions about receipts. Example 'how much did we spend in March 2025?'
             - general chat questions""",
        }
        main_flow.add_conditional_edges(START, make_classifier(routing_map=classifier_routes, default_node="chat"))

        return main_flow
