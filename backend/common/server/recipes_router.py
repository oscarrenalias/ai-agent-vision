import logging
import os
from typing import Any, Dict

from bson import ObjectId
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

RECIPES_COLLECTION = "recipes"

MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGODB_DATABASE", "receipts")

logger = logging.getLogger(__name__)

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]

recipes_router = APIRouter()

# Helper to convert MongoDB document to JSON-serializable dict


def recipe_to_dict(recipe: Dict[str, Any]) -> Dict[str, Any]:
    recipe = dict(recipe)
    recipe["id"] = str(recipe.pop("_id"))
    return recipe


@recipes_router.get("/recipes")
async def get_all_recipes():
    try:
        cursor = db[RECIPES_COLLECTION].find()
        recipes = [recipe_to_dict(doc) async for doc in cursor]
        return {"recipes": recipes}
    except Exception as e:
        logger.error(f"Error fetching recipes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recipes.")


@recipes_router.put("/recipes/{recipe_id}")
async def update_recipe(recipe_id: str, data: Dict[str, Any] = Body(...)):
    try:
        oid = ObjectId(recipe_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid recipe id.")
    try:
        result = await db[RECIPES_COLLECTION].update_one({"_id": oid}, {"$set": data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Recipe not found.")
        updated = await db[RECIPES_COLLECTION].find_one({"_id": oid})
        return recipe_to_dict(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating recipe {recipe_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update recipe.")


@recipes_router.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: str):
    try:
        oid = ObjectId(recipe_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid recipe id.")
    try:
        result = await db[RECIPES_COLLECTION].delete_one({"_id": oid})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Recipe not found.")
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting recipe {recipe_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete recipe.")
