"""
Recipe repository implementation for the AI Agent Vision application.
This module provides a MongoDB implementation for storing and retrieving recipes.
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

import pymongo
from bson import ObjectId
from pymongo.errors import PyMongoError

from .mongo_connection import MongoConnection

logger = logging.getLogger(__name__)


class RecipeRepository:
    """
    MongoDB implementation for storing and retrieving recipes.
    This class provides methods to store and retrieve recipe data from a MongoDB database.
    """

    def __init__(self, connection_params: Dict[str, Any] = None):
        """
        Initialize the recipe repository with MongoDB connection parameters

        Args:
            connection_params: Dictionary containing MongoDB connection parameters
                               (uri, database)
        """
        self.mongo_connection = MongoConnection(connection_params)
        self.initialize()

    def initialize(self):
        """Create the recipes collection if it doesn't exist and set up indexes"""
        try:
            # Create the collection with a descending index on created_at
            self.mongo_connection.initialize_collection(
                "recipes",
                indexes=[
                    (("created_at", pymongo.DESCENDING),),
                    (("name", pymongo.TEXT),),  # Text index for recipe name searching
                    (("tags", pymongo.TEXT),),  # Text index for tag searching
                ],
            )
            logger.info("Recipe repository initialized successfully")
        except PyMongoError as e:
            logger.error(f"Error initializing recipe repository: {str(e)}")
            raise

    @property
    def recipes_collection(self):
        """Get the recipes collection from the MongoDB database"""
        return self.mongo_connection.get_database().recipes

    def save_recipe(self, recipe_data: Dict[str, Any]) -> Optional[str]:
        """
        Save recipe data to MongoDB

        Args:
            recipe_data: Dictionary containing recipe data

        Returns:
            Recipe ID if successful, None otherwise
        """
        try:
            current_time = datetime.now(UTC)

            # Ensure recipe_data is a dictionary
            if isinstance(recipe_data, str):
                recipe_data = json.loads(recipe_data)

            document = {
                "name": recipe_data.get("name", ""),
                "description": recipe_data.get("description", ""),
                "steps": recipe_data.get("steps", []),
                "ingredients": recipe_data.get("ingredients", []),
                "prep_time": recipe_data.get("prep_time", None),
                "cook_time": recipe_data.get("cook_time", None),
                "total_time": recipe_data.get("total_time", None),
                "servings": recipe_data.get("servings", None),
                "tags": recipe_data.get("tags", []),
                "source_url": recipe_data.get("source_url", ""),
                "image_url": recipe_data.get("image_url", ""),
                "created_at": current_time,
                "updated_at": current_time,
            }

            result = self.recipes_collection.insert_one(document)
            recipe_id = str(result.inserted_id)
            logger.info(f"Recipe saved to MongoDB successfully with ID: {recipe_id}")
            return recipe_id
        except Exception as e:
            logger.error(f"Error saving recipe to MongoDB: {str(e)}")
            return None

    def get_all_recipes(self) -> List[Dict[str, Any]]:
        """
        Retrieve all recipes from the database

        Returns:
            List of recipe dictionaries
        """
        try:
            cursor = self.recipes_collection.find().sort("created_at", pymongo.DESCENDING)

            recipes = []
            for document in cursor:
                recipe = self._format_recipe_document(document)
                recipes.append(recipe)

            return recipes
        except Exception as e:
            logger.error(f"Error retrieving recipes from MongoDB: {str(e)}")
            return []

    def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific recipe by ID

        Args:
            recipe_id: The ID of the recipe to retrieve (string representation of ObjectId)

        Returns:
            Recipe dictionary or None if not found
        """
        try:
            document = self.recipes_collection.find_one({"_id": ObjectId(recipe_id)})

            if document:
                return self._format_recipe_document(document)
            return None
        except Exception as e:
            logger.error(f"Error retrieving recipe {recipe_id} from MongoDB: {str(e)}")
            return None

    def update_recipe(self, recipe_id: str, recipe_data: Dict[str, Any]) -> bool:
        """
        Update an existing recipe

        Args:
            recipe_id: The ID of the recipe to update (string representation of ObjectId)
            recipe_data: Dictionary containing updated recipe data

        Returns:
            True if successful, False otherwise
        """
        try:
            current_time = datetime.now(UTC)

            # Ensure recipe_data is a dictionary
            if isinstance(recipe_data, str):
                recipe_data = json.loads(recipe_data)

            update_data = {
                "name": recipe_data.get("name", ""),
                "description": recipe_data.get("description", ""),
                "steps": recipe_data.get("steps", []),
                "ingredients": recipe_data.get("ingredients", []),
                "prep_time": recipe_data.get("prep_time", None),
                "cook_time": recipe_data.get("cook_time", None),
                "total_time": recipe_data.get("total_time", None),
                "servings": recipe_data.get("servings", None),
                "tags": recipe_data.get("tags", []),
                "source_url": recipe_data.get("source_url", ""),
                "image_url": recipe_data.get("image_url", ""),
                "updated_at": current_time,
            }

            result = self.recipes_collection.update_one({"_id": ObjectId(recipe_id)}, {"$set": update_data})

            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating recipe {recipe_id} in MongoDB: {str(e)}")
            return False

    def delete_recipe(self, recipe_id: str) -> bool:
        """
        Delete a recipe from the database

        Args:
            recipe_id: The ID of the recipe to delete (string representation of ObjectId)

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.recipes_collection.delete_one({"_id": ObjectId(recipe_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting recipe {recipe_id} from MongoDB: {str(e)}")
            return False

    def search_recipes(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for recipes by name or tag

        Args:
            query: The search query

        Returns:
            List of matching recipe dictionaries
        """
        try:
            # Create text search query
            text_query = {"$text": {"$search": query}}

            # Sort by relevance score
            cursor = self.recipes_collection.find(text_query, {"score": {"$meta": "textScore"}}).sort(
                [("score", {"$meta": "textScore"})]
            )

            recipes = []
            for document in cursor:
                recipe = self._format_recipe_document(document)
                recipes.append(recipe)

            return recipes
        except Exception as e:
            logger.error(f"Error searching recipes in MongoDB: {str(e)}")
            return []

    def get_recipes_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """
        Find recipes that match any of the specified tags

        Args:
            tags: List of tags to search for

        Returns:
            List of matching recipe dictionaries
        """
        try:
            query = {"tags": {"$in": tags}}
            cursor = self.recipes_collection.find(query).sort("created_at", pymongo.DESCENDING)

            recipes = []
            for document in cursor:
                recipe = self._format_recipe_document(document)
                recipes.append(recipe)

            return recipes
        except Exception as e:
            logger.error(f"Error retrieving recipes by tags from MongoDB: {str(e)}")
            return []

    def get_recipes_by_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """
        Find recipes that contain any of the specified ingredients

        Args:
            ingredients: List of ingredients to search for

        Returns:
            List of matching recipe dictionaries
        """
        try:
            # Create a regex pattern for each ingredient to enable partial matching
            ingredient_patterns = [{"ingredients": {"$regex": ingredient, "$options": "i"}} for ingredient in ingredients]

            query = {"$or": ingredient_patterns}
            cursor = self.recipes_collection.find(query).sort("created_at", pymongo.DESCENDING)

            recipes = []
            for document in cursor:
                recipe = self._format_recipe_document(document)
                recipes.append(recipe)

            return recipes
        except Exception as e:
            logger.error(f"Error retrieving recipes by ingredients from MongoDB: {str(e)}")
            return []

    def _format_recipe_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a MongoDB document into a recipe dictionary

        Args:
            document: MongoDB document

        Returns:
            Formatted recipe dictionary
        """
        recipe = {
            "id": str(document["_id"]),
            "name": document.get("name", ""),
            "description": document.get("description", ""),
            "steps": document.get("steps", []),
            "ingredients": document.get("ingredients", []),
            "prep_time": document.get("prep_time"),
            "cook_time": document.get("cook_time"),
            "total_time": document.get("total_time"),
            "servings": document.get("servings"),
            "tags": document.get("tags", []),
            "source_url": document.get("source_url", ""),
            "image_url": document.get("image_url", ""),
            "created_at": document["created_at"].isoformat(),
            "updated_at": document["updated_at"].isoformat(),
        }
        return recipe
