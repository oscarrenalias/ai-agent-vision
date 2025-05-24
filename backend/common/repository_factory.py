"""
Repository factory module for the AI Agent Vision application.
This module provides factory functions to get repository instances.
"""

import logging
import os
from typing import Any, Dict

from .receipt_repository import ReceiptRepository
from .recipe_repository import RecipeRepository

logger = logging.getLogger(__name__)


def get_receipt_repository(connection_params: Dict[str, Any] = None) -> ReceiptRepository:
    """
    Factory function to get a receipt repository instance

    Args:
        connection_params: Dictionary containing MongoDB connection parameters
                          (uri, database)

    Returns:
        ReceiptRepository instance
    """
    # Use default connection params if not specified
    if connection_params is None:
        connection_params = {
            "uri": os.environ.get("MONGODB_URI", "mongodb://localhost:27017"),
            "database": os.environ.get("MONGODB_DATABASE", "receipts"),
        }

    logger.info("Creating receipt repository")
    return ReceiptRepository(connection_params)


def get_recipe_repository(connection_params: Dict[str, Any] = None) -> RecipeRepository:
    """
    Factory function to get a recipe repository instance

    Args:
        connection_params: Dictionary containing MongoDB connection parameters
                          (uri, database)

    Returns:
        RecipeRepository instance
    """
    # Use default connection params if not specified
    if connection_params is None:
        connection_params = {
            "uri": os.environ.get("MONGODB_URI", "mongodb://localhost:27017"),
            "database": os.environ.get("MONGODB_DATABASE", "receipts"),
        }

    logger.info("Creating recipe repository")
    return RecipeRepository(connection_params)
