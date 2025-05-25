from typing import List, Optional

from pydantic import BaseModel, Field


class Recipe(BaseModel):
    name: str = Field(description="Name of the recipe")
    description: Optional[str] = Field(default=None, description="Description of the recipe")
    ingredients: List[str] = Field(description="List of ingredients")
    steps: List[str] = Field(description="List of steps to prepare the recipe")
    yields: Optional[int] = Field(default=None, description="Number of yields for this recipe")
    url: Optional[str] = Field(default=None, description="Original site with the source for this recipe")

    # min and max cooking and preparation times as dictionaries with minutes
    cooking_time: Optional[int] = Field(default=None, description="Cooking time in minutes")
    preparation_time: Optional[int] = Field(default=None, description="Preparation time in minutes")

    # list of tags
    tags: Optional[List[str]] = Field(default_factory=list, description="List of tags for the recipe")
