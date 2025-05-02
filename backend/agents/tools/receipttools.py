import json
import logging
from typing import List

from langchain_core.tools import tool

from common.datastore import get_data_store

logger = logging.getLogger(__name__)


def get_tools() -> List:
    """
    Returns a list of tools that can be used in the chat.
    """
    return [get_receipts_by_date, get_items_per_item_type]


def mongo_json_default(obj):
    from datetime import datetime

    from bson import ObjectId

    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@tool
def get_receipts_by_date(start_date: str, end_date: str, store: None) -> str:
    """
    Get the receipts and their associated items for a given period of time, including all receipt data.

    Example prompts:
    - how much did we spend on groceries in 2025 so far?
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

    data_store = get_data_store()
    receipts = data_store.get_receipts_by_date(start_date, end_date)

    return json.dumps(receipts, default=mongo_json_default)


def is_correct_item_type(item, item_type):
    category = item["item_category"]
    if not category:
        return False

    if not isinstance(category, dict):
        return False

    if item_type.lower() in (category.get("level_1") or "__not_defined__").lower():
        return True
    if item_type.lower() in (category.get("level_2") or "__not_defined__").lower():
        return True
    if item_type.lower() in (category.get("level_3") or "__not_defined__").lower():
        return True

    return False


@tool
def get_items_per_item_type(item_type: str) -> str:
    """
    Retrieves a list of items based on their item type based on existing categorization in receipts.
    For each item, it will provide the date when it was purchased, the price, the store, price per unit and the quantity.

    If there's an item that does not make sense to be in the list, do not mention it. Just state something like
    "An item of an unexpected type was included", or something along those lines.

    Example prompts:
    - how much poultry have we bought?
    - how much pasta have we bought?
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

    data_store = get_data_store()
    receipts = data_store.get_items_per_item_type(item_type)
    logger.info(f"Found {len(receipts)} receipts for {item_type}")
    response_data = []

    for receipt in receipts:
        for item in receipt["items"]:
            if is_correct_item_type(item, item_type):
                """
                response_data.append(
                    f"Name: {item['name_fi']}, \
                    Quantity: {item['quantity']}, \
                    Total price: {item['total_price']}, \
                    Price per unit: {item['unit_price']}, \
                    Store: {receipt['receipt_data']['place']}, \
                    Purchased on: {receipt['receipt_data']['date'].isoformat() if receipt['receipt_data']['date'] else 'Unknown'}"
                )
                """
                response_data.append(item)

    return json.dumps(response_data)
