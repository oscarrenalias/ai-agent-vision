"""
Module for persisting receipt data to storage.
"""

import json
import logging
from datetime import UTC, datetime

from langchain.schema import AIMessage

from common.datastore import DataStore

from .receiptstate import ReceiptState

logger = logging.getLogger(__name__)


class PersistData:
    def __init__(self, data_store: DataStore = None):
        self.data_store = data_store
        self.data_store.initialize()

    def run(self, state: ReceiptState) -> ReceiptState:
        logger.debug("PersistData run")

        if "receipt" not in state:
            logger.warning("No receipt data found in state")
            return state

        # Convert receipt data to JSON string
        receipt_json = json.dumps(state["receipt"])
        metadata = {"timestamp": datetime.now(UTC).isoformat()}
        success = self.data_store.save_receipt(receipt_json, metadata)
        state["persistence_status"] = "success" if success else "failed"
        state["messages"].append(
            AIMessage("Receipt data persisted successfully." if success else "Failed to persist receipt data.")
        )

        return state
