from .receiptstate import ReceiptState
import logging
from abc import ABC, abstractmethod
import json
import sqlite3
from .receiptstate import ReceiptState
import logging
import os
from datetime import datetime, UTC

class DataStore(ABC):
    """Abstract base class for data storage implementations"""
    @abstractmethod
    def initialize(self):
        """Initialize the data store (create tables etc)"""
        pass

    @abstractmethod
    def save_receipt(self, receipt_data: str, metadata: dict) -> bool:
        """Save receipt data to storage"""
        pass

class SQLiteStore(DataStore):
    def __init__(self, db_path: str = "receipts.db"):
        self.db_path = db_path

    def initialize(self):
        """Create the receipts table if it doesn't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS receipts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    receipt_data TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            ''')
            conn.commit()

    def save_receipt(self, receipt_data: str, metadata: dict) -> bool:
        """Save receipt data to SQLite"""
        try:
            current_time = datetime.now(UTC).isoformat()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO receipts (receipt_data, created_at, updated_at) VALUES (?, ?, ?)',
                    (receipt_data, current_time, current_time)
                )
                conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error saving receipt to SQLite: {str(e)}")
            return False

class PersistData:
    """Persists the receipt data into a data store"""
    def __init__(self, data_store: DataStore = None):
        self.data_store = data_store or SQLiteStore()
        self.data_store.initialize()
        logging.info("PersistData initialized")

    def run(self, state: ReceiptState) -> ReceiptState:
        logging.info("PersistData run")
        
        if "receipt" not in state:
            logging.warning("No receipt data found in state")
            return state

        # Convert receipt data to JSON string
        receipt_json = json.dumps(state["receipt"])
        
        # Create metadata (you can expand this as needed)
        metadata = {
            "timestamp": datetime.now(UTC).isoformat()
        }

        # Persist the data
        success = self.data_store.save_receipt(receipt_json, metadata)
        
        state["persistence_status"] = "success" if success else "failed"

        return state