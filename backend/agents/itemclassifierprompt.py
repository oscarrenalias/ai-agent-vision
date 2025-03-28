class ItemClassifierPrompt:
    template = """
        You are given a grocery list in JSON format where each item includes a name, quantity, and other metadata, in JSON format. Response must always be in JSON format, by extending the initial request. You must obey the output format under all circumstances. Please follow the formatting instructions exactly.

        Your task is to classify each item using a 3-level taxonomy and add a new "category" object to each item in the list using the following format:

        "category": {{
        "level_1": "<Food | Household | Other>",
        "level_2": "<Subcategory from predefined list>",
        "level_3": "<Specific type, if applicable; otherwise null>"
        }}

        Taxonomy:

        Level 1 must be one of:
        - Food
        - Household
        - Other

        Level 2 and Level 3 depend on the Level 1 category:
        If Level 1 is Food:

        - Fruits
        - Vegetables
        - Meats: Pork, Beef, Poultry, Mixed, Other
        - Fish & Seafood: Tuna, Salmon, Shrimp, Other
        - Dairy: Milk, Yoghurt, Cheese, Butter, Other
        - Bread & Bakery: Flatbread, Sliced Bread, Sweet Bakery, Other
        - Grains & Pasta
        - Sauces & Condiments
        - Snacks & Sweets
        - Beverages: Juice, Water, Soft Drink, Alcohol, Sports Drink, Other
        - Legumes & Pulses
        - Herbs & Spices
        - Prepared Foods: Sauces, Soups, Ready Meals, Other
        - Other Food

        If Level 1 is Household:

        - Cleaning Products: Toilet Cleaner, Surface Cleaner, Dishwashing, Other
        - Paper Goods
        - Laundry
        - Kitchen Supplies
        - Personal Hygiene

        If Level 1 is Other:
        - Deposits: Bottle Deposit, Can Deposit, Other
        - Unknown / Miscellaneous
        - Ensure that level_3 is always null if there’s no need for further classification.

        Please return the response in correctly formatted JSON. Do not return any additional comments or explanation.
    """
