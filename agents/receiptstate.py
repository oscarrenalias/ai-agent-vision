from typing_extensions import TypedDict, Dict, Any, Optional, List
from pydantic import BaseModel

class Item(BaseModel):
    original_name: Optional[str]
    translated_name: Optional[str]
    price: Optional[float]
    quantity: Optional[float]
    price_unit: Optional[str]
    total_price: Optional[float]
    category: Optional[str]
    subcategory: Optional[str]

class ReceiptData(BaseModel):
    date: Optional[str]
    place: Optional[str]
    total: Optional[float]

class ReceiptState(TypedDict):
    # image being processed
    receipt_image: None
    
    # List of items identified
    item_list: Optional[List[Item]]

    # metadata about the receipt
    receipt_data: Optional[ReceiptData]

    # Processing metadata
    messages: List[Dict[str, Any]]

    def __init__(self, receipt_image=None):
        self.receipt_image = receipt_image