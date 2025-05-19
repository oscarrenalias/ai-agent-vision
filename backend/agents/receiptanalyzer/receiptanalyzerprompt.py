from dataclasses import dataclass


@dataclass
class ReceiptAnalyzerPrompt:
    template: str = """
       You are analyzing a Finnish grocery receipt. Your task is to extract structured information in JSON format. Please follow the rules carefully.

        Do not guess. If some information is missing just return "N/A" in the relevant field. If you determine that the image is not of a receipt, just set all the fields in the formatting instructions to "N/A".

        You must obey the output format under all circumstances. Please follow the formatting instructions exactly.
        Do not return any additional comments or explanation.

        1. List of Items
        For each line item (product), extract the following:
        - Name of the item in Finnish
        - Translated name in English
        - Unit of measure (e.g., kg, unit, pkg, box, etc.). Include it as a string. If the unit is not specified, set to null.
        - Number of units, kilos, or packages (include unit type: e.g., kg, unit, pkg, box, etc.). Only include the number, do not include the unit type.
        - Price per unit (e.g., €/kg or €/unit). Only include the number, do not include the currency or anything else.
        - Total price paid for this item before discount
        - If a discount is listed under the item (indicated by a line starting with PLUSSA-ETU), include the total discount for that item. Otherwise, set to null.
        - Include a boolean flag depending on whether a loyalty discount was applied to this item
        Lines that start with PLUSSA-TASAERÄ can be ignored.

        2. Item classification
        Each one of the items in the list must be classified using a 3-level taxonomy. The classification must be added to each item in the list using the following format:
"category": {{
        "level_1": "<Food | Household | Other>",
        "level_2": "<Subcategory from predefined list>",
        "level_3": "<Specific type, if applicable; otherwise null>"
        }}

        Taxonomy:

        level_1 must be one of:
        - Food
        - Household
        - Other

        level_2 and level_2 depend on the level_1 category.

        level_1 is Food:

        - Fruits
        - Vegetables
        - Meats: use one of the following values for level_3=Pork, Beef, Poultry, Mixed, Other
        - Fish & Seafood: use one of the following values for level_3=Tuna, Salmon, Shrimp, Other
        - Dairy: use one of the following values for level_3=Milk, Yoghurt, Cheese, Butter, Other
        - Bread & Bakery: use one of the following values for level_3=Flatbread, Sliced Bread, Sweet Bakery, Other
        - Grains & Pasta
        - Sauces & Condiments
        - Snacks & Sweets
        - Beverages: use one of the following values for level_3=Juice, Water, Soft Drink, Alcohol, Sports Drink, Other
        - Legumes & Pulses
        - Herbs & Spices
        - Prepared Foods: use one of the following values for level_3=Sauces, Soups, Ready Meals, Other
        - Other Food

        If level_1 is Household:
        - Cleaning Products: use one of the following values for level_3=Toilet Cleaner, Surface Cleaner, Dishwashing, Other
        - Paper Goods
        - Laundry
        - Kitchen Supplies
        - Personal Hygiene

        If level_1 is Other:
        - Deposits: use one of the following values for level_3=Bottle Deposit, Can Deposit, Other
        - Unknown / Miscellaneous
        - Ensure that level_3 is always null if there’s no need for further classification.

        Do not use any other categories or subcategories. If you cannot classify an item, set Level 1 to "Other" and Level 2 to "Unknown / Miscellaneous". Set Level 3 to null.

        3. Receipt Summary
        Extract the following:
        - Total value of the items before loyalty discounts
        - Total amount saved via loyalty card discounts (PLUSSAT-EDUT YHTEENSÄ)
        - Total amount paid by the customer (including taxes)
        - Date of the receipt in YYYY-MM-DD format, if available. Otherwise, set to null. The receipt date
        is typically found in the top of the receipt, in the format "DD.MM.YYYY" (e.g., 01.01.2023).
        - Store name, if available. Otherwise, set to null. The store name is usually found in the top of
        the receipt, but is it not always present or identified as the store name.
       """
