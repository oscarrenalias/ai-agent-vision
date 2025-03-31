import logging
from typing import List, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def get_tools() -> List:
    """
    Returns a list of tools that can be used in the chat.
    """
    return [get_groceries_per_period, get_data_per_item_type]


class ReceiptItemData(BaseModel):
    """
    Schema class for some of the tools
    """

    date: str = Field(description="Date when the item was purchased")
    description: str = Field(description="Description of the item")
    price: float = Field(description="Price of the item")
    store: str = Field(description="Store where the item was purchased")
    price_per_unit: float = Field(description="Price per unit of the item")
    quantity: float = Field(description="Quantity of the item purchased")
    item_type_level1: str = Field(description="Level 1 item type")
    item_type_level2: Optional[str] = Field(description="Level 2 item type", default=None)
    item_type_level3: Optional[str] = Field(description="Level 3 item type", default=None)

    def __str__(self):
        """
        Returns a string representation of the ReceiptItemData object. Used for the LLM to process the data.
        """
        return f"item: {self.description}, quantity: {self.quantity}, price: ({self.price}), location: {self.store}, date: {self.date}"


class ReceiptData(BaseModel):
    """
    Schema class for the receipt data.

    TODO: might want to include the total discount
    """

    items: List[ReceiptItemData] = Field(description="List of items in the receipt")
    total_price: float = Field(description="Total price of the receipt")
    date: str = Field(description="Date of the receipt")
    store: str = Field(description="Store where the receipt was issued")

    def __str__(self):
        """
        Returns a string representation of the ReceiptData object. Used for the LLM to process the data.
        """
        items_str = "\n".join([str(item) for item in self.items])
        return f"Receipt from {self.store} on {self.date}: \nTotal Price: {self.total_price}\nItems: \n{items_str}"


@tool
def get_groceries_per_period(start_date: str, end_date: str, store: None) -> str:
    """
    Get the receipts and their associated items for a given period of time, including all metadata.

    Example prompts:
    - how much did we spend on groceries in the last year?
    - how much did we pay for the last groceries?
    - how much do we usually spend on groceries in store K-Citymarket?

    Args:
        start_date (str): The start date of the period as YYYY-MM-DD.
        end_date (str): The end date of the period as YYYY-MM-DD.

    Returns:
        str: A list of receipts and their associated items. The response string includes:
            - Total price of the receipt. Currency is always €.
            - Date of the receipt.
            - Store where the receipt was issued.
            - List of items in the receipt, including:
                - Date when the item was purchased specified as YYYY-MM-DD
                - Price of the item
                - Store where the item was purchased
                - Price per unit of the item
                - Quantity of the item purchased, must always use €
                - Level 1 item type (food/household/other)
                - Level 2 item type (meat/vegetable/fruit/other)
                - Level 3 item type (specific type such as chicken or fish, if applicable; otherwise None)
    """
    logger.info(f"Getting groceries from {start_date} to {end_date}")

    receipt_list = [
        ReceiptData(
            items=[
                ReceiptItemData(
                    date="2025-02-01",
                    description="Frozen Chicken",
                    price=10.0,
                    store="K-Citymarket",
                    price_per_unit=2.0,
                    quantity=5.0,
                    item_type_level1="food",
                    item_type_level2="meats",
                    item_type_level3="chicken",
                ),
                ReceiptItemData(
                    date="2025-02-01",
                    description="Fresh Chicken",
                    price=20.0,
                    store="K-Citymarket",
                    price_per_unit=4.0,
                    quantity=10.0,
                    item_type_level1="food",
                    item_type_level2="meats",
                    item_type_level3="chicken",
                ),
            ],
            total_price=30.0,
            date="2025-02-01",
            store="K-Citymarket",
        )
    ]

    results = "\n".join([str(receipt) for receipt in receipt_list])

    logger.info("Returning receipt data {results}")
    return results


@tool
def get_data_per_item_type(item_type: str) -> str:
    """
    Retrieves a list of items based on their item type based on existing categorization in receipts.
    For each item, it will provide the date when it was purchased, the price, the store, price per unit and the quantity.

    If there's an item that does not make sense to be in the list, do not mention it. Just state something like
    "An item of an unexpected type was included", or something along those lines.

    Example prompts:
    - how much chicken have we bought?
    - how much meat did we buy last week?
    - how much vegetables did we buy in Store A?

    Args:
        item_type (str): The type of item to get groceries for.

    Returns:
        str: A string containing the list of items based on the given item type. The response string includes:
            - Date when the item was purchased specified as YYYY-MM-DD
            - Price of the item
            - Store where the item was purchased
            - Price per unit of the item
            - Quantity of the item purchased, must always use €
            - Level 1 item type (food/household/other)
            - Level 2 item type (meat/vegetable/fruit/other)
            - Level 3 item type (specific type such as chicken or fish, if applicable; otherwise None)
    """
    logger.info(f"Getting groceries for {item_type}")

    # Simulate a call to the database
    receipt_item_list = [
        # first two items are always generated to be the requested type
        ReceiptItemData(
            date="2023-10-01",
            description=f"Frozen {item_type}",
            price=10.0,
            store="Store A",
            price_per_unit=2.0,
            quantity=5.0,
            item_type_level1="food",
            item_type_level2="meats",
            item_type_level3=item_type,
        ),
        ReceiptItemData(
            date="2023-11-01",
            price=20.0,
            description=f"Fresh {item_type}",
            store="Store B",
            price_per_unit=4.0,
            quantity=10.0,
            item_type_level1="food",
            item_type_level2="meats",
            item_type_level3=item_type,
        ),
        # Last item is always lettuce-vegetables
        ReceiptItemData(
            date="2023-11-01",
            price=20.0,
            description="Eco Lettuce",
            store="Store A",
            price_per_unit=2.5,
            quantity=1.0,
            item_type_level1="food",
            item_type_level2="vegetables",
            item_type_level3=None,
        ),
    ]

    # process the list into a format that is suitable for the LLM; uses the object's __str__ method to generate a
    # readable description that the LLM can process
    results = [str(receipt_item) for receipt_item in receipt_item_list]
    response = "\n".join(results)

    logger.info(f"Returning receipt data {response}")
    # return [receipt_item.model_dump() for receipt_item in results]
    return response
