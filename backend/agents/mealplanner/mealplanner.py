from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import END, START, StateGraph

from agents.models import OpenAIModel


class MealPlannerState(BaseModel):
    messages: list = Field(default_factory=list)
    budget: str = None
    num_meals: int = None
    num_people: int = None
    preferences: str = None
    plan: list = None
    shopping_list: dict = None


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
        self.state = {
            "budget": None,
            "num_meals": None,
            "preferences": None,
            "num_people": None,
            "plan": None,
            "shopping_list": None,
        }

    def extract_preferences(self, state: MealPlannerState) -> MealPlannerState:
        user_input = state.messages[-1].content if state.messages else ""
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
You are a meal planning assistant. Extract the following information from the user's message if present:
- budget (in dollars or a range)
- number of meals (integer)
- number of people (in order to plan the amounts)
- preferences (ingredients, dietary restrictions, or recipe types)
Return a JSON object with keys: budget, num_meals, preferences. If a value is missing, use null.
"""
                ),
                HumanMessage(content=user_input),
            ]
        )
        result = self.llm_model.invoke(prompt.format_prompt().to_messages())
        import json

        try:
            data = json.loads(result.content)
            state.budget = data.get("budget") or state.budget
            state.num_meals = data.get("num_meals") or state.num_meals
            state.preferences = data.get("preferences") or state.preferences
            state.num_people = data.get("num_people") or state.num_people
        except Exception:
            pass
        return state

    def ask_for_missing(self, state: MealPlannerState) -> MealPlannerState:
        from langchain_core.messages import AIMessage

        if not state.budget:
            state.messages.append(AIMessage(content="What is your budget for the week?"))
        elif not state.num_meals:
            state.messages.append(AIMessage(content="How many meals do you want to plan for?"))
        elif not state.preferences:
            state.messages.append(AIMessage(content="Do you have any preferred ingredients or recipes?"))
        return state

    def is_ready(self, state: MealPlannerState) -> bool:
        return all([state.budget, state.num_meals, state.preferences])

    def build_plan(self, state: MealPlannerState) -> MealPlannerState:
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
You are a meal planner. Given the following preferences, generate a meal plan for the week. For each meal, list the meal name and 3-5 ingredients. Return a JSON array of objects with keys: meal, ingredients (list).
Preferences:
- Budget: {budget}
- Number of meals: {num_meals}
- Number of people: {num_people}
- Preferences: {preferences}
"""
                ),
                HumanMessage(content="Generate the meal plan."),
            ]
        )
        formatted = (
            prompt.partial(budget=state.budget, num_meals=state.num_meals, preferences=state.preferences)
            .format_prompt()
            .to_messages()
        )
        result = self.llm_model.invoke(formatted)
        import json

        try:
            state.plan = json.loads(result.content)
        except Exception:
            state.plan = [
                {"meal": f"Meal {i+1} ({state.preferences})", "ingredients": [f"Ingredient {j+1}" for j in range(3)]}
                for i in range(int(state.num_meals or 3))
            ]
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
            return "build_plan" if self.is_ready(state) else END

        workflow.add_conditional_edges("ask_for_missing", ready_cond)
        workflow.add_edge("build_plan", "generate_shopping_list")
        workflow.add_edge("generate_shopping_list", "format_response")
        workflow.add_edge("format_response", END)

        return workflow


class DummyPriceLookupTool:
    def lookup(self, ingredient: str) -> str:
        # Dummy price lookup
        return "$2.00"


class MealPlanner:
    def __init__(self, llm_model=None):
        self.flow = MealPlannerFlow(DummyPriceLookupTool(), llm_model=llm_model)

    def handle(self, user_input: str) -> str:
        # Collect preferences
        ask = self.flow.collect_preferences(user_input)
        if ask != "OK":
            return ask
        # All info collected
        if not self.flow.state["plan"]:
            self.flow.build_plan()
        if not self.flow.state["shopping_list"]:
            self.flow.generate_shopping_list()
        return self.flow.get_response()
