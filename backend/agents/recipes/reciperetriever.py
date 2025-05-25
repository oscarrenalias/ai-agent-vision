import json
import logging
import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class RecipeRetriever:
    """
    A class for retrieving and extracting recipe content from URLs.
    Uses multiple strategies with fallbacks to ensure the best possible recipe extraction.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def retrieve_recipe(self, url: str) -> Dict[str, Any]:
        """
        Main method to retrieve recipe content from a URL.
        Attempts multiple strategies in order of preference:
        1. recipe-scrapers library (most reliable for supported sites)
        2. JSON-LD structured data extraction (works for many recipe sites)
        3. Basic content extraction using BeautifulSoup (fallback method)

        Parameters:
        - url: URL of the page to retrieve

        Returns:
        - Dictionary with recipe_content, site_url, and description
        """
        if not url or not url.startswith(("http://", "https://")):
            error_msg = f"Invalid URL provided: {url}"
            logger.error(error_msg)
            return {"recipe_content": f"Error: {error_msg}", "site_url": url if url else "", "description": error_msg}

        logger.info(f"Retrieving recipe content from URL: {url}")
        domain = urlparse(url).netloc

        try:
            # Strategy 1: Try recipe-scrapers library (specialized for recipe websites)
            logger.info(f"Attempting extraction using recipe-scrapers for {domain}")
            recipe_data = self._try_recipe_scrapers(url)
            if recipe_data:
                logger.info(f"Successfully extracted recipe from {domain} using recipe-scrapers")
                return recipe_data

            # Strategy 2: Fall back to JSON-LD structured data extraction
            logger.info(f"Attempting JSON-LD extraction for {domain}")
            recipe_data = self._try_json_ld_extraction(url)
            if recipe_data:
                logger.info(f"Successfully extracted recipe from {domain} using JSON-LD")
                return recipe_data

            # Strategy 3: Last resort - basic content extraction
            logger.info(f"Falling back to basic content extraction for {domain}")
            return self._extract_basic_content(url)

        except Exception as e:
            error_msg = f"Error retrieving recipe from {url}: {str(e)}"
            logger.error(error_msg)
            return {"recipe_content": f"Error retrieving recipe: {str(e)}", "site_url": url, "description": error_msg}

    def _try_recipe_scrapers(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Try to extract recipe using the recipe-scrapers library.

        This method will:
        1. Check if the recipe-scrapers library is installed
        2. Verify if the URL is supported by the library
        3. Attempt to extract recipe data with proper error handling for each field

        Returns:
        - Dictionary with recipe data if successful, None otherwise
        """
        try:
            # Import recipe-scrapers components (inside try block to handle case where library isn't installed)
            from recipe_scrapers import scrape_me
            from recipe_scrapers._exceptions import WebsiteNotImplementedError

            # Try to extract recipe data with scraper
            try:
                scraper = scrape_me(url)
                recipe_data = {}
                extraction_success = False

                # Extract each recipe element with individual try-except blocks
                # This ensures we get as much data as possible even if some parts fail

                # Core recipe elements that should be present in most recipes
                try:
                    recipe_data["title"] = scraper.title()
                    extraction_success = True  # If we at least get a title, consider it a partial success
                except Exception as e:
                    logger.warning(f"Failed to extract title: {e}")
                    recipe_data["title"] = "Unknown recipe title"

                try:
                    recipe_data["ingredients"] = scraper.ingredients()
                    extraction_success = True
                except Exception as e:
                    logger.warning(f"Failed to extract ingredients: {e}")
                    recipe_data["ingredients"] = []

                try:
                    recipe_data["instructions"] = scraper.instructions()
                    extraction_success = True
                except Exception as e:
                    logger.warning(f"Failed to extract instructions: {e}")
                    recipe_data["instructions"] = "No instructions found"

                # Optional recipe elements
                try:
                    recipe_data["description"] = scraper.description()
                except Exception as e:
                    logger.warning(f"Failed to extract description: {e}")
                    recipe_data["description"] = ""

                try:
                    recipe_data["total_time"] = scraper.total_time()
                except Exception as e:
                    logger.warning(f"Failed to extract total_time: {e}")

                try:
                    recipe_data["yields"] = scraper.yields()
                except Exception as e:
                    logger.warning(f"Failed to extract yields: {e}")

                # Try to extract cook/prep times separately if available
                try:
                    recipe_data["preparation_time"] = scraper.prep_time()
                except Exception as e:
                    logger.warning(f"Failed to extract preparation time: {e}")

                try:
                    recipe_data["cooking_time"] = scraper.cook_time()
                except Exception as e:
                    logger.warning(f"Failed to extract cooking time: {e}")

                # If we couldn't extract any useful data, consider this a failure
                if not extraction_success:
                    logger.warning(f"recipe-scrapers extraction failed to retrieve any useful data from {url}")
                    return None

                # Format the content in a readable structure for the LLM
                content_parts = [
                    f"Recipe: {recipe_data['title']}",
                    f"Description: {recipe_data['description']}",
                    "Ingredients:",
                ]

                # Add ingredients
                for ingredient in recipe_data["ingredients"]:
                    content_parts.append(f"- {ingredient}")

                content_parts.append("\nInstructions:")
                content_parts.append(recipe_data["instructions"])

                # Add time information
                if recipe_data.get("preparation_time"):
                    content_parts.append(f"\nPreparation Time: {recipe_data['preparation_time']} minutes")

                if recipe_data.get("cooking_time"):
                    content_parts.append(f"Cooking Time: {recipe_data['cooking_time']} minutes")

                if recipe_data.get("total_time"):
                    content_parts.append(f"Total Time: {recipe_data['total_time']} minutes")

                if recipe_data.get("yields"):
                    content_parts.append(f"Yields: {recipe_data['yields']}")

                page_content = "\n".join(content_parts)

                return {
                    "recipe_content": page_content,
                    "site_url": url,
                    "description": f"Successfully extracted recipe: {recipe_data['title']}",
                }

            except WebsiteNotImplementedError:
                # This shouldn't happen if check_if_url_can_be_scraped works correctly,
                # but we keep it as an additional safeguard
                logger.warning(f"Website not implemented by recipe-scrapers: {url}")
                return None

            except Exception as e:
                logger.warning(f"recipe-scrapers extraction failed: {str(e)}")
                return None

        except ImportError as e:
            logger.warning(f"recipe-scrapers library not available: {e}")
            return None

    def _try_json_ld_extraction(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Try to extract recipe from JSON-LD data in the page.
        """
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, "html.parser")

            # First try to find structured recipe data in JSON-LD
            recipe_json = None
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    json_data = json.loads(script.string)
                    # Check if this is a recipe
                    if isinstance(json_data, dict) and "@type" in json_data:
                        if json_data["@type"] == "Recipe" or (
                            isinstance(json_data.get("@graph"), list)
                            and any(item.get("@type") == "Recipe" for item in json_data.get("@graph", []))
                        ):
                            recipe_json = json_data
                            break
                    elif isinstance(json_data, list):
                        for item in json_data:
                            if isinstance(item, dict) and item.get("@type") == "Recipe":
                                recipe_json = item
                                break
                        if recipe_json:
                            break
                except Exception:
                    continue

            if not recipe_json:
                logger.info("No JSON-LD recipe data found")
                return None

            # Extract recipe from JSON-LD
            content_parts = []

            # Find the recipe data (might be nested in @graph)
            recipe_data = recipe_json
            if "@graph" in recipe_json:
                for item in recipe_json["@graph"]:
                    if item.get("@type") == "Recipe":
                        recipe_data = item
                        break

            # Extract recipe components
            title = recipe_data.get("name", "Unknown Recipe")
            description = recipe_data.get("description", "")

            content_parts.append(f"Recipe: {title}")
            content_parts.append(f"Description: {description}")
            content_parts.append("Ingredients:")

            # Get ingredients
            ingredients = recipe_data.get("recipeIngredient", [])
            for ingredient in ingredients:
                content_parts.append(f"- {ingredient}")

            # Get instructions
            content_parts.append("\nInstructions:")
            instructions = recipe_data.get("recipeInstructions", [])
            if isinstance(instructions, list):
                for i, step in enumerate(instructions):
                    if isinstance(step, dict):
                        content_parts.append(f"{i+1}. {step.get('text', '')}")
                    else:
                        content_parts.append(f"{i+1}. {step}")
            else:
                content_parts.append(instructions)

            # Get time information
            cook_time = recipe_data.get("cookTime", "")
            prep_time = recipe_data.get("prepTime", "")
            total_time = recipe_data.get("totalTime", "")

            if prep_time:
                content_parts.append(f"\nPreparation Time: {prep_time}")
            if cook_time:
                content_parts.append(f"Cooking Time: {cook_time}")
            if total_time:
                content_parts.append(f"Total Time: {total_time}")

            page_content = "\n".join(content_parts)

            return {
                "recipe_content": page_content,
                "site_url": url,
                "description": f"Successfully extracted structured recipe: {title}",
            }

        except Exception as e:
            logger.warning(f"JSON-LD extraction failed: {str(e)}")
            return None

    def _extract_basic_content(self, url: str) -> Dict[str, Any]:
        """
        Extract basic content using BeautifulSoup as last resort.
        """
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script, style, meta, and other non-content tags
            for element in soup(
                [
                    "script",
                    "style",
                    "meta",
                    "noscript",
                    "iframe",
                    "head",
                    "footer",
                    "nav",
                    "aside",
                    "svg",
                    "form",
                    "header",
                    '[class*="banner"]',
                    '[class*="menu"]',
                    '[class*="sidebar"]',
                    '[class*="navigation"]',
                    '[class*="nav-"]',
                    '[class*="footer"]',
                    '[class*="cookie"]',
                    '[class*="popup"]',
                    '[class*="modal"]',
                    '[id*="popup"]',
                    '[id*="modal"]',
                    '[id*="cookie"]',
                ]
            ):
                element.decompose()

            # Try to find recipe specific content using common selectors
            content_section = None
            recipe_selectors = [
                ".recipe",
                "#recipe",
                ".recipe-content",
                ".recipe-container",
                '[itemprop="recipeInstructions"]',
                '[itemprop="ingredients"]',
                ".ingredients",
                ".instructions",
                ".steps",
                ".recipe-ingredients",
                ".recipe-directions",
                ".wprm-recipe",
                ".tasty-recipes",
                ".recipe-summary",
                "article",
                ".post-content",
                ".entry-content",
                ".content",
                "main",
            ]

            for selector in recipe_selectors:
                content_section = soup.select_one(selector)
                if content_section and len(content_section.get_text(strip=True)) > 200:
                    break

            # If we found a specific recipe section, use that, otherwise use the whole body
            if content_section:
                filtered_content = content_section
            else:
                filtered_content = soup.body if soup.body else soup

            # Extract text and clean it up
            text = filtered_content.get_text(separator="\n", strip=True)

            # Remove excessive whitespace and empty lines
            text = re.sub(r"\n\s*\n", "\n\n", text)
            text = re.sub(r" +", " ", text)

            # Extract domain name for better description
            domain = urlparse(url).netloc

            # Limit content to avoid OpenAI rate limits
            if len(text) > 4000:
                text = text[:4000]  # Truncate to approximately 4000 characters

            page_content = "Recipe content:\n" + text.strip()

            return {
                "recipe_content": page_content,
                "site_url": url,
                "description": f"Retrieved recipe content from {domain} ({len(page_content)} characters)",
            }

        except Exception as e:
            logger.error(f"Basic content extraction failed: {str(e)}")
            return {
                "recipe_content": f"Failed to retrieve content from {url}. Error: {str(e)}",
                "site_url": url,
                "description": "Failed to retrieve page content",
            }
