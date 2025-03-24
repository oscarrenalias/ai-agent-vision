from .receiptstate import ReceiptState
import logging

class ReceiptAnalyzer:
    """
        Analyzes purchases receipts
    """
    def __init__(self):
        logging.info("ReceiptAnalyzer initialized")

    def run(self, state: ReceiptState) -> ReceiptState:
        return(state)