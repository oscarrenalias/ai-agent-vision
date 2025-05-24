"""
Receipt repository implementation for the AI Agent Vision application.
This module provides a MongoDB implementation for storing and retrieving receipts.
"""

import json
import logging
import re
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

import pymongo
from bson import ObjectId
from pymongo.errors import PyMongoError

from common.mongo_connection import MongoConnection

logger = logging.getLogger(__name__)


class ReceiptRepository:
    """
    MongoDB implementation for storing and retrieving receipts.
    This class provides methods to store and retrieve receipt data from a MongoDB database.
    """

    def __init__(self, connection_params: Dict[str, Any] = None):
        """
        Initialize the receipt repository with MongoDB connection parameters

        Args:
            connection_params: Dictionary containing MongoDB connection parameters
                               (uri, database)
        """
        self.mongo_connection = MongoConnection(connection_params)
        self.initialize()

    def initialize(self):
        """Create the receipts collection if it doesn't exist and set up indexes"""
        try:
            # Create the collection with a descending index on created_at
            self.mongo_connection.initialize_collection("receipts", indexes=[(("created_at", pymongo.DESCENDING),)])
            logger.info("Receipt repository initialized successfully")
        except PyMongoError as e:
            logger.error(f"Error initializing receipt repository: {str(e)}")
            raise

    @property
    def receipts_collection(self):
        """Get the receipts collection from the MongoDB database"""
        return self.mongo_connection.get_database().receipts

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

            # Convert string to dict if it's a JSON string
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

            result = self.receipts_collection.insert_one(document)
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
            cursor = self.receipts_collection.find().sort("created_at", pymongo.DESCENDING)

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
            document = self.receipts_collection.find_one({"_id": ObjectId(receipt_id)})

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

            # Convert string to dict if it's a JSON string
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

            result = self.receipts_collection.update_one({"_id": ObjectId(receipt_id)}, {"$set": update_data})

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
            result = self.receipts_collection.delete_one({"_id": ObjectId(receipt_id)})
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
            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

            # Adjust end_date to include the entire day
            end_date_dt = datetime(end_date_dt.year, end_date_dt.month, end_date_dt.day, 23, 59, 59)

            # Query using receipt_data.date field instead of created_at
            cursor = self.receipts_collection.find({"receipt_data.date": {"$gte": start_date_dt, "$lte": end_date_dt}}).sort(
                "receipt_data.date", pymongo.DESCENDING
            )

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
            logger.error(f"Error retrieving receipts by date from MongoDB: {str(e)}")
            return None

    def get_items_per_item_type(self, item_type: str) -> List[Dict[str, Any]]:
        """
        Get items per item type from the database.

        Args:
            item_type (str): The item type to filter by.

        Returns:
            List of dictionaries containing items of the specified type.

        Mongosh query:
            db.receipts.find({
                "$or": [
                    {"items.item_category.level_1": /poultry/i},
                    {"items.item_category.level_2": /poultry/i},
                    {"items.item_category.level_3": /poultry/i}
                ]
            })

            db.receipts.find({
                "$or": [
                    {"items.item_category.level_1": /pasta/i},
                    {"items.item_category.level_2": /pasta/i},
                    {"items.item_category.level_3": /pasta/i}
                ]
            }).count()
        """
        try:
            pattern = re.compile(item_type, re.IGNORECASE)
            query = {
                "$or": [
                    {"items.item_category.level_1": pattern},
                    {"items.item_category.level_2": pattern},
                    {"items.item_category.level_3": pattern},
                ]
            }

            result = self.receipts_collection.find(query)
            return list(result)

        except Exception as e:
            logging.error(f"Error searching items by category value: {str(e)}")
            return []
