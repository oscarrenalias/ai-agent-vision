from .receiptstate import ReceiptState

class PersistData:
    """
        Persists the receipt data into a data store
    """
    def __init__(self):
        pass

    def run(self, state: ReceiptState) -> ReceiptState:
        return(state)