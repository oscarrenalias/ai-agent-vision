import logging
from typing import List, TypedDict

from langchain.tools import tool

logger = logging.getLogger(__name__)


class Meal(TypedDict):
    day: str
    type: str
    name: str
    ingredients: List[str]
    steps: List[str]


class MealPlan(TypedDict):
    name: str
    meals: List[Meal]

    def make_instance(name: str):
        """
        Create an instance of MealPlan with the given name and an empty list of meals.
        """
        return MealPlan(name=name, meals=[])


def get_tools():
    return [
        initialize_meal_plan,
        add_to_meal_plan,
        get_meal_plan,
        get_meal_plan_with_ingredients,
        convert_meal_plan_to_shopping_list,
    ]


@tool
def initialize_meal_plan(state: dict, name: str) -> dict:
    """
    Initializes a meal plan with a given name. This tool should be when the user requests that a new meal plan be created, e.g.,
    "can you create a meal plan for me?", "I want to plan my meals for the week", "please help me plan my meals for the next week", etc.
    The meal plan will be initialized with an empty list of meals, which can then be added to using the add_to_meal_plan tool.

    Inputs:
    - name: A description of the meal plan, e.g., "Weekly Meal plan (only weekday dinners)"

    Outputs:
    - description: A human-readable description of the action taken
    - meals: An empty list of meals to start with
    """
    meal_plan = MealPlan.make_instance(name)
    logger.info("Initializing meal plan")
    return {"description": "Meal plan initialized", "meal_plan": meal_plan}


@tool
def add_to_meal_plan(state: dict, day: str, type: str, name: str, ingredients: List[str] = [], steps: List[str] = []) -> dict:
    """
    This tool adds a meal to the meal plan based on the meal (the recipe), the day of the week,
    and the type of meal. If the recipe is not available, the agent should try to find it using the recipe search tool.

    Inputs:
    - day: The day of the week for which to add the meal
    - type: type of meal: dinner, or lunch
    - name: the name or brief description of the recipe to add to the meal plan.
    - ingredients: a list of ingredients for the meal, provided a list of items, may be empty. If possible, please provide the amounts of each ingredient.
    - steps: List of steps required to prepare the meal. May be empty.

    Outputs:
    - description: A human-readable description of the action taken
    - meal_plan: Updated list of meals in the meal plan
    """
    logger.info("Calling add_to_meal_plan")

    # get the meal plan from teh state, or create a new one if it doesn't exist with a default name
    meal_plan = state.get("meal_plan", MealPlan.make_instance("Meal Plan"))
    # create a meal and add to the list of meals
    meal = Meal(day=day, type=type, name=name, ingredients=ingredients, steps=steps)
    meal_plan["meals"].append(meal)

    return {"description": f"Meal added to {day} {type}", "meal_plan": meal_plan}


@tool
def get_meal_plan(state: dict) -> dict:
    """
    Use this tool to retrieve the contents of the current meal plan so far.

    Use the description of the meal plan to understand what the meal plan is about, e.g., "Weekly Meal plan (only weekday dinners)",
    and use that to continue planning at the right point in the plan.

    If the meal plan is empty so far, the tool will report that the meal plan is empty in its response
    and will not return any more results or data.

    If the meal plan has not been initialized yet, the tool will report that it has not been initialized yet. In that case,
    please ask the user to initialize the meal plan before proceeding.

    Inputs:
    None

    Outputs:
    - description: A human-readable description of the action taken
    - meals: The current meal plan. Keep the following in mind:
        - If the meal plan is empty, the meals list will be empty.
        - If the meal plan has not been initialized yet, the meals list will be empty and the description will indicate that.
        - If the meal plan has been initialized, the meals list will contain the meals added so far.
    """
    logger.info("Getting current meal plan")

    meal_plan = state.get("meal_plan")
    result = {}

    if meal_plan is None:
        description = "Meal plan has not been initialized yet."
    else:
        meals = meal_plan.get("meals", [])
        if not meals:
            description = "Meal plan is empty."
        else:
            # Create a human-readable description of the meals
            description = f"Meal plan: '{meal_plan['name']}'" + "\n".join(
                f"{meal['day']} {meal['type']}: {meal['name']}" for meal in meals
            )

    result["description"] = description

    return result


@tool
def get_meal_plan_with_ingredients(state: dict) -> dict:
    """
    Use this tool to retrieve the contents of the current meal plan so far, including the ingredients for each meal.

    If the meal plan is empty so far, the tool will report that the meal plan is empty in its response
    and will not return any more results or data.

    If the meal plan has not been initialized yet, the tool will report that it has not been initialized yet. In that case,
    please ask the user to initialize the meal plan before proceeding.

    Inputs:
    None

    Outputs:
    - description: The list of ingredients for each meal in the meal plan, formatted as a human-readable string.

    """
    logger.info("Getting current meal plan with ingredients")

    meal_plan = state.get("meal_plan")
    result = {}

    if meal_plan is None:
        description = "Meal plan has not been initialized yet."
        result["meals"] = []
    else:
        meals = meal_plan.get("meals", [])
        if not meals:
            description = "Meal plan is empty."
            result["meals"] = []
        else:
            # Create a human-readable description of the meals with ingredients
            description = f"Meal plan: '{meal_plan['name']}'" + "\n".join(
                f"{meal['day']} {meal['type']}: {meal['name']} - Ingredients: {', '.join(meal['ingredients'])}"
                for meal in meals
            )

    result["description"] = description

    return result


@tool
def convert_meal_plan_to_shopping_list(state: dict, items: List[str]) -> dict:
    """
    This tool converts the meal plan to items in the shopping list. Every item in the meal plan is
    added to the shopping list, so that the user can easily purchase the ingredients needed for the meals.
    This function should be when the user confirms that the meal plan is complete and that they want to add
    the items to the shopping list; this tool should be preferread instead of adding the items one by one as the
    process will be faster with it.

    If the shopping list already exists and has items, ingredients from the meal plan will be added to it.

    Inputs:
    - items: the list of ingredients from each one of the meals in the current meal plan. This is a list of strings and should be
    formatted in a way that is easy to read and understand, e.g., "2 cans of beer", "500g of minced beef". The list of items should
    also be normalized; in case of duplicates because the same ingredient is used in multiple meals, items should be combined, e.g.,
    "100g of cheese" and "0.5kg of cheese" should be combined into "600g of cheese".

    Outputs:
    - description: A human-readable description with a summary of the action taken, e.g., number of items
    added to the shopping list.
    - shopping_list: Updated shopping list with the items from the meal plan added.
    """
    logger.info("convert_meal_plan_to_shopping_list")

    # loop through the meals and extract ingredients
    shopping_list = state.get("shopping_list", [])
    meal_plan = state.get("meal_plan")

    if not meal_plan:
        logger.debug("The meal plan has not been initialized yet. This should not happen.")
        return {"description": "Meal plan has not been initialized yet. Please create one, add some meals and try again."}

    logger.info(f"Processing meal plan: {meal_plan['name']}")

    for ingredient in items:
        logger.debug(f"Adding ingredient '{ingredient}' to shopping list")
        shopping_list.append(ingredient)

    return {"description": "Meal plan converted to shopping list", "shopping_list": shopping_list}
