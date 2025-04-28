import logging

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import interrupt

from agents.common import make_tool_node
from agents.models import OpenAIModel
from agents.pricecomparison import price_lookup_tools

logger = logging.getLogger(__name__)


class MealPlannerState(MessagesState):
    preferences: str
    user_input: str
    plan: list
    shopping_list: dict
    ready_to_plan: bool
    additional_input_required: str

    # factory meyhod to provide default values
    def make_instance():
        return MealPlannerState(
            messages=[],
            preferences=None,
            user_input=None,
            plan=[],
            shopping_list=None,
            ready_to_plan=False,
            additional_input_required=None,
        )


class MealPlannerFlow:
    """
    Handles the multi-step meal planning interaction:
    1. Collects user preferences (budget, meals, ingredients, etc.)
    2. Finds suitable recipes
    3. Builds a menu for the week
    4. Generates a shopping list with price lookup
    """

    llm_model: None

    def __init__(self, llm_model=None):
        llm_model = llm_model or OpenAIModel(use_cache=False).get_model()
        # allow the model to do price lookups
        self.llm_model = llm_model.bind_tools(self.get_tools())

    def get_tools(self) -> list:
        return price_lookup_tools.get_tools()

    def extract_preferences(self, state: MealPlannerState):
        # extract user input from most recent message if not set yet
        messages = state["messages"].copy()
        if state["user_input"] is None:
            state["user_input"] = messages[-1].content

        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
You are a meal planning assistant. Extract the following information from the user's message if present:
- budget: in euros or a range)
- number of meals: usually provided as an integer, or converted to an integer from an expreession such as "a week's worth of meals" or "a meal for tonight"
- number of people: in order to plan the amounts
- preferences: ingredients, dietary restrictions (optional, user may have no restrictions), recipe types, e.g., "italian food", "indian" or "vegetarian"

Return the extracted information as a string including the data above, as well as anything else you can infer from the message.

