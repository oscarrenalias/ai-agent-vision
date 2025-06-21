import logging

from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def add_to_shopping_list(state: dict, item: str, emoji: str) -> dict:
    """
    Tool to add an item to the shopping list. When using this tool, the agent should try
    to rewrite the item to be as specific as possible based on the description provided by the
    user, e.g.,

    - "beer, 2 cans" instead of "two cans of beer"
    - "minced beef, 500g" instead of "500g of minced beef"

    Inputs:
    - item: The item to add to the shopping list
    - emoji: emoji to associate with the item (e.g., 🍺 for beer).

    Outputs:
    - description: A human-readable description of the action taken
    - shopping_list: Updated shopping list with the new item added
    """
    logger.info(f"Adding item '{item}' to shopping list")

    full_item = f"{emoji} {item}"
    shopping_list = state.get("shopping_list", [])
    shopping_list.append(full_item)
    logger.debug(f"Updated shopping list: {shopping_list}")

    return {"description": f"Item '{full_item}' added to shopping list", "shopping_list": shopping_list}


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


def get_tools():
    return [
        add_to_shopping_list,
        get_shopping_list,
    ]
