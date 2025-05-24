"""
MongoDB connection utility for the AI Agent Vision application.
This module provides a utility class for managing MongoDB connections.
"""

import logging
import os
from typing import Any, Dict, Optional

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, PyMongoError

logger = logging.getLogger(__name__)


class MongoConnection:
    """
    Utility class for managing MongoDB connections.
    This class provides methods to connect to and interact with a MongoDB database.
    """

    _instance = None
    _client = None
    _db = None

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern to reuse the same connection."""
        if cls._instance is None:
            cls._instance = super(MongoConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self, connection_params: Optional[Dict[str, Any]] = None):
        """
        Initialize the MongoDB connection with connection parameters.

        Args:
            connection_params: Dictionary containing MongoDB connection parameters
                               (uri, database)
        """
        # Only initialize once (singleton pattern)
        if self._client is not None:
            return

        self.connection_params = connection_params or {
            "uri": os.environ.get("MONGODB_URI", "mongodb://localhost:27017"),
            "database": os.environ.get("MONGODB_DATABASE", "receipts"),
        }

        logger.info(
            f"MongoDB connection initialized with URI: {self.connection_params.get('uri')}, "
            f"database: {self.connection_params.get('database')}"
        )

    def get_database(self) -> Database:
        """
        Get a connection to the MongoDB database.

        Returns:
            MongoDB database object
        """
        if self._client is None:
            try:
                self._client = MongoClient(self.connection_params.get("uri"))
                # Test the connection
                self._client.admin.command("ping")
                self._db = self._client[self.connection_params.get("database")]
                logger.info("Connected to MongoDB successfully")
            except ConnectionFailure as e:
                logger.error(f"Error connecting to MongoDB: {str(e)}")
                raise

        return self._db

    def initialize_collection(self, collection_name: str, indexes=None):
        """
        Create a collection if it doesn't exist and set up indexes.

        Args:
            collection_name: Name of the collection to initialize
            indexes: List of index specifications to create
        """
        try:
            db = self.get_database()

            # In MongoDB, collections are created automatically when first document is inserted
            # We can create an index to optimize queries
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)

                # Create indexes if specified
                if indexes:
                    for index_spec in indexes:
                        db[collection_name].create_index(index_spec)

            logger.info(f"MongoDB collection '{collection_name}' initialized successfully")
        except PyMongoError as e:
            logger.error(f"Error initializing MongoDB collection '{collection_name}': {str(e)}")
            raise

    def close(self):
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")