Do not ask for more than 4 pieces of information all together, otherwise the user may be overwhelmed. If you're still missing something, please suggest a sensible option.
"""
                ),
                ("human", "User input: {user_input}\nPreferences gathered so far: {preferences}\n"),
                ("human", "{messages}"),
            ]
        )

        # add logic for calling the llm_model
        prompt = prompt_template.invoke(
            {"user_input": state["user_input"], "preferences": state["preferences"], "messages": messages}
        )

        logger.debug(f"Extraction prompt: {prompt}")

        result = self.llm_model.invoke(prompt)
        preferences = result.content.strip()
        messages.append(result)
        logger.debug(f"Extracted preferences: {preferences}")

        # store the preferences so far in the state
        # state.messages.append(result)
        # state.preferences = preferences

        return {
            "messages": messages,
            "preferences": preferences,
        }

    def ask_for_missing(self, state: MealPlannerState):
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                    You are a meal planning assistant. Given the following preferences extracted so far as well as the user's original request,
                    determine if all required information for meal planning has been provided.
                    If everything is present, reply only with 'ready'. If something is missing, reply with a single message that should be shown
                    to the user to collect the missing information. Be as specific as possible when requesting additional information.

                    Do not try to collect more than 4 pieces of information all together, otherwise the user may be overwhelmed. If you're still missing something,
                    please suggest a sensible option.

                    Do not explain your reasoning, just reply with the message for the user or 'ready'.
                """
                ),
                ("human", "User input: {user_input}\nPreferences gathered so far: {preferences}"),
                ("placeholder", "{messages}"),
            ]
        )

        prompt = prompt_template.invoke(
            {"user_input": state["user_input"], "preferences": state["preferences"], "messages": state["messages"]}
        )

        messages = state["messages"].copy()

        result = self.llm_model.invoke(prompt)
        response = result.content.strip()
        messages.append(result)

        response_state = {}
        if response.lower() == "ready":
            response_state["ready_to_plan"] = True
        else:
            # trigger an interrupt to ask the user for more information, which will depend
            # on what the LLM thinks it needs

            # response is what the LLM replied, with additional context around what is still missing
            response_state["additional_input_required"] = response

            # When the graph restarts, interrupt(...) no longer causes an exception but returns the
            # value that the user provided via a Command object
            additional_input = interrupt(response)
            if additional_input is not None:
                messages.append(HumanMessage(content=additional_input))
                response_state["messages"] = messages

        return response_state

    def is_ready(self, state: MealPlannerState) -> bool:
        return state["ready_to_plan"]

    def build_plan(self, state: MealPlannerState):
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                    You are a meal planner. Given the following preferences, generate a meal plan for the week. For each meal, list the meal name and the key ingredients.
                    Return a JSON array of objects with keys: meal, ingredients (list). Do not look up any pricess, just provide the meal plan.
                    Do not wrap your response in markdown, just send JSON as a plain string with no formatting at all."""
                ),
                ("human", "User input: {user_input}\nPreferences gathered so far: {preferences}\n"),
            ]
        )
        prompt = prompt_template.invoke({"user_input": state["user_input"], "preferences": state["preferences"]})
        result = self.llm_model.invoke(prompt)

        try:
            import json

            plan = json.loads(result.content)
            logger.debug(f"Generated meal plan: {plan}")
        except Exception as e:
            plan = []
            logger.error(f"This should not happen! There was an error parsing the JSON response with the meal plan: {e}")

        return {"plan": plan}

    def generate_shopping_list(self, state: MealPlannerState):
        """
        Calls the LLM to generate a shopping list with approximate prices using the s_kaupat_price_source tool.
        """
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                You are a meal planning assistant.
                Given the following meal plan and user preferences, generate a shopping list with approximate prices for each ingredient provided in the meal plan.

                - description of the item
                - matched product name; from tool calling, so that the user can identify the product in the shelves
                - quantity needed
                - unit of measurement
                - price of the item; use the price lookup tool provided to you to get the price

                Use the tools available to you to look up the prices of ingredients.
                Return the result as a JSON object.
                Do not wrap your response in markdown, just send JSON as a plain string with no formatting at all.
            """
                ),
                ("human", "Meal plan: {plan}\nPreferences: {preferences}"),
                ("human", "{messages}"),
            ]
        )

        import json

        plan = state["plan"]
        preferences = state["preferences"]
        messages = state["messages"].copy()
        prompt = prompt_template.invoke({"plan": plan, "preferences": preferences, "messages": messages})
        result = self.llm_model.invoke(prompt)
        messages.append(result)

        shopping_list = {}
        try:
            shopping_list = json.loads(result.content)
            logger.debug(f"Generated shopping list with prices: {shopping_list}")
        except Exception as e:
            logger.error(f"Error parsing shopping list JSON: {e}")

        return {
            "messages": messages,
            "shopping_list": shopping_list,
        }

    def format_response(self, state: MealPlannerState):
        from langchain_core.messages import AIMessage

        plan = state["plan"]
        shopping_list = state["shopping_list"]
        messages = state["messages"].copy()

        response = "Here is your meal plan:\n"
        for meal in plan:
            response += f"- {meal['meal']}: {', '.join(meal['ingredients'])}\n"
        response += "\nShopping list with prices:\n"
        for ingredient, price in shopping_list.items():
            response += f"- {ingredient}: {price}\n"

        messages.append(AIMessage(content=response))
        return {"messages": messages}

    # TODO: this could be generalized and then moved to a better place
    def pricing_tools_condition(self, state, messages_key="messages"):
        if isinstance(state, list):
            ai_message = state[-1]
        elif isinstance(state, dict) and (messages := state.get(messages_key, [])):
            ai_message = messages[-1]
        elif messages := getattr(state, messages_key, []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return "format_response"

    def as_subgraph(self):
        workflow = StateGraph(state_schema=MealPlannerState)

        # Nodes
        workflow.add_node("extract_preferences", self.extract_preferences)
        workflow.add_node("ask_for_missing", self.ask_for_missing)
        workflow.add_node("build_plan", self.build_plan)
        workflow.add_node("generate_shopping_list", self.generate_shopping_list)
        workflow.add_node("tools", make_tool_node(messages_key="messages", tools=self.get_tools()))
        workflow.add_node("format_response", self.format_response)

        # Edges
        workflow.add_edge(START, "extract_preferences")
        workflow.add_edge("extract_preferences", "ask_for_missing")
        workflow.add_edge("tools", "generate_shopping_list")
        workflow.add_conditional_edges("generate_shopping_list", self.pricing_tools_condition)

        def ready_cond(state):
            return "build_plan" if self.is_ready(state) else "extract_preferences"

        workflow.add_conditional_edges("ask_for_missing", ready_cond)
        workflow.add_edge("build_plan", "generate_shopping_list")
        workflow.add_edge("format_response", END)

        return workflow
