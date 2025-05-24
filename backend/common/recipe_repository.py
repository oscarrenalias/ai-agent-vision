import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

import pymongo
from bson import ObjectId
from bson.codec_options import CodecOptions, TypeCodec, TypeRegistry
from pymongo.errors import PyMongoError

from agents.recipes.recipeflow import Recipe, TimeRange

from .mongo_connection import MongoConnection

logger = logging.getLogger(__name__)


# Helper functions for timedelta serialization/deserialization
def serialize_timedelta(td: Optional[timedelta]) -> Optional[Dict[str, int]]:
    """Convert timedelta to a MongoDB and JSON-serializable format"""
    if td is None:
        return None
    return {"total_seconds": int(td.total_seconds())}


def deserialize_timedelta(data: Optional[Dict[str, int]]) -> Optional[timedelta]:
    """Recreate timedelta from serialized format"""
    if data is None or "total_seconds" not in data:
        return None
    return timedelta(seconds=data["total_seconds"])


def serialize_time_range(tr: Optional[TimeRange]) -> Optional[List[Dict[str, int]]]:
    """Convert TimeRange to a MongoDB and JSON-serializable format"""
    if tr is None:
        return None
    min_time, max_time = tr
    result = [serialize_timedelta(min_time)]
    if max_time is not None:
        result.append(serialize_timedelta(max_time))
    return result


def deserialize_time_range(data: Optional[List[Dict[str, int]]]) -> Optional[TimeRange]:
    """Recreate TimeRange from serialized format"""
    if not data or not isinstance(data, list) or len(data) == 0:
        return None

    min_time = deserialize_timedelta(data[0])
    max_time = deserialize_timedelta(data[1]) if len(data) > 1 else None

    return (min_time, max_time)


# MongoDB customization for PyMongo
def setup_mongodb_codecs():
    """Setup custom codecs for PyMongo to handle timedelta serialization"""

    class TimedeltaCodec(TypeCodec):
        python_type = timedelta
        bson_type = dict

        def transform_python(self, value):
            return serialize_timedelta(value)

        def transform_bson(self, value):
            return deserialize_timedelta(value)

    # Register the codec with PyMongo
    type_registry = TypeRegistry([TimedeltaCodec()])
    codec_options = CodecOptions(type_registry=type_registry)

    return codec_options


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
        self._setup_mongodb_collections()
        self.initialize()

    def _setup_mongodb_collections(self):
        """Setup MongoDB collections with proper codec options"""
        # Get codec options for TimeRange and timedelta
        codec_options = setup_mongodb_codecs()

        # Get database with default options
        db = self.mongo_connection.get_database()

        # Get collection with custom codec options
        self._recipes_collection = db.get_collection("recipes", codec_options=codec_options)

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
        return self._recipes_collection or self.mongo_connection.get_database().recipes

    def save_recipe(self, recipe: Recipe) -> Optional[str]:
        """
        Save recipe to MongoDB

        Args:
            recipe: Recipe model instance

        Returns:
            Recipe ID if successful, None otherwise
        """
        try:
            # Convert Recipe model to MongoDB document
            document = self._recipe_to_document(recipe)

            # Insert into database
            result = self.recipes_collection.insert_one(document)
            recipe_id = str(result.inserted_id)
            logger.info(f"Recipe saved to MongoDB successfully with ID: {recipe_id}")
            return recipe_id
        except Exception as e:
            logger.error(f"Error saving recipe to MongoDB: {str(e)}")
            return None

    def get_all_recipes(self) -> List[Recipe]:
        """
        Retrieve all recipes from the database

        Returns:
            List of Recipe model objects
        """
        try:
            cursor = self.recipes_collection.find().sort("created_at", pymongo.DESCENDING)

            recipes = []
            for document in cursor:
                recipe = self._document_to_recipe(document)
                recipes.append(recipe)

            return recipes
        except Exception as e:
            logger.error(f"Error retrieving recipes from MongoDB: {str(e)}")
            return []

    def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """
        Retrieve a specific recipe by ID

        Args:
            recipe_id: The ID of the recipe to retrieve (string representation of ObjectId)

        Returns:
            Recipe model object or None if not found
        """
        try:
            document = self.recipes_collection.find_one({"_id": ObjectId(recipe_id)})

            if document:
                return self._document_to_recipe(document)
            return None
        except Exception as e:
            logger.error(f"Error retrieving recipe {recipe_id} from MongoDB: {str(e)}")
            return None

    def update_recipe(self, recipe_id: str, recipe: Recipe) -> bool:
        """
        Update an existing recipe

        Args:
            recipe_id: The ID of the recipe to update (string representation of ObjectId)
            recipe: Recipe model object with updated data

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing document to maintain created_at and other fields
            existing_doc = self.recipes_collection.find_one({"_id": ObjectId(recipe_id)})

            if not existing_doc:
                logger.error(f"Recipe {recipe_id} not found for update")
                return False

            # Convert Recipe model to MongoDB document format, preserving fields not in model
            update_data = self._recipe_to_document(recipe, existing_doc)

            # Remove _id to avoid update error
            if "_id" in update_data:
                del update_data["_id"]

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

    def search_recipes(self, query: str) -> List[Recipe]:
        """
        Search for recipes by name or tag

        Args:
            query: The search query

        Returns:
            List of matching Recipe model objects
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
                recipe = self._document_to_recipe(document)
                recipes.append(recipe)

            return recipes
        except Exception as e:
            logger.error(f"Error searching recipes in MongoDB: {str(e)}")
            return []

    def get_recipes_by_tags(self, tags: List[str]) -> List[Recipe]:
        """
        Find recipes that match any of the specified tags

        Args:
            tags: List of tags to search for

        Returns:
            List of matching Recipe model objects
        """
        try:
            query = {"tags": {"$in": tags}}
            cursor = self.recipes_collection.find(query).sort("created_at", pymongo.DESCENDING)

            recipes = []
            for document in cursor:
                recipe = self._document_to_recipe(document)
                recipes.append(recipe)

            return recipes
        except Exception as e:
            logger.error(f"Error retrieving recipes by tags from MongoDB: {str(e)}")
            return []

    def get_recipes_by_ingredients(self, ingredients: List[str]) -> List[Recipe]:
        """
        Find recipes that contain any of the specified ingredients

        Args:
            ingredients: List of ingredients to search for

        Returns:
            List of matching Recipe model objects
        """
        try:
            # Create a regex pattern for each ingredient to enable partial matching
            ingredient_patterns = [{"ingredients": {"$regex": ingredient, "$options": "i"}} for ingredient in ingredients]

            query = {"$or": ingredient_patterns}
            cursor = self.recipes_collection.find(query).sort("created_at", pymongo.DESCENDING)

            recipes = []
            for document in cursor:
                recipe = self._document_to_recipe(document)
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
