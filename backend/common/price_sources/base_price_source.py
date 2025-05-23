"""
Base scraper class for price comparison functionality.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BasePriceSource(ABC):
    """Base class for all price scrapers."""

    def __init__(self, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the scraper with optional custom headers.

        Args:
            headers: Optional custom headers for HTTP requests
        """
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "fi-FI,fi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def make_request(self, url: str) -> Optional[requests.Response]:
        """
        Make an HTTP GET request to the specified URL.

        Args:
            url: The URL to request

        Returns:
            Response object or None if request failed
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Get BeautifulSoup object from URL.

        Args:
            url: The URL to parse

        Returns:
            BeautifulSoup object or None if request failed
        """
        response = self.make_request(url)
        if response:
            return BeautifulSoup(response.text, "html.parser")
        return None

    def inspect_response(self, url: str) -> Dict[str, Any]:
        """
        Make a request and return detailed information about the response.
        Useful for debugging and understanding site structure.

        Args:
            url: The URL to inspect

        Returns:
            Dictionary with response details
        """
        response = self.make_request(url)
        if not response:
            return {"error": "Failed to get response"}

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract basic page information
        title = soup.title.string if soup.title else "No title"

        # Count different HTML elements
        elements = {
            "div": len(soup.find_all("div")),
            "a": len(soup.find_all("a")),
            "img": len(soup.find_all("img")),
            "span": len(soup.find_all("span")),
            "p": len(soup.find_all("p")),
            "h1": len(soup.find_all("h1")),
            "h2": len(soup.find_all("h2")),
            "h3": len(soup.find_all("h3")),
        }

        # Look for common product listing elements
        product_candidates = {
            "products_by_class_product": len(soup.find_all(class_=lambda c: c and "product" in c.lower())),
            "products_by_class_item": len(soup.find_all(class_=lambda c: c and "item" in c.lower())),
            "products_by_class_price": len(soup.find_all(class_=lambda c: c and "price" in c.lower())),
        }

        # Get response headers and status
        headers = dict(response.headers)
        status = response.status_code

        # Get a sample of the HTML (first 1000 chars)
        html_sample = response.text[:1000] if response.text else ""

        return {
            "url": url,
            "status": status,
            "title": title,
            "headers": headers,
            "elements": elements,
            "product_candidates": product_candidates,
            "html_sample": html_sample,
        }

    @abstractmethod
    def search_product(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for products matching the query.

        Args:
            query: Product search query

        Returns:
            List of product dictionaries with details
        """
        pass
