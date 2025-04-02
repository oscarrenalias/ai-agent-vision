"""
Data storage module for the AI Agent Vision application.
This module provides abstract base class and factory function for data storage.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataStore(ABC):
    """
    Abstract base class for data storage implementations.
    This class defines the interface that all data stores must implement.
    """

    @abstractmethod
    def initialize(self):
        """Initialize the data store (create tables etc)"""
        pass

    @abstractmethod
    def save_receipt(self, receipt_data: str, metadata: dict) -> bool:
        """
        Save receipt data to storage

        Args:
            receipt_data: JSON string containing receipt data
            metadata: Dictionary with additional metadata

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_all_receipts(self) -> List[Dict[str, Any]]:
        """
        Retrieve all receipts from the data store

        Returns:
            List of receipt dictionaries
        """
        pass

    @abstractmethod
    def get_receipt_by_id(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific receipt by ID

        Args:
            receipt_id: The ID of the receipt to retrieve (string for MongoDB, int for SQL)

        Returns:
            Receipt dictionary or None if not found
        """
        pass

    @abstractmethod
    def update_receipt(self, receipt_id: str, receipt_data: str, metadata: dict) -> bool:
        """
        Update an existing receipt

        Args:
            receipt_id: The ID of the receipt to update (string for MongoDB, int for SQL)
            receipt_data: JSON string containing updated receipt data
            metadata: Dictionary with additional metadata

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def delete_receipt(self, receipt_id: str) -> bool:
        """
        Delete a receipt from the data store

        Args:
            receipt_id: The ID of the receipt to delete (string for MongoDB, int for SQL)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_receipts_by_date(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Retrieve receipts within a specific date range

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of receipt dictionaries within the specified date range
        """
        pass

    @abstractmethod
    def get_items_per_item_type(self, item_type: str) -> List[Dict[str, Any]]:
        """
        Retrieve items based on their item type based on existing categorization in receipts,
        in level 1, level 2 or level 3.

        Args:
            item_type: The type of item to retrieve

        Returns:
            List of item dictionaries matching the specified type
        """
        pass


# Factory function to get the appropriate data store implementation
def get_data_store(store_type: str = None) -> DataStore:
    """
    Factory function to get the appropriate data store implementation

    Args:
        store_type: Type of data store to use ('postgres', 'sqlite', or None)
                   If None, will check for DATASTORE_TYPE environment variable
                   and default to 'postgres' if not set

    Returns:
        DataStore implementation
    """
    from .postgres_store import PostgresStore
    from .sqlite_store import SQLiteStore

    # Determine store type from environment variable if not specified
    if store_type is None:
        store_type = os.environ.get("DATASTORE_TYPE", "mongodb").lower()

    # Create and return the appropriate data store
    if store_type == "sqlite":
        logger.info("Using SQLite data store")
        return SQLiteStore()
    elif store_type == "postgres":
        logger.info("Using PostgreSQL data store")
        connection_params = {
            "host": os.environ.get("POSTGRES_HOST", "localhost"),
            "port": int(os.environ.get("POSTGRES_PORT", 5432)),
            "dbname": os.environ.get("POSTGRES_DB", "receipts"),
            "user": os.environ.get("POSTGRES_USER", "postgres"),
            "password": os.environ.get("POSTGRES_PASSWORD", "postgres"),
        }
        return PostgresStore(connection_params)
    else:
        # Default to MongoDB
        logger.info("Using MongoDB data store")
        from .mongo_store import MongoStore

        connection_params = {
            "uri": os.environ.get("MONGODB_URI", "mongodb://localhost:27017"),
            "database": os.environ.get("MONGODB_DATABASE", "receipts"),
        }
        return MongoStore(connection_params)
