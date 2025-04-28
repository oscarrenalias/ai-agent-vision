import logging
from typing import List

from langchain_core.tools import tool

from common.price_sources import SKaupatPriceSource

logger = logging.getLogger(__name__)


def get_tools() -> List:
    """
    Returns a list of tools that can be used in the chat.
    """
    return [s_kaupat_price_lookup]


@tool
def s_kaupat_price_lookup(item: str) -> str:
    """
    Can be used to perform a product lookup in the S-Kaupat grocer site. The result is a list of items that match the query. Input parameter must
    always be in Finnish since the S-Ruoka site does not support other languages.

    Args:
        item (str): The name of the item to look up. Always in Finnish, must be translated beforehand if provided in another language.

    Returns:
        str: A list of items that match the query. The response string includes:
            - Product name
            - Price
            - Store where the product was found
    """
    logger.info(f"Executing S-Kauppa price lookup for item: {item}")
    price_source = SKaupatPriceSource()
    results = price_source.search_product(item)
    logger.info(f"Query returned {len(results)} results.")
    logger.debug(f"Price lookup results: {results}")

    if not results:
        logger.info("No results found for the given item.")
        return "No results found"

    # Format the results into a string
    formatted_results = []
    for result in results:
        formatted_results.append(f"{result['name']}: {result['price']} at {result['store_id']}")
    return "\n".join(formatted_results)
