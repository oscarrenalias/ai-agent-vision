"""
Recipe handling tools for the AI Agent Vision application.
This module provides tools for fetching and storing recipes.
"""

import json
import logging
from typing import Any, Dict, List

from langchain_core.tools import tool

from agents.recipes.recipeflow import Recipe
from common.recipe_repository import deserialize_time_range, serialize_time_range
from common.repository_factory import get_recipe_repository

logger = logging.getLogger(__name__)


def get_tools() -> List:
    """
    Returns a list of tools that can be used in the chat.
    """
    return [fetch_and_store_recipe, get_recipe_by_id, search_recipes, get_recipes_by_tags, get_recipes_by_ingredients]


def _recipe_to_dict(recipe: Recipe) -> Dict[str, Any]:
    """Convert a Recipe model object to a dictionary for JSON serialization"""
    recipe_dict = {
        "name": recipe.name,
        "description": recipe.description,
        "ingredients": recipe.ingredients,
        "steps": recipe.steps,
        "tags": recipe.tags,
    }

    # Handle TimeRange fields with proper serialization
    if recipe.cooking_time_range:
        recipe_dict["cooking_time_range"] = serialize_time_range(recipe.cooking_time_range)

    if recipe.preparation_time_range:
        recipe_dict["preparation_time_range"] = serialize_time_range(recipe.preparation_time_range)

    return recipe_dict


@tool
def fetch_and_store_recipe(recipe_data: Dict[str, Any]) -> str:
    """
    Store a recipe in the database.

    Args:
        recipe_data (dict): Recipe data to store

    Returns:
        str: JSON string with operation result
    """
    try:
        # Create Recipe object from the provided data
        recipe = Recipe(
            name=recipe_data.get("name"),
            description=recipe_data.get("description"),
            ingredients=recipe_data.get("ingredients", []),
            steps=recipe_data.get("steps", []),
            tags=recipe_data.get("tags", []),
        )

        # Handle time ranges if present
        if "cooking_time_range" in recipe_data:
            recipe.cooking_time_range = deserialize_time_range(recipe_data["cooking_time_range"])

        if "preparation_time_range" in recipe_data:
            recipe.preparation_time_range = deserialize_time_range(recipe_data["preparation_time_range"])

        # Store the recipe in the database
        recipe_repo = get_recipe_repository()
        recipe_id = recipe_repo.save_recipe(recipe)

        if recipe_id:
            # Fetch the stored recipe to return
            stored_recipe = recipe_repo.get_recipe_by_id(recipe_id)
            if stored_recipe:
                return json.dumps({"success": True, "recipe": _recipe_to_dict(stored_recipe), "recipe_id": recipe_id})
            else:
                return json.dumps(
                    {"success": True, "recipe_id": recipe_id, "message": "Recipe stored but could not retrieve details"}
                )
        else:
            return json.dumps({"success": False, "error": "Failed to store recipe"})
    except Exception as e:
        logger.error(f"Error in fetch_and_store_recipe: {str(e)}")
        return json.dumps({"success": False, "error": str(e)})


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
        return json.dumps({"success": True, "recipe": _recipe_to_dict(recipe), "recipe_id": recipe_id})
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

    # Convert Recipe objects to dictionaries for JSON serialization
    recipe_dicts = [_recipe_to_dict(recipe) for recipe in recipes]

    return json.dumps({"success": True, "results": recipe_dicts, "count": len(recipes)})


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

    # Convert Recipe objects to dictionaries for JSON serialization
    recipe_dicts = [_recipe_to_dict(recipe) for recipe in recipes]

    return json.dumps({"success": True, "results": recipe_dicts, "count": len(recipes)})


@tool
def get_recipes_by_ingredients(ingredients: str) -> str:
    """
    Get recipes that contain any of the specified ingredients.

    Args:
        ingredients (str): Comma-separated list of ingredients.

    Returns:
        str: A JSON string containing a list of matching recipes.
    """
    ingredient_list = [ingredient.strip() for ingredient in ingredients.split(",")]
    logger.info(f"Getting recipes with ingredients: {ingredient_list}")

    recipe_repo = get_recipe_repository()
    recipes = recipe_repo.get_recipes_by_ingredients(ingredient_list)

    # Convert Recipe objects to dictionaries for JSON serialization
    recipe_dicts = [_recipe_to_dict(recipe) for recipe in recipes]

    return json.dumps({"success": True, "results": recipe_dicts, "count": len(recipes)})
