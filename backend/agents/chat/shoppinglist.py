import logging
from typing import List, TypedDict

from langchain.tools import tool

logger = logging.getLogger(__name__)


class Meal(TypedDict):
    day: str
    type: str
    recipe: str


@tool
def initialize_meal_plan(state: dict) -> dict:
    """
    Tool to initialize a meal plan.

    Inputs:
    None

    Outputs:
    - description: A human-readable description of the action taken
    - meals: An empty list of meals to start with
    """
    logger.info("Initializing meal plan")
    return {"description": "Meal plan initialized", "meals": []}


@tool
def add_to_meal_plan(state: dict, day: str, type: str, recipe: str) -> dict:
    """
    This tool adds a meal to the meal plan based on the meal (the recipe), the day of the week,
    and the type of meal

    Inputs:
    - day: The day of the week for which to add the meal
    - type: type of meal: dinner, or lunch
    - recipe: the recipe to add to the meal plan

    Outputs:
    - description: A human-readable description of the action taken
    - meals: Updated list of meals in the meal plan
    """
    meal = Meal(day=day, type=type, recipe=recipe)

    logger.info("Calling add_to_meal_plan")
    return {"description": f"Meal added to {day} {type}", "meals": state.get("meals", []) + [meal]}


@tool
def convert_meal_plan_to_shopping_list(state: dict, meals: List[Meal]) -> dict:
    """
    Tool to convert the meal plan to a shopping list.

    Inputs:
    - meals: List of meals in the meal plan

    Outputs:
    - description: A human-readable description of the action taken
    - shopping_list: A shopping list of items
    """
    logger.info("convert_meal_plan_to_shopping_list")

    return {"description": "Meal plan converted to shopping list", "shopping_list": []}


@tool
def add_to_shopping_list(state: dict, item: str) -> dict:
    """
    Tool to add an item to the shopping list. When using this tool, the agent should try
    to rewrite the item to be as specific as possible based on the description provided by the
    user, e.g.,

    - "beer, 2 cans" instead of "two cans of beer"
    - "minced beef, 500g" instead of "500g of minced beef"

    Inputs:
    - item: The item to add to the shopping list

    Outputs:
    - description: A human-readable description of the action taken
    - shopping_list: Updated shopping list with the new item added
    """
    logger.info(f"Adding item '{item}' to shopping list")

    # Assuming state has a 'shopping_list' field
    shopping_list = state.get("shopping_list", [])
    shopping_list.append(item)

    logger.debug(f"Updated shopping list: {shopping_list}")

    return {"description": f"Item '{item}' added to shopping list", "shopping_list": shopping_list}


@tool
def get_shopping_list(state: dict) -> dict:
    """
    Tool to get the current shopping list.

    Inputs:
    None

    Outputs:
    - description: A human-readable description of the action taken
    - shopping_list: The current shopping list
    """
    logger.info("Getting current shopping list")

    # Assuming state has a 'shopping_list' field
    shopping_list = state.get("shopping_list", [])
    if len(shopping_list) == 0:
        description = "Shopping list is empty"
    else:
        description = "Current shopping list:\n" + "\n".join(shopping_list)

    return {"description": description, "shopping_list": shopping_list}


@tool
def get_meal_plan(state: dict) -> dict:
    """
    Tool to get the current meal plan.

    Inputs:
    None

    Outputs:
    - description: A human-readable description of the action taken
    - meals: The current meal plan
    """
    logger.info("Getting current meal plan")

    # Assuming state has a 'meals' field
    meals = state.get("meals", [])

    if len(meals) == 0:
        description = "Meal plan is empty"
    else:
        description = "Current meal plan:\n" + "\n".join(f"{meal['day']} {meal['type']}: {meal['recipe']}" for meal in meals)

    return {"description": description, "meals": meals}


def get_tools():
    return [
        initialize_meal_plan,
        add_to_meal_plan,
        get_meal_plan,
        convert_meal_plan_to_shopping_list,
        add_to_shopping_list,
        get_shopping_list,
    ]
