"""
Unit tests for the Recipe model.

These tests validate the Pydantic model validation for the Recipe class,
including mandatory and optional fields.
"""

import unittest

from pydantic import ValidationError

from agents.recipes.recipe import Recipe


class TestRecipe(unittest.TestCase):
    """Test cases for Recipe model validation."""

    def test_create_recipe_with_required_fields(self):
        """Test creating a Recipe with only the required fields."""
        recipe = Recipe(name="Test Recipe", ingredients=["Ingredient 1", "Ingredient 2"], steps=["Step 1", "Step 2"])

        self.assertEqual(recipe.name, "Test Recipe")
        self.assertEqual(recipe.ingredients, ["Ingredient 1", "Ingredient 2"])
        self.assertEqual(recipe.steps, ["Step 1", "Step 2"])

        # Verify optional fields have default values
        self.assertIsNone(recipe.description)
        self.assertIsNone(recipe.yields)
        self.assertIsNone(recipe.url)
        self.assertIsNone(recipe.cooking_time)
        self.assertIsNone(recipe.preparation_time)
        self.assertEqual(recipe.tags, [])  # default_factory=list

    def test_create_recipe_with_all_fields(self):
        """Test creating a Recipe with all fields."""
        recipe = Recipe(
            name="Complete Recipe",
            description="A test recipe with all fields",
            ingredients=["Flour", "Sugar", "Eggs"],
            steps=["Mix ingredients", "Bake at 350F for 30 mins"],
            yields=4,
            url="https://example.com/recipe",
            cooking_time=30,
            preparation_time=15,
            tags=["dessert", "easy", "quick"],
        )

        self.assertEqual(recipe.name, "Complete Recipe")
        self.assertEqual(recipe.description, "A test recipe with all fields")
        self.assertEqual(recipe.ingredients, ["Flour", "Sugar", "Eggs"])
        self.assertEqual(recipe.steps, ["Mix ingredients", "Bake at 350F for 30 mins"])
        self.assertEqual(recipe.yields, 4)
        self.assertEqual(recipe.url, "https://example.com/recipe")
        self.assertEqual(recipe.cooking_time, 30)
        self.assertEqual(recipe.preparation_time, 15)
        self.assertEqual(recipe.tags, ["dessert", "easy", "quick"])

    def test_missing_required_fields(self):
        """Test that validation fails when required fields are missing."""
        # Missing name
        with self.assertRaises(ValidationError):
            Recipe(ingredients=["Ingredient 1"], steps=["Step 1"])

        # Missing ingredients
        with self.assertRaises(ValidationError):
            Recipe(name="Test Recipe", steps=["Step 1"])

        # Missing steps
        with self.assertRaises(ValidationError):
            Recipe(name="Test Recipe", ingredients=["Ingredient 1"])

    def test_invalid_field_types(self):
        """Test that validation fails with incorrect field types."""
        # Invalid name type
        with self.assertRaises(ValidationError):
            Recipe(name=123, ingredients=["Ingredient 1"], steps=["Step 1"])  # Should be a string

        # Invalid ingredients type
        with self.assertRaises(ValidationError):
            Recipe(name="Test Recipe", ingredients="Not a list", steps=["Step 1"])  # Should be a list

        # Invalid steps type
        with self.assertRaises(ValidationError):
            Recipe(name="Test Recipe", ingredients=["Ingredient 1"], steps="Not a list")  # Should be a list

        # Invalid optional field types
        with self.assertRaises(ValidationError):
            Recipe(
                name="Test Recipe",
                ingredients=["Ingredient 1"],
                steps=["Step 1"],
                cooking_time="30 minutes",  # Should be an integer
            )

    def test_empty_lists(self):
        """Test that empty lists are valid for list fields."""
        # Empty ingredients list - since it's required but can be empty
        recipe1 = Recipe(name="Test Recipe", ingredients=[], steps=["Step 1"])  # Empty list is valid for required field
        self.assertEqual(recipe1.ingredients, [])

        # Empty steps list - since it's required but can be empty
        recipe2 = Recipe(name="Test Recipe", ingredients=["Ingredient 1"], steps=[])  # Empty list is valid for required field
        self.assertEqual(recipe2.steps, [])

        # Empty tags list (optional field)
        recipe3 = Recipe(name="Test Recipe", ingredients=["Ingredient 1"], steps=["Step 1"], tags=[])
        self.assertEqual(recipe3.tags, [])

    def test_none_for_optional_fields(self):
        """Test that None is accepted for optional fields."""
        recipe = Recipe(
            name="Test Recipe",
            ingredients=["Ingredient 1"],
            steps=["Step 1"],
            description=None,
            yields=None,
            url=None,
            cooking_time=None,
            preparation_time=None,
            # Not setting tags at all - should use default_factory=list
        )

        self.assertIsNone(recipe.description)
        self.assertIsNone(recipe.yields)
        self.assertIsNone(recipe.url)
        self.assertIsNone(recipe.cooking_time)
        self.assertIsNone(recipe.preparation_time)
        self.assertEqual(recipe.tags, [])  # default_factory=list


if __name__ == "__main__":
    unittest.main()
