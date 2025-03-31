import logging
from typing import List

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


def get_tools() -> List:
    """
    Returns a list of tools that can be used in the chat.
    """
    return [multiply, get_weather]


@tool
def multiply(a: int, y: int) -> int:
    """
    Multiplies two numbers.

    Args:
        a (int): The first number to multiply.
        y (int): The second number to multiply.
    """
    logger.info(f"a={a}, y={y}")
    return a * y


@tool
def get_weather(city: str) -> str:
    """
    Gets the weather for a given city.

    Args:
        city (str): The name of the city to get the weather for.
    """
    logger.info(f"Getting weather for {city}")
    # Simulate a weather API call
    result = "it's very cold" if city.lower() == "helsinki" else "sunny and 25C"
    return result
