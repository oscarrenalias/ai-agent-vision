import os
import sys
import time
import unittest

import requests.exceptions

# Add the backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agents.recipes.reciperetriever import RecipeRetriever  # noqa: E402


class TestRecipeRetriever(unittest.TestCase):
    """
    Integration test cases for the RecipeRetriever class covering its three retrieval strategies:
    1. recipe-scrapers library (for well-supported recipe sites)
    2. JSON-LD structured data extraction
    3. Basic content extraction (fallback method)

    Note: These tests perform actual HTTP requests to real websites, so they may be slower
    and could fail if the websites change their structure or are temporarily unavailable.
    """

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.retriever = RecipeRetriever()

        # Common URLs for testing
        self.recipe_scrapers_supported_url = "http://bbc.co.uk/food/recipes/tandoori_chickpeas_47491"
        self.json_ld_supported_url = "https://www.allrecipes.com/recipe/158968/spinach-and-feta-turkey-burgers/"
        self.fallback_url = "https://breaddad.com/easy-banana-bread-recipe/"

        # Add a delay between tests to avoid overwhelming servers
        if getattr(self, "is_first_test", None) is None:
            self.is_first_test = True
        else:
            time.sleep(2)  # 2-second delay between tests to be nice to the servers

    def test_recipe_scrapers_strategy(self):
        """
        Integration test for extraction using recipe-scrapers library.
        """
        try:
            # Call the method with a site that should be supported by recipe-scrapers
            result = self.retriever.retrieve_recipe(self.recipe_scrapers_supported_url)

            # Assertions to verify we got a valid result
            self.assertIsNotNone(result)
            self.assertIn("recipe_content", result)
            self.assertIn("site_url", result)
            self.assertIn("description", result)

            # Check that we got a non-empty content with expected recipe components
            self.assertTrue(len(result["recipe_content"]) > 100, "Recipe content should be substantial")
            self.assertEqual(result["site_url"], self.recipe_scrapers_supported_url)

            # Look for common recipe elements in the content
            content = result["recipe_content"].lower()
            self.assertIn("confit tandoori chickpeas", content, "Recipe title should be present")
            self.assertIn("ingredients", content, "Should contain ingredients section")
            self.assertIn("instructions", content, "Should contain instructions section")

            # verify existence of prep time and cook time
            self.assertIn("preparation time", content, "Recipe should have at least minimum preparation time")
            self.assertIn("cooking time", content, "Recipe should have at least minimum cooking time")

            # verify yields
            self.assertIn("yields", content, "Recipe should have yields")

        except (requests.exceptions.RequestException, ConnectionError) as e:
            self.skipTest(f"Network error when accessing {self.recipe_scrapers_supported_url}: {str(e)}")

    def test_json_ld_extraction_strategy(self):
        """
        Integration test for extraction using JSON-LD structured data.
        Tests the AllRecipes site which typically has JSON-LD data.
        """
        try:
            # Call the method with a site that should have JSON-LD data
            result = self.retriever.retrieve_recipe(self.json_ld_supported_url)

            # Assertions to verify we got a valid result
            self.assertIsNotNone(result)
            self.assertIn("recipe_content", result)
            self.assertIn("site_url", result)
            self.assertIn("description", result)

            # Check that we got a non-empty content
            self.assertTrue(len(result["recipe_content"]) > 100, "Recipe content should be substantial")
            self.assertEqual(result["site_url"], self.json_ld_supported_url)

            # Look for expected recipe content
            content = result["recipe_content"].lower()
            self.assertIn("turkey burger", content, "Recipe title or ingredients should be present")
            self.assertIn("spinach", content, "Should contain key ingredient")
            self.assertIn("feta", content, "Should contain key ingredient")

            # Check that either recipe-scrapers or JSON-LD extraction worked
            self.assertTrue(
                "successfully extracted recipe" in result["description"].lower()
                or "successfully extracted structured recipe" in result["description"].lower(),
                "Should indicate successful extraction",
            )

        except (requests.exceptions.RequestException, ConnectionError) as e:
            self.skipTest(f"Network error when accessing {self.json_ld_supported_url}: {str(e)}")

    def test_basic_extraction_fallback_strategy(self):
        """
        Integration test for basic content extraction fallback.
        Tests a site that may not be supported by recipe-scrapers or have JSON-LD.
        """
        try:
            # Call the method with a site that may require fallback extraction
            result = self.retriever.retrieve_recipe(self.fallback_url)

            # Assertions to verify we got a valid result
            self.assertIsNotNone(result)
            self.assertIn("recipe_content", result)
            self.assertIn("site_url", result)
            self.assertIn("description", result)

            # Check that we got a non-empty content
            self.assertTrue(len(result["recipe_content"]) > 100, "Recipe content should be substantial")
            self.assertEqual(result["site_url"], self.fallback_url)

            # Check for some banana bread content
            content = result["recipe_content"].lower()
            self.assertIn("banana", content, "Should contain key ingredient")
            self.assertIn("bread", content, "Should contain recipe type")

            # Verify we got some kind of content description
            self.assertTrue(
                result["description"].startswith("Successfully extracted")
                or "retrieved recipe content" in result["description"].lower(),
                "Should indicate content was retrieved",
            )

        except (requests.exceptions.RequestException, ConnectionError) as e:
            self.skipTest(f"Network error when accessing {self.fallback_url}: {str(e)}")

    def test_invalid_url(self):
        """Test handling of invalid URLs"""
        # Test with empty URL
        result = self.retriever.retrieve_recipe("")
        self.assertIn("Error:", result["recipe_content"])
        self.assertIn("Invalid URL", result["description"])

        # Test with malformed URL
        result = self.retriever.retrieve_recipe("not-a-valid-url")
        self.assertIn("Error:", result["recipe_content"])
        self.assertIn("Invalid URL", result["description"])

    def test_nonexistent_url(self):
        """Test handling of nonexistent URLs that should return errors"""
        # Use a URL that doesn't exist
        result = self.retriever.retrieve_recipe("https://this-site-does-not-exist-123456789.com/recipe")

        # Should still return a result with error information
        self.assertIsNotNone(result)
        self.assertIn("recipe_content", result)
        self.assertIn("site_url", result)
        self.assertIn("description", result)

        # The result should indicate an error occurred
        self.assertIn("Error", result["recipe_content"])
        # Check for common error phrases in the description
        self.assertTrue(
            "Error" in result["description"] or "Failed" in result["description"],
            "Description should indicate an error occurred",
        )


if __name__ == "__main__":
    unittest.main()
