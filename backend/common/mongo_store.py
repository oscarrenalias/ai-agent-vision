"""
MongoDB data storage implementation for the AI Agent Vision application.
This module provides a MongoDB implementation of the DataStore interface.
"""

import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

import pymongo
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

from .datastore import DataStore

logger = logging.getLogger(__name__)


class MongoStore(DataStore):
    """
    MongoDB implementation of the DataStore interface.
    This class provides methods to store and retrieve data from a MongoDB database.
    """

    def __init__(self, connection_params: Dict[str, Any] = None):
        """
        Initialize the MongoDB store with connection parameters

        Args:
            connection_params: Dictionary containing MongoDB connection parameters
                               (uri, database)
        """
        self.connection_params = connection_params or {
            "uri": "mongodb://localhost:27017",
            "database": "receipts",
        }
        self.client = None
        self.db = None
        logger.info(
            f"MongoDB store initialized with URI: {self.connection_params.get('uri')}, "
            f"database: {self.connection_params.get('database')}"
        )

    def _get_connection(self):
        """
        Get a connection to the MongoDB database

        Returns:
            MongoDB database object
        """
        if self.client is None:
            try:
                self.client = MongoClient(self.connection_params.get("uri"))
                # Test the connection
                self.client.admin.command("ping")
                self.db = self.client[self.connection_params.get("database")]
                logger.info("Connected to MongoDB successfully")
            except ConnectionFailure as e:
                logger.error(f"Error connecting to MongoDB: {str(e)}")
                raise
        return self.db

    def initialize(self):
        """Create the receipts collection if it doesn't exist"""
        try:
            db = self._get_connection()
            # In MongoDB, collections are created automatically when first document is inserted
            # We can create an index to optimize queries
            if "receipts" not in db.list_collection_names():
                db.create_collection("receipts")
                db.receipts.create_index([("created_at", pymongo.DESCENDING)])
            logger.info("MongoDB database initialized successfully")
        except PyMongoError as e:
            logger.error(f"Error initializing MongoDB database: {str(e)}")
            raise

    def save_receipt(self, receipt_data: str, metadata: dict) -> bool:
        """
        Save receipt data to MongoDB

        Args:
            receipt_data: JSON string containing receipt data
            metadata: Dictionary with additional metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            current_time = datetime.now(UTC)
            db = self._get_connection()

            # Convert string to dict if it's a JSON string
            import json

            if isinstance(receipt_data, str):
                receipt_data = json.loads(receipt_data)

            document = {"receipt_data": receipt_data, "created_at": current_time, "updated_at": current_time}

            result = db.receipts.insert_one(document)
            logger.info(f"Receipt saved to MongoDB successfully with ID: {result.inserted_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving receipt to MongoDB: {str(e)}")
            return False

    def get_all_receipts(self) -> List[Dict[str, Any]]:
        """
        Retrieve all receipts from the database

        Returns:
            List of receipt dictionaries with id, created_at, updated_at, and data fields
        """
        try:
            db = self._get_connection()
            cursor = db.receipts.find().sort("created_at", pymongo.DESCENDING)

            receipts = []
            for document in cursor:
                receipt = {
                    "id": str(document["_id"]),
                    "created_at": document["created_at"].isoformat(),
                    "updated_at": document["updated_at"].isoformat(),
                    "data": document["receipt_data"],
                }
                receipts.append(receipt)

            return receipts
        except Exception as e:
            logger.error(f"Error retrieving receipts from MongoDB: {str(e)}")
            return []

    def get_receipt_by_id(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific receipt by ID

        Args:
            receipt_id: The ID of the receipt to retrieve (string representation of ObjectId)

        Returns:
            Receipt dictionary or None if not found
        """
        try:
            db = self._get_connection()
            document = db.receipts.find_one({"_id": ObjectId(receipt_id)})

            if document:
                receipt = {
                    "id": str(document["_id"]),
                    "created_at": document["created_at"].isoformat(),
                    "updated_at": document["updated_at"].isoformat(),
                    "data": document["receipt_data"],
                }
                return receipt
            return None
        except Exception as e:
            logger.error(f"Error retrieving receipt {receipt_id} from MongoDB: {str(e)}")
            return None

    def update_receipt(self, receipt_id: str, receipt_data: str, metadata: dict) -> bool:
        """
        Update an existing receipt

        Args:
            receipt_id: The ID of the receipt to update (string representation of ObjectId)
            receipt_data: JSON string containing updated receipt data
            metadata: Dictionary with additional metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            current_time = datetime.now(UTC)
            db = self._get_connection()

            # Convert string to dict if it's a JSON string
            import json

            if isinstance(receipt_data, str):
                receipt_data = json.loads(receipt_data)

            result = db.receipts.update_one(
                {"_id": ObjectId(receipt_id)}, {"$set": {"receipt_data": receipt_data, "updated_at": current_time}}
            )

            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating receipt {receipt_id} in MongoDB: {str(e)}")
            return False

    def delete_receipt(self, receipt_id: str) -> bool:
        """
        Delete a receipt from the database

        Args:
            receipt_id: The ID of the receipt to delete (string representation of ObjectId)

        Returns:
            True if successful, False otherwise
        """
        try:
            db = self._get_connection()
            result = db.receipts.delete_one({"_id": ObjectId(receipt_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting receipt {receipt_id} from MongoDB: {str(e)}")
            return False
