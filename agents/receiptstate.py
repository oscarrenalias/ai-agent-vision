from typing_extensions import TypedDict, Dict, Any, Optional, List
from pydantic import BaseModel

class Item(BaseModel):
    name_fi: Optional[str]
    name_en: Optional[str]
    unit_of_measure: Optional[str]
    unit_price: Optional[float]
    total_price: Optional[float]
    quantity: Optional[float]
    loyalty_discount: Optional[float] = None
    has_loyalty_discount: Optional[bool] = False

class ReceiptData(BaseModel):
    date: Optional[str]
    place: Optional[str]
    total: Optional[float]

class ReceiptState(TypedDict):
    # image being processed
    receipt_image: Optional[Any] = None

    receipt_image_path: Optional[str] = None
    
    # List of items identified
    item_list: Optional[List[Item]] = None

    # metadata about the receipt
    receipt_data: Optional[ReceiptData] = None

    # Processing metadata
    messages: List[Dict[str, Any]] = None

    def __init__(
        self,
        receipt_image_path: Optional[str] = None,
        receipt_image: Optional[Any] = None,
    ):
        self.receipt_image_path = receipt_image_path
        self.receipt_image = receipt_image

    # generate a string representation from this object but represent the image field as "..."
    def __str__(self):
        return str({k: v if k != "receipt_image" else "..." for k, v in self.items()})