import sqlite3
import json
import logging
from datetime import datetime, UTC
from typing import List, Dict, Optional, Any

class ReceiptRepository:
    """
    Repository class for managing CRUD operations for receipts in the database.
    This class provides methods to create, read, update, and delete receipt records.
    """
    
    def __init__(self, db_path: str = "../receipts.db"):
        """
        Initialize the repository with the database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._initialize_db()
        
    def _initialize_db(self):
        """Create the receipts table if it doesn't exist"""
        try:
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
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")
            raise
            
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
            current_time = datetime.now(UTC).isoformat()
            receipt_json = json.dumps(receipt_data)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO receipts (receipt_data, created_at, updated_at) VALUES (?, ?, ?)',
                    (receipt_json, current_time, current_time)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logging.error(f"Error creating receipt: {str(e)}")
            raise
            
    def get_all_receipts(self) -> List[Dict[str, Any]]:
        """
        Retrieve all receipts from the database.
        
        Returns:
            List of receipt dictionaries with id, created_at, updated_at, and data fields
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT id, receipt_data, created_at, updated_at FROM receipts ORDER BY created_at DESC')
                rows = cursor.fetchall()
                
                receipts = []
                for row in rows:
                    receipt = {
                        'id': row['id'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'data': json.loads(row['receipt_data'])
                    }
                    receipts.append(receipt)
                
                return receipts
        except Exception as e:
            logging.error(f"Error retrieving receipts: {str(e)}")
            return []
            
    def get_receipt_by_id(self, receipt_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific receipt by ID.
        
        Args:
            receipt_id: The ID of the receipt to retrieve
            
        Returns:
            Receipt dictionary or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT id, receipt_data, created_at, updated_at FROM receipts WHERE id = ?', (receipt_id,))
                row = cursor.fetchone()
                
                if row:
                    receipt = {
                        'id': row['id'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'data': json.loads(row['receipt_data'])
                    }
                    return receipt
                return None
        except Exception as e:
            logging.error(f"Error retrieving receipt {receipt_id}: {str(e)}")
            return None
            
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
            current_time = datetime.now(UTC).isoformat()
            receipt_json = json.dumps(receipt_data)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE receipts SET receipt_data = ?, updated_at = ? WHERE id = ?',
                    (receipt_json, current_time, receipt_id)
                )
                conn.commit()
                return cursor.rowcount > 0
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
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM receipts WHERE id = ?', (receipt_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error deleting receipt {receipt_id}: {str(e)}")
            return False
