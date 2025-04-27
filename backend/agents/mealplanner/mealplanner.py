import logging

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from pydantic import BaseModel, Field

from agents.models import OpenAIModel

logger = logging.getLogger(__name__)


class MealPlannerState(BaseModel):
    messages: list = Field(default=[], description="List of messages exchanged with the user.")
    preferences: str = Field(
        default=None, description="User preferences for meal planning. Populated by the LLM during the process."
    )
    user_input: str = Field(default=None, description="User input")
    budget: str = Field(default=None, description="User's budget")
    plan: list = Field(default=None, description="Generated meal plan")
    shopping_list: dict = Field(default=None, description="Generated shopping list with prices")
    ready_to_plan: bool = Field(default=False, description="Flag indicating if the meal planner is ready to generate a plan")
    additional_input_required: str = Field(default=None, description="Additional user input, as required by the LLM")


class MealPlannerFlow:
    """
    Handles the multi-step meal planning interaction:
    1. Collects user preferences (budget, meals, ingredients, etc.)
    2. Finds suitable recipes
    3. Builds a menu for the week
    4. Generates a shopping list with price lookup
    """

    def __init__(self, llm_model=None):
        self.llm_model = llm_model or OpenAIModel(use_cache=False).get_model()

    def extract_preferences(self, state: MealPlannerState) -> MealPlannerState:
        # extract user input from most recent message if not set yet
        if state.user_input is None:
            state.user_input = state.messages[-1].content

        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
You are a meal planning assistant. Extract the following information from the user's message if present:
- budget: in euros or a range)
- number of meals: usually provided as an integer, or converted to an integer from an expreession such as "a week's worth of meals" or "a meal for tonight"
- number of people: in order to plan the amounts
- preferences: ingredients, dietary restrictions, recipe types, e.g., "italian food", "indian" or "vegetarian"
Return the extracted information as a string including the data above, as well as anything else you can infer from the message.
"""
                ),
                ("human", "User input: {user_input}\nPreferences gathered so far: {preferences}\n"),
                ("human", "{messages}"),
            ]
        )

        # add logic for calling the llm_model
        prompt = prompt_template.invoke(
            {"user_input": state.user_input, "preferences": state.preferences, "messages": state.messages}
        )

        logger.debug(f"Extraction prompt: {prompt}")

        result = self.llm_model.invoke(prompt)
        preferences = result.content.strip()
        logger.debug(f"Extracted preferences: {preferences}")

        # store the preferences so far in the state
        state.messages.append(result)
        state.preferences = preferences

        return state

    def ask_for_missing(self, state: MealPlannerState) -> MealPlannerState:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                    You are a meal planning assistant. Given the following preferences extracted so far as well as the user's original request,
                    determine if all required information for meal planning has been provided.
                    If everything is present, reply only with 'ready'. If something is missing, reply with a single message that should be shown
                    to the user to collect the missing information. Be as specific as possible when requesting additional information.

                    Do not explain your reasoning, just reply with the message for the user or 'ready'.
                """
                ),
                ("human", "User input: {user_input}\nPreferences gathered so far: {preferences}"),
            ]
        )

        prompt = prompt_template.invoke({"user_input": state.user_input, "preferences": state.preferences})

        result = self.llm_model.invoke(prompt)
        state.messages.append(result)
        response = result.content.strip()
        if response.lower() == "ready":
            state.ready_to_plan = True
            return state
        else:
            # state.messages.append(AIMessage(content=response))
            # trigger an interrupt to ask the user for more information, which will depend
            # on what the LLM thinks it needs

            # response is what the LLM replied, with additional context around what is still missing
            state.additional_input_required = response

            # When the graph restarts, interrupt(...) no longer causes an exception but returns the
            # value that the user provided via a Command object
            additional_input = interrupt(response)
            if additional_input is not None:
                state.messages.append(HumanMessage(content=additional_input))

        return state

    def is_ready(self, state: MealPlannerState) -> bool:
        return state.ready_to_plan

    def build_plan(self, state: MealPlannerState) -> MealPlannerState:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                    You are a meal planner. Given the following preferences, generate a meal plan for the week. For each meal, list the meal name and 3-5 ingredients. Return a JSON array of objects with keys: meal, ingredients (list).
                    Do not wrap your response in markdown, just sent JSON as a plain string with no formatting at all."""
                ),
                ("human", "User input: {user_input}\nPreferences gathered so far: {preferences}\n"),
            ]
        )
        prompt = prompt_template.invoke({"user_input": state.user_input, "preferences": state.preferences})
        result = self.llm_model.invoke(prompt)
        import json

        try:
            state.plan = json.loads(result.content)
            logger.debug(f"Generated meal plan: {state.plan}")
        except Exception as e:
            logger.error(f"This should not happen! There was an error parsing the JSON response with the meal plan: {e}")
            state.plan = []
        return state

    def generate_shopping_list(self, state: MealPlannerState) -> MealPlannerState:
        shopping_list = {}
        for meal in state.plan or []:
            for ingredient in meal["ingredients"]:
                # price = self.price_lookup_tool.lookup(ingredient)
                shopping_list[ingredient] = 3.0
        state.shopping_list = shopping_list
        return state

    def format_response(self, state: MealPlannerState) -> MealPlannerState:
        from langchain_core.messages import AIMessage

        plan = state.plan or []
        shopping_list = state.shopping_list or {}
        response = "Here is your meal plan:\n"
        for meal in plan:
            response += f"- {meal['meal']}: {', '.join(meal['ingredients'])}\n"
        response += "\nShopping list with prices:\n"
        for ingredient, price in shopping_list.items():
            response += f"- {ingredient}: {price}\n"
        state.messages.append(AIMessage(content=response))
        return state

    def as_subgraph(self):
        workflow = StateGraph(state_schema=MealPlannerState)

        # Nodes
        workflow.add_node("extract_preferences", self.extract_preferences)
        workflow.add_node("ask_for_missing", self.ask_for_missing)
        workflow.add_node("build_plan", self.build_plan)
        workflow.add_node("generate_shopping_list", self.generate_shopping_list)
        workflow.add_node("format_response", self.format_response)
        workflow.add_edge(START, "extract_preferences")

        # Edges
        workflow.add_edge("extract_preferences", "ask_for_missing")

        def ready_cond(state):
            return "build_plan" if self.is_ready(state) else "extract_preferences"

        workflow.add_conditional_edges("ask_for_missing", ready_cond)
        workflow.add_edge("build_plan", "generate_shopping_list")
        workflow.add_edge("generate_shopping_list", "format_response")
        workflow.add_edge("format_response", END)

        return workflow


class DummyPriceLookupTool:
    def lookup(self, ingredient: str) -> str:
        # Dummy price lookup
        return "2.00"
