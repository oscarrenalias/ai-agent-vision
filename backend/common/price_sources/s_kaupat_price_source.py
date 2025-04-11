"""
API client for S-Kaupat product search.
"""
import json
import logging
import urllib.parse
from typing import Any, Dict, List, Optional

from .base_price_source import BasePriceSource

logger = logging.getLogger(__name__)


class SKaupatPriceSource(BasePriceSource):
    """API client for S-Kaupat product search."""

    # Base URL for the API endpoint
    API_URL = "https://api.s-kaupat.fi/"

    # Default store ID for Helsinki area
    DEFAULT_STORE_ID = "513971200"

    def __init__(self, headers: Optional[Dict[str, str]] = None, store_id: str = None):
        """
        Initialize S-Kaupat API client.

        Args:
            headers: Optional custom headers for HTTP requests
            store_id: Optional store ID to use for pricing (defaults to Helsinki area)
        """
        # Update headers for API requests
        api_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }

        if headers:
            api_headers.update(headers)

        super().__init__(api_headers)
        self.store_id = store_id or self.DEFAULT_STORE_ID

    def _build_api_url(self, query: str, limit: int = 24) -> str:
        """
        Build the API URL for product search.

        Args:
            query: Product search query
            limit: Maximum number of results to return

        Returns:
            Formatted API URL
        """
        # Create the variables object
        variables = {
            "facets": [{"key": "brandName", "order": "asc"}, {"key": "category"}, {"key": "labels"}],
            "includeAgeLimitedByAlcohol": False,
            "limit": limit,
            "loop54DirectSearch": True,
            "queryString": query,
            "storeId": self.store_id,
            "useRandomId": True,
        }

        # Create the extensions object
        extensions = {
            "persistedQuery": {"version": 1, "sha256Hash": "29121c3595103a8c4ad58cc195a143f1c8c39789017a8165761d0b251d78da0e"}
        }

        # URL encode the parameters
        encoded_variables = urllib.parse.quote(json.dumps(variables))
        encoded_extensions = urllib.parse.quote(json.dumps(extensions))

        # Build the complete URL
        url = f"{self.API_URL}?operationName=RemoteFilteredProducts&variables={encoded_variables}&extensions={encoded_extensions}"

        return url

    def search_product(self, query: str, limit: int = 24) -> List[Dict[str, Any]]:
        """
        Search for products using S-Kaupat API.

        Args:
            query: Product search query
            limit: Maximum number of results to return

        Returns:
            List of product dictionaries with details
        """
        logger.info(f"Searching S-Kaupat API for: {query}")

        # Build the API URL
        api_url = self._build_api_url(query, limit)

        # Make the API request
        response = self.make_request(api_url)
        if not response:
            logger.error("Failed to get search results from S-Kaupat API")
            return []

        try:
            # Parse the JSON response
            response_data = response.json()

            logger.debug(f"S-Kaupat API response: {response_data}")

            """
                Sample response structure:

                "data": {
                    "store": {
                        "id": "513971200",
                        "products": {
                            "total": 1635,
                            "from": 0,
                            "limit": 24,
                            "items": [
                            {
                                "id": "6437002001454",
                                "ean": "6437002001454",
                                "sokId": "100827466",
                                "name": "Vaasan Ruispalat  660g 12 kpl täysjyväruispalaleipä",
                                "price": 2.19,
                                "storeId": "513971200",
                                "pricing": {
                                "campaignPrice": null,
                                "lowest30DayPrice": null,
                                "campaignPriceValidUntil": null,
                                "regularPrice": 2.19,
                                "currentPrice": 2.19,
                                "__typename": "ProductPricing"
                                },
                                "__typename": "Product",
                                "approxPrice": false,
                                "basicQuantityUnit": "KPL",
                                "comparisonPrice": 3.32,
                                "comparisonUnit": "KGM",
                                "consumerPackageSize": null,
                                "consumerPackageUnit": null,
                                "priceUnit": "KPL",
                                "quantityMultiplier": 1,
                                "isForceSalesByCount": false,
                                "availability": null,
                                "brandName": "Vaasan",
                                "slug": "vaasan-ruispalat-660g-12-kpl-taysjyvaruispalaleipa",
                                "isAgeLimitedByAlcohol": false,
                                "isNewProduct": false,
                                "frozen": false,
                                "packagingLabels": ["Hyvää Suomesta (Sininen Joutsen)"],
                                "packagingLabelCodes": ["GOODS_FROM_FINLAND_BLUE_SWAN"],
                                "hierarchyPath": [
                                {
                                    "id": "StructureGroup_507756644163854",
                                    "name": "Tummat leivät",
                                    "slug": "leivat-keksit-ja-leivonnaiset-1/leivat/tummat-leivat",
                                    "__typename": "HierarchyPathItem"
                                },
                                {
                                    "id": "StructureGroup_1796559627347513",
                                    "name": "Leivät",
                                    "slug": "leivat-keksit-ja-leivonnaiset-1/leivat",
                                    "__typename": "HierarchyPathItem"
                                },
                                {
                                    "id": "Herkku_00000008",
                                    "name": "Leivät, keksit ja leivonnaiset",
                                    "slug": "leivat-keksit-ja-leivonnaiset-1",
                                    "__typename": "HierarchyPathItem"
                                }
                                ],
                                "isGlobalFallback": null,
                                "countryName": {
                                "fi": "Suomi",
                                "__typename": "CountryName"
                                },
                                "productDetails": {
                                "productImages": {
                                    "modifiersString": "{MODIFIERS}",
                                    "extensionString": "{EXTENSION}",
                                    "mainImage": {
                                    "name": "Vaasan Ruispalat  660g 12 kpl täysjyväruispalaleipä",
                                    "urlTemplate": "https://cdn.s-cloud.fi/v1/{MODIFIERS}/assets/dam-id/9sXeRd6faNRBg-k9v4kWUG.{EXTENSION}",
                                    "__typename": "ProductImage"
                                    },
                                    "mobileReadyHeroImage": {
                                    "name": "Vaasan Ruispalat  660g 12 kpl täysjyväruispalaleipä",
                                    "urlTemplate": "https://cdn.s-cloud.fi/v1/{MODIFIERS}/assets/dam-id/8FPHpXZ5qOz9EI_a8uLSGD.{EXTENSION}",
                                    "__typename": "ProductImage"
                                    },
                                    "variableImages": [],
                                    "__typename": "ProductImages"
                                },
                                "__typename": "ProductDetails",
                                "wineSweetness": null
                                },
                                "depositPrice": 0
                            },
                            { ... }
                    ],
                }
            """

            # Extract products from the response
            products = []

            # check if we have any products at all
            data = response_data.get("data", {})
            if "store" in data and data["store"]["products"]:
                total_products = data["store"]["products"].get("total", 0)
                logger.info(f"Found {total_products} products")
                for item in data["store"]["products"]["items"]:
                    product = {
                        "id": item["id"],
                        "name": item["name"],
                        "price": item["pricing"]["currentPrice"],
                        "brand": item["brandName"],
                        "store_id": self.store_id,
                        "image_url": item["productDetails"]["productImages"]["mainImage"]["urlTemplate"],
                    }
                    products.append(product)

            return products

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing S-Kaupat API response: {e}")
            return []

    def inspect_api_response(self, query: str) -> Dict[str, Any]:
        """
        Inspect API response for a query to understand the data structure.

        Args:
            query: Product search query

        Returns:
            Dictionary with response details
        """
        # Build the API URL
        api_url = self._build_api_url(query)

        # Make the API request
        response = self.make_request(api_url)
        if not response:
            return {"error": "Failed to get response from S-Kaupat API"}

        try:
            # Parse the JSON response
            data = response.json()

            # Return the raw response for inspection
            return {"url": api_url, "status": response.status_code, "headers": dict(response.headers), "data": data}

        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse JSON response: {e}",
                "url": api_url,
                "status": response.status_code,
                "headers": dict(response.headers),
                "text": response.text[:1000] if response.text else "",
            }
