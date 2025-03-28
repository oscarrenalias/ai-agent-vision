"""
Module for persisting receipt data to storage.
"""

import json
import logging
from datetime import UTC, datetime

from common.datastore import DataStore

from .receiptstate import ReceiptState


class PersistData:
    """Persists the receipt data into a data store"""

    def __init__(self, data_store: DataStore = None):
        self.data_store = data_store
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
        metadata = {"timestamp": datetime.now(UTC).isoformat()}

        # Persist the data
        success = self.data_store.save_receipt(receipt_json, metadata)

        state["persistence_status"] = "success" if success else "failed"

        return state
