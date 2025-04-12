#!/usr/bin/env python3
"""
Test script for price comparison sources.
This script helps inspect the structure of the target websites.
"""
import argparse
import json
import logging
import sys
from typing import Any, Dict

from common.price_sources import KRuokaPriceSource, SKaupatPriceSource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def pretty_print_json(data: Dict[str, Any]) -> None:
    """Print JSON data in a readable format."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_k_ruoka(query: str) -> None:
    """Test K-Ruoka price source with a query."""
    logger.info(f"Testing K-Ruoka price source with query: {query}")
    price_source = KRuokaPriceSource()
    results = price_source.inspect_search_results(query)

    logger.info("K-Ruoka inspection results:")
    pretty_print_json(results)


def test_s_kaupat(query: str) -> None:
    """Test S-Kaupat API with a query."""
    logger.info(f"Testing S-Kaupat API with query: {query}")
    price_source = SKaupatPriceSource()

    # Test the API response inspection
    logger.info("Testing S-Kaupat API response inspection:")
    api_results = price_source.inspect_api_response(query)

    # Print a simplified version of the results to avoid overwhelming output
    simplified_results = {
        "url": api_results.get("url", ""),
        "status": api_results.get("status", ""),
        "headers": api_results.get("headers", {}),
    }

    # Add data structure overview if available
    if "data" in api_results:
        data = api_results["data"]
        if isinstance(data, dict):
            simplified_results["data_structure"] = {
                "keys": list(data.keys()),
                "has_products": "data" in data and "remoteFilteredProducts" in data["data"],
            }

            # Add sample product if available
            if (
                "data" in data
                and "remoteFilteredProducts" in data["data"]
                and "products" in data["data"]["remoteFilteredProducts"]
                and len(data["data"]["remoteFilteredProducts"]["products"]) > 0
            ):
                sample_product = data["data"]["remoteFilteredProducts"]["products"][0]
                simplified_results["sample_product"] = sample_product

    logger.info("S-Kaupat API inspection results (simplified):")
    pretty_print_json(simplified_results)

    # Test the product search functionality
    logger.info("Testing S-Kaupat product search:")
    products = price_source.search_product(query, limit=5)  # Limit to 5 products for testing

    logger.info(f"Found {len(products)} products: ")
    pretty_print_json(products)


def main() -> None:
    """Main function to run the price source tests."""
    parser = argparse.ArgumentParser(description="Test price comparison price sources")
    parser.add_argument("query", help="Product search query")
    parser.add_argument(
        "--site", choices=["k-ruoka", "s-kaupat", "both"], default="both", help="Which site to test (default: both)"
    )

    args = parser.parse_args()

    if args.site in ["k-ruoka", "both"]:
        test_k_ruoka(args.query)

    if args.site in ["s-kaupat", "both"]:
        test_s_kaupat(args.query)


if __name__ == "__main__":
    main()
