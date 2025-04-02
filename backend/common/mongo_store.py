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

            # Convert date string to MongoDB Date object if it exists
            if "receipt_data" in receipt_data and "date" in receipt_data["receipt_data"]:
                date_str = receipt_data["receipt_data"]["date"]
                if date_str and isinstance(date_str, str):
                    try:
                        # Try to parse date in DD.MM.YYYY format
                        if "." in date_str:
                            day, month, year = date_str.split(".")
                            receipt_data["receipt_data"]["date"] = datetime(int(year), int(month), int(day))
                        # Try to parse date in YYYY-MM-DD format
                        elif "-" in date_str:
                            receipt_data["receipt_data"]["date"] = datetime.strptime(date_str, "%Y-%m-%d")
                    except (ValueError, TypeError):
                        # Keep original string if parsing fails
                        logger.warning(f"Could not parse date: {date_str}, keeping as string")

            document = {
                "receipt_data": receipt_data["receipt_data"],
                "items": receipt_data["items"],
                "created_at": current_time,
                "updated_at": current_time,
            }

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
                # Convert MongoDB date objects to ISO format strings for JSON serialization
                receipt_data = document.get("receipt_data", {})
                items = document.get("items", [])

                # Convert MongoDB date to string if it's a datetime object
                if "date" in receipt_data and isinstance(receipt_data["date"], datetime):
                    receipt_data["date"] = receipt_data["date"].strftime("%d.%m.%Y")

                receipt = {
                    "id": str(document["_id"]),
                    "created_at": document["created_at"].isoformat(),
                    "updated_at": document["updated_at"].isoformat(),
                    "data": {"receipt_data": receipt_data, "items": items},
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
                # Convert MongoDB date objects to ISO format strings for JSON serialization
                receipt_data = document.get("receipt_data", {})
                items = document.get("items", [])

                # Convert MongoDB date to string if it's a datetime object
                if "date" in receipt_data and isinstance(receipt_data["date"], datetime):
                    receipt_data["date"] = receipt_data["date"].strftime("%d.%m.%Y")

                receipt = {
                    "id": str(document["_id"]),
                    "created_at": document["created_at"].isoformat(),
                    "updated_at": document["updated_at"].isoformat(),
                    "data": {"receipt_data": receipt_data, "items": items},
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

            # Convert date string to MongoDB Date object if it exists
            if "receipt_data" in receipt_data and "date" in receipt_data["receipt_data"]:
                date_str = receipt_data["receipt_data"]["date"]
                if date_str and isinstance(date_str, str):
                    try:
                        # Try to parse date in DD.MM.YYYY format
                        if "." in date_str:
                            day, month, year = date_str.split(".")
                            receipt_data["receipt_data"]["date"] = datetime(int(year), int(month), int(day))
                        # Try to parse date in YYYY-MM-DD format
                        elif "-" in date_str:
                            receipt_data["receipt_data"]["date"] = datetime.strptime(date_str, "%Y-%m-%d")
                    except (ValueError, TypeError):
                        # Keep original string if parsing fails
                        logger.warning(f"Could not parse date: {date_str}, keeping as string")

            update_data = {
                "receipt_data": receipt_data["receipt_data"],
                "items": receipt_data["items"],
                "updated_at": current_time,
            }

            result = db.receipts.update_one({"_id": ObjectId(receipt_id)}, {"$set": update_data})

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

    def get_receipts_by_date(self, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get the receipts and their associated items for a given period of time, including all metadata.

        Args:
            start_date (str): The start date of the period as YYYY-MM-DD.
            end_date (str): The end date of the period as YYYY-MM-DD.

        Returns:
            List of dictionaries containing receipt data for the specified period.
        """
        try:
            db = self._get_connection()
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

            cursor = db.receipts.find({"created_at": {"$gte": start_date, "$lte": end_date}}).sort(
                "created_at", pymongo.DESCENDING
            )

            receipts = []
            for document in cursor:
                receipt = {
                    "id": str(document["_id"]),
                    "created_at": document["created_at"].isoformat(),
                    "updated_at": document["updated_at"].isoformat(),
                    "receipt_data": document["receipt_data"],
                    "items": document["items"],
                }
                receipts.append(receipt)

            return receipts
        except Exception as e:
            logger.error(f"Error retrieving receipts from MongoDB: {str(e)}")
            return None

    def get_items_per_item_type(self, item_type: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get items per item type from the database.

        Args:
            item_type (str): The item type to filter by.

        Returns:
            List of dictionaries containing items of the specified type.
        """
        try:
            db = self._get_connection()
            cursor = db.receipts.find({"items.item_type": item_type})

            items = []
            for document in cursor:
                items.extend(document["items"])

            return items
        except Exception as e:
            logger.error(f"Error retrieving items from MongoDB: {str(e)}")
            return None
