from .receiptstate import ReceiptState
import logging

class PersistData:
    """
        Persists the receipt data into a data store
    """
    def __init__(self):
        logging.info("PersistData initialized")

    def run(self, state: ReceiptState) -> ReceiptState:
        return(state)