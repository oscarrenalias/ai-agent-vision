from .receiptstate import ReceiptState
import logging

class ItemClassifier:
    """
        Classifies items in the receipt according to their type
    """
    def __init__(self):
        logging.info("ItemClassifier initialized")
        pass

    def run(self, state: ReceiptState) -> ReceiptState:
        return(state)