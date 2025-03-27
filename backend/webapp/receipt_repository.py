"""
Repository module for receipt operations.
This module provides a repository pattern implementation for receipt data.
"""

import json
import logging
from datetime import datetime, UTC
from typing import List, Dict, Optional, Any
from common.datastore import DataStore, SQLiteStore

class ReceiptRepository:
    """
    Repository class for managing CRUD operations for receipts in the database.
    This class provides methods to create, read, update, and delete receipt records.
    """
    
    def __init__(self, data_store: DataStore = None):
        """
        Initialize the repository with a data store.
        
        Args:
            data_store: DataStore implementation to use
            db_path: Path to the database file (used only if data_store is not provided)
        """
        self.data_store = data_store or SQLiteStore()
        self.data_store.initialize()
        logging.info("ReceiptRepository initialized")
        
    def create_receipt(self, receipt_data: Dict[str, Any]) -> int:
        """
        Save a new receipt to the database.
        
        Args:
            receipt_data: Dictionary containing receipt data
            
        Returns:
            The ID of the newly created receipt
            
        Raises:
            Exception: If there's an error saving the receipt
        """
        try:
            # Convert receipt data to JSON string
            receipt_json = json.dumps(receipt_data)
            
            # Create metadata
            metadata = {
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            # Save the receipt using the data store
            success = self.data_store.save_receipt(receipt_json, metadata)
            
            if not success:
                raise Exception("Failed to save receipt")
                
            # Note: This is a limitation as SQLiteStore doesn't return the ID
            # In a real application, we would modify the interface to return the ID
            # For now, we'll return 0 as a placeholder
            return 0
        except Exception as e:
            logging.error(f"Error creating receipt: {str(e)}")
            raise
            
    def get_all_receipts(self) -> List[Dict[str, Any]]:
        """
        Retrieve all receipts from the database.
        
        Returns:
            List of receipt dictionaries with id, created_at, updated_at, and data fields
        """
        return self.data_store.get_all_receipts()
            
    def get_receipt_by_id(self, receipt_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific receipt by ID.
        
        Args:
            receipt_id: The ID of the receipt to retrieve
            
        Returns:
            Receipt dictionary or None if not found
        """
        return self.data_store.get_receipt_by_id(receipt_id)
            
    def update_receipt(self, receipt_id: int, receipt_data: Dict[str, Any]) -> bool:
        """
        Update an existing receipt.
        
        Args:
            receipt_id: The ID of the receipt to update
            receipt_data: New receipt data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert receipt data to JSON string
            receipt_json = json.dumps(receipt_data)
            
            # Create metadata
            metadata = {
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            # Update the receipt using the data store
            return self.data_store.update_receipt(receipt_id, receipt_json, metadata)
        except Exception as e:
            logging.error(f"Error updating receipt {receipt_id}: {str(e)}")
            return False
            
    def delete_receipt(self, receipt_id: int) -> bool:
        """
        Delete a receipt from the database.
        
        Args:
            receipt_id: The ID of the receipt to delete
            
        Returns:
            True if successful, False otherwise
        """
        return self.data_store.delete_receipt(receipt_id)
