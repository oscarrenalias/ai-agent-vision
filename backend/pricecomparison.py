"""
CLI tool that takes a parameter from the command line with an item or type of food, in Finnish, and
compares prices across stores using the price comparison agent
"""

import logging
import sys

from dotenv import load_dotenv

from agents import PriceComparisonManager


# Configure logging
def configure_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    # Configure specific loggers
    for logger_name in ["agents", "common"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)


# Create a logger for this module
logger = logging.getLogger(__name__)


def main():
    # Use the first command line argument as item or type of food
    item = sys.argv[1] if len(sys.argv) > 1 else None
    if not item:
        logger.error("No item provided for price comparison.")
        sys.exit(1)

    logger.info(f"Comparing prices for item: {item}")

    # Run the orchestrator agent
    load_dotenv()
    price_comparison_manager = PriceComparisonManager()
    result = price_comparison_manager.run(item=item)

    logger.info(f"Price comparison complete. Results: {result}")
    return result


if __name__ == "__main__":
    configure_logging()
    main()
