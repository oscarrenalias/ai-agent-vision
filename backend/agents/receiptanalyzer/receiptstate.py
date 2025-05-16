from copilotkit import CopilotKitState
from pydantic import BaseModel, Field
from typing_extensions import Any, List, Literal, Optional


class ReceiptItemCategory(BaseModel):
    """
    Used to categoryze items in the receipt according to a simple taxonomy
    """

    level_1: Optional[str] = Field(description="Level 1 category (e.g., food, household, other, etc.)")
    level_2: Optional[str] = Field(
        description="Level 2 category (e.g., fruits, vegetables, meats, depending on the level 1 category)"
    )
    level_3: Optional[str] = Field(
        description="Level 3 category (e.g., pork, beef, poultry, mixed, other, etc.)",
        default=None,
    )


class ReceiptItem(BaseModel):
    """
    List of Items. For each line item (product), extract the following
    """

    name_fi: Optional[str] = Field(description="Name of the item in Finnish")
    name_en: Optional[str] = Field(description="Translated name in English")
    unit_of_measure: Optional[str] = Field(
        description="Unit of measure (e.g., kg, unit, pkg, box, etc.). Include it as a string. If the unit is not specified, set to null."
    )
    unit_price: Optional[float] = Field(
        description="Price per unit (e.g., €/kg or €/unit). Only include the number, do not include the currency or anything else."
    )
    total_price: Optional[float] = Field(description="Total price paid for this item before discount")
    quantity: Optional[float] = Field(
        description="Number of units, kilos, or packages (include unit type: e.g., kg, unit, pkg, box, etc.). Only include the number, do not include the unit type."
    )
    loyalty_discount: Optional[float] = Field(
        description="If a discount is listed under the item (indicated by a line starting with PLUSSA-ETU), include the total discount for that item. Otherwise, set to null.",
        default=0.0,
    )
    has_loyalty_discount: Optional[bool] = Field(
        description="true or false depending on whether a loyalty discount was applied to this item",
        default=False,
    )
    item_category: Optional[ReceiptItemCategory] = Field(description="Category of the item")


class ReceiptData(BaseModel):
    """
    Receipt Summary. Extract the following.
    """

    date: Optional[str] = Field(description="Total value of the items before loyalty discounts")
    total_savings: Optional[str] = Field(
        description="Total amount saved via loyalty card discounts (PLUSSAT-EDUT YHTEENSÄ)",
        default=None,
    )
    place: Optional[str] = Field(description="Place where the receipt was issued", default="")
    total: Optional[float] = Field(description="Total amount paid by the customer (including taxes)")


class Receipt(BaseModel):
    """
    Top-level object for the receipt.
    """

    items: List[ReceiptItem] = Field(description="List of items identified", default=[])
    receipt_data: ReceiptData = Field(description="metadata about the receipt", default=None)


class ReceiptState(CopilotKitState):
    # image being processed
    receipt_image: Optional[Any] = None

    receipt_image_path: Optional[str] = None

    # receipt
    receipt: Optional[Receipt] = None

    # Tracks status of the persistence operation
    persistence_status: Literal["success", "failed"] = None

    def __init__(
        self,
        receipt_image_path: Optional[str] = None,
        receipt_image: Optional[Any] = None,
    ):
        self.receipt_image_path = receipt_image_path
        self.receipt_image = receipt_image

    def make_instance():
        """
        Create a new instance of the ReceiptState object. Needed because this class
        is a TypedDict and constructor is not automatically generated.
        """
        return ReceiptState(
            receipt_image_path=None,
            receipt_image=None,
            receipt={},
            messages=[],
            persistence_status=None,
        )
