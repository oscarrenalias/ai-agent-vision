from typing_extensions import TypedDict, Dict, Any, Optional, List
from pydantic import BaseModel, Field

class ReceiptItem(BaseModel):
    """
    List of Items. For each line item (product), extract the following
    """
    name_fi: Optional[str] = Field(description = "Name of the item in Finnish")
    name_en: Optional[str] = Field(description = "Translated name in English")
    unit_of_measure: Optional[str] = Field(description = "Unit of measure (e.g., kg, unit, pkg, box, etc.). Include it as a string. If the unit is not specified, set to null.")
    unit_price: Optional[float] = Field(description = "Price per unit (e.g., €/kg or €/unit). Only include the number, do not include the currency or anything else.")
    total_price: Optional[float] = Field(description = "Total price paid for this item before discount")
    quantity: Optional[float] = Field(description = "Number of units, kilos, or packages (include unit type: e.g., kg, unit, pkg, box, etc.). Only include the number, do not include the unit type.")
    loyalty_discount: Optional[float] = Field(description = "If a discount is listed under the item (indicated by a line starting with PLUSSA-ETU), include the total discount for that item. Otherwise, set to null.", default=0.0)
    has_loyalty_discount: Optional[bool] = Field(description = "true or false depending on whether a loyalty discount was applied to this item", default=False)
    
class ReceiptData(BaseModel):
    """
    Receipt Summary. Extract the following.
    """
    date: Optional[str] = Field(description = "Total value of the items before loyalty discounts")
    total_savings: Optional[str] = Field(description = "Total amount saved via loyalty card discounts (PLUSSAT-EDUT YHTEENSÄ)", default=None)
    place: Optional[str] = Field(description = "Place where the receipt was issued", default="")
    total: Optional[float] = Field(description = "Total amount paid by the customer (including taxes)")

class Receipt(BaseModel):
    """
    Top-level object for the receipt.
    """
    items: List[ReceiptItem] = Field(description = "List of items identified", default=[])
    receipt_data: ReceiptData = Field(description = "metadata about the receipt", default=None)

class ReceiptState(TypedDict):
    # image being processed
    receipt_image: Optional[Any] = None

    receipt_image_path: Optional[str] = None
    
    # receipt
    receipt: Optional[Receipt] = None

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