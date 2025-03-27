# Initial prompt

Given the attached JSON structure, what would be a good taxonomy to classify items from the grocery list? I think that we need 3 a taxonomy with 3 levels according to the following criteria:
1. food (fruits, vegetables, meats, bread, etc), household items (cleaning products, toilet paper, etc), or other (for everything else)
2. for food, it should be possible to identiy key things like fruits, vegetables, meats, bread, dairy, and others
3. depending on the type of food, there should be a level of classification to determine if the meat is pork, poultry or beef; for dairy, if an item is milk, yoghourt, etc. The same should be considered for all other types of items.
4. for household items, come up with a basic level 2 classification
5. for items in the "other" category, please propose something

Can you finally write a prompt for this taxonomy, so that other LLMs can use it to classify the items? The output should be added to the input JSON structure, adding a "category" attribute for each item with the following fields:

- level_1: string with the first category
- level_2: string wtih the second category
- level_3: string with the third category. Set is to null if not required for the item.

# OpenAI Response

```
Here's a well-structured taxonomy based on your criteria, along with a prompt that LLMs can use to classify grocery items accordingly.

Taxonomy Design (3 Levels)
Level 1 Categories:
- Food
- Household
- Other

Level 2 Subcategories:
Food:
- Fruits
- Vegetables
- Meats
- Fish & Seafood
- Dairy
- Bread & Bakery
- Grains & Pasta
- Sauces & Condiments
- Snacks & Sweets
- Beverages
- Legumes & Pulses
- Herbs & Spices
- Prepared Foods
- Other Food

Household:
- Cleaning Products
- Paper Goods (e.g., toilet paper, paper towels)
- Laundry
- Kitchen Supplies
- Personal Hygiene

Other:
- Deposits (e.g., bottle deposits)
- Unknown / Miscellaneous

Level 3 Specifics (only if applicable)
- Meats → Pork, Beef, Poultry, Mixed, Other
- Fish & Seafood → Tuna, Salmon, Shrimp, Other
- Dairy → Milk, Yoghurt, Cheese, Butter, Other
- Bread & Bakery → Flatbread, Sliced Bread, Sweet Bakery, Other
- Beverages → Juice, Water, Soft Drink, Alcohol, Sports Drink, Other
- Cleaning Products → Toilet Cleaner, Surface Cleaner, Dishwashing, Other
- Deposits → Bottle Deposit, Can Deposit, Other
- Prepared Foods → Sauces, Soups, Ready Meals, Other

LLM Classification Prompt

You are given a grocery list where each item includes a name, quantity, and other metadata, in JSON format. Response must always be in JSON format, by extending the initial request. You must obey the output format under all circumstances. Please follow the formatting instructions exactly.

Your task is to classify each item using a 3-level taxonomy and add a new "category" object to each item in the list using the following format:

"category": {
  "level_1": "<Food | Household | Other>",
  "level_2": "<Subcategory from predefined list>",
  "level_3": "<Specific type, if applicable; otherwise null>"
}

Taxonomy:

Level 1 must be one of:
- Food
- Household
- Other

Level 2 and Level 3 depend on the Level 1 category:
If Level 1 is Food:

- Fruits
- Vegetables
- Meats → {Pork, Beef, Poultry, Mixed, Other}
- Fish & Seafood → {Tuna, Salmon, Shrimp, Other}
- Dairy → {Milk, Yoghurt, Cheese, Butter, Other}
- Bread & Bakery → {Flatbread, Sliced Bread, Sweet Bakery, Other}
- Grains & Pasta
- Sauces & Condiments
- Snacks & Sweets
- Beverages → {Juice, Water, Soft Drink, Alcohol, Sports Drink, Other}
- Legumes & Pulses
- Herbs & Spices
- Prepared Foods → {Sauces, Soups, Ready Meals, Other}
- Other Food

If Level 1 is Household:

- Cleaning Products → {Toilet Cleaner, Surface Cleaner, Dishwashing, Other}
- Paper Goods
- Laundry
- Kitchen Supplies
- Personal Hygiene

If Level 1 is Other:
- Deposits → {Bottle Deposit, Can Deposit, Other}
- Unknown / Miscellaneous
- Ensure that level_3 is always null if there’s no need for further classification.

Please return the response in correctly formatted JSON. 
```