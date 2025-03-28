"""
PostgreSQL data storage implementation for the AI Agent Vision application.
This module provides a PostgreSQL implementation of the DataStore interface.
"""

import json
import logging
from datetime import datetime, UTC
from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from .datastore import DataStore

class PostgresStore(DataStore):
    """
    PostgreSQL implementation of the DataStore interface.
    This class provides methods to store and retrieve data from a PostgreSQL database.
    """
    
    def __init__(self, connection_params: Dict[str, Any] = None):
        """
        Initialize the PostgreSQL store with connection parameters
        
        Args:
            connection_params: Dictionary containing PostgreSQL connection parameters
                               (host, port, dbname, user, password)
        """
        self.connection_params = connection_params or {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'receipts',
            'user': 'postgres',
            'password': 'postgres'
        }
        logging.info(f"PostgreSQL store initialized with host: {self.connection_params.get('host')}, "
                     f"port: {self.connection_params.get('port')}, "
                     f"database: {self.connection_params.get('dbname')}")

    def _get_connection(self):
        """
        Get a connection to the PostgreSQL database
        
        Returns:
            PostgreSQL connection object
        """
        try:
            return psycopg2.connect(**self.connection_params)
        except Exception as e:
            logging.error(f"Error connecting to PostgreSQL: {str(e)}")
            raise

    def initialize(self):
        """Create the receipts table if it doesn't exist"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS receipts (
                            id SERIAL PRIMARY KEY,
                            receipt_data JSONB NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                            updated_at TIMESTAMP WITH TIME ZONE NOT NULL
                        )
                    ''')
                conn.commit()
            logging.info("PostgreSQL database initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing PostgreSQL database: {str(e)}")
            raise

    def save_receipt(self, receipt_data: str, metadata: dict) -> bool:
        """
        Save receipt data to PostgreSQL
        
        Args:
            receipt_data: JSON string containing receipt data
            metadata: Dictionary with additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            current_time = datetime.now(UTC)
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO receipts (receipt_data, created_at, updated_at) VALUES (%s::jsonb, %s, %s)',
                        (receipt_data, current_time, current_time)
                    )
                conn.commit()
            logging.info("Receipt saved to PostgreSQL successfully")
            return True
        except Exception as e:
            logging.error(f"Error saving receipt to PostgreSQL: {str(e)}")
            return False
            
    def get_all_receipts(self) -> List[Dict[str, Any]]:
        """
        Retrieve all receipts from the database
        
        Returns:
            List of receipt dictionaries with id, created_at, updated_at, and data fields
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('SELECT id, receipt_data, created_at, updated_at FROM receipts ORDER BY created_at DESC')
                    rows = cursor.fetchall()
                    
                    receipts = []
                    for row in rows:
                        receipt = {
                            'id': row['id'],
                            'created_at': row['created_at'].isoformat(),
                            'updated_at': row['updated_at'].isoformat(),
                            'data': row['receipt_data']  # PostgreSQL automatically converts JSONB to Python dict
                        }
                        receipts.append(receipt)
                    
                    return receipts
        except Exception as e:
            logging.error(f"Error retrieving receipts from PostgreSQL: {str(e)}")
            return []
            
    def get_receipt_by_id(self, receipt_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific receipt by ID
        
        Args:
            receipt_id: The ID of the receipt to retrieve
            
        Returns:
            Receipt dictionary or None if not found
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('SELECT id, receipt_data, created_at, updated_at FROM receipts WHERE id = %s', (receipt_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        receipt = {
                            'id': row['id'],
                            'created_at': row['created_at'].isoformat(),
                            'updated_at': row['updated_at'].isoformat(),
                            'data': row['receipt_data']  # PostgreSQL automatically converts JSONB to Python dict
                        }
                        return receipt
                    return None
        except Exception as e:
            logging.error(f"Error retrieving receipt {receipt_id} from PostgreSQL: {str(e)}")
            return None
            
    def update_receipt(self, receipt_id: int, receipt_data: str, metadata: dict) -> bool:
        """
        Update an existing receipt
        
        Args:
            receipt_id: The ID of the receipt to update
            receipt_data: JSON string containing updated receipt data
            metadata: Dictionary with additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            current_time = datetime.now(UTC)
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        'UPDATE receipts SET receipt_data = %s::jsonb, updated_at = %s WHERE id = %s',
                        (receipt_data, current_time, receipt_id)
                    )
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error updating receipt {receipt_id} in PostgreSQL: {str(e)}")
            return False
            
    def delete_receipt(self, receipt_id: int) -> bool:
        """
        Delete a receipt from the database
        
        Args:
            receipt_id: The ID of the receipt to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('DELETE FROM receipts WHERE id = %s', (receipt_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error deleting receipt {receipt_id} from PostgreSQL: {str(e)}")
            return False
