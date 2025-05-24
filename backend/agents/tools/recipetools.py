"""
Recipe handling tools for the AI Agent Vision application.
This module provides tools for fetching and storing recipes.
"""

import json
import logging
from typing import List

from langchain_core.tools import tool

from common.repository_factory import get_recipe_repository

logger = logging.getLogger(__name__)


def get_tools() -> List:
    """
    Returns a list of tools that can be used in the chat.
    """
    return [fetch_and_store_recipe, get_recipe_by_id, search_recipes, get_recipes_by_tags]


@tool
def fetch_and_store_recipe(recipe_to_store: dict) -> str:
    # Store the recipe in the database
    recipe_repo = get_recipe_repository()
    recipe_id = recipe_repo.save_recipe(recipe_to_store)

    if recipe_id:
        # Fetch the stored recipe to return
        stored_recipe = recipe_repo.get_recipe_by_id(recipe_id)
        return json.dumps({"success": True, "recipe": stored_recipe})
    else:
        return json.dumps({"success": False, "error": "Failed to store recipe"})


@tool
def get_recipe_by_id(recipe_id: str) -> str:
    """
    Get a recipe from the database by its ID.

    Args:
        recipe_id (str): The ID of the recipe to retrieve.

    Returns:
        str: A JSON string containing the recipe information.
    """
    logger.info(f"Getting recipe with ID {recipe_id}")

    recipe_repo = get_recipe_repository()
    recipe = recipe_repo.get_recipe_by_id(recipe_id)

    if recipe:
        return json.dumps({"success": True, "recipe": recipe})
    else:
        return json.dumps({"success": False, "error": "Recipe not found"})


@tool
def search_recipes(query: str) -> str:
    """
    Search for recipes by name or tag.

    Args:
        query (str): The search query.

    Returns:
        str: A JSON string containing a list of matching recipes.
    """
    logger.info(f"Searching recipes with query: {query}")

    recipe_repo = get_recipe_repository()
    recipes = recipe_repo.search_recipes(query)

    return json.dumps({"success": True, "results": recipes, "count": len(recipes)})


@tool
def get_recipes_by_tags(tags: str) -> str:
    """
    Get recipes that match any of the specified tags.

    Args:
        tags (str): Comma-separated list of tags.

    Returns:
        str: A JSON string containing a list of matching recipes.
    """
    tag_list = [tag.strip() for tag in tags.split(",")]
    logger.info(f"Getting recipes with tags: {tag_list}")

    recipe_repo = get_recipe_repository()
    recipes = recipe_repo.get_recipes_by_tags(tag_list)

    return json.dumps({"success": True, "results": recipes, "count": len(recipes)})
