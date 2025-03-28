# Prompts to help analyze a receipt

# Input prompt (to generate a more comprehensive prompt)

```
Based on the attached receipt, can you define a prompt that will help an LLM to analyze the receipt and output the following information:

* List of items
* Per item, provide the total price, as well as the price per unit or kilo as well as the total number of units
* The unit price can be kilo, box, or just “unit”
* Some items have a discount for holders of the chain’s loyalty card, and they will have a line just below with text “PLUSSA-ERÄ” or “PLUSSA-TASAERÄ” with the overall discount on the full price. In cases where an item has a loyalty discount, include the total amount as well as the discount, no need to calculate the  difference

The receipt is in Finnish, so the response needs to provide all texts both in Finnish as well as translated to English, including the units of measure for items.

The receipt also includes the full total at the bottom, which must be recorded. The receipt also includes loyalty card benefits as a total amount of savings, which must be recorded.

Please also propose a JSON schema for the response that includes all the fields described above.
```

# OpenAI Response

```
You are analyzing a Finnish grocery receipt. Your task is to extract structured information in JSON format. Please follow the rules carefully.

1. List of Items
For each line item (product), extract the following:
- name_fi: Name of the item in Finnish
- name_en: Translated name in English
- quantity: Number of units, kilos, or packages (include unit type: e.g., kg, unit, pkg, box, etc.)
- unit_price: Price per unit (e.g., €/kg or €/unit)
- total_price: Total price paid for this item before discount
- loyalty_discount: If a discount is listed under the item (indicated by a line starting with PLUSSA-ERÄ or PLUSSA-TASAERÄ), include the total discount for that item. Otherwise, set to null.
- has_loyalty_discount: true or false

2. Receipt Summary
Extract the following:
- total_before_discounts: Total value of the items before loyalty discounts
- total_loyalty_savings: Total amount saved via loyalty card discounts (PLUSSAT-EDUT YHTEENSÄ)
- total_paid: Total amount paid by the customer (including taxes)
```

# Mistral AI Response

```
You are provided with a receipt in Finnish. Your task is to analyze the receipt and extract the following information:

1. List of Items: Extract the name of each item.
2. Per Item Details: For each item, provide:
    * Total price
    * Price per unit or kilo
    * Total number of units
    * Unit of measure (kilo, box, unit)
3. Loyalty Discounts: Some items have a discount for loyalty card holders, indicated by "PLUSSA-ERÄ" or "PLUSSA-TASAERÄ" with the overall discount. If an item has a loyalty discount, include:
    * The total amount of the discount
4. Total Amount: Record the full total at the bottom of the receipt.
5. Loyalty Card Benefits: Record the total amount of savings from loyalty card benefits.
Provide all texts in both Finnish and English, including the units of measure for items.
```

Proposed schema:

```
{
  "items": [
    {
      "name_fi": "string",  // Item name in Finnish
      "name_en": "string",  // Item name in English
      "total_price": "number",  // Total price of the item
      "price_per_unit": "number",  // Price per unit or kilo
      "total_units": "number",  // Total number of units
      "unit_fi": "string",  // Unit of measure in Finnish
      "unit_en": "string",  // Unit of measure in English
      "loyalty_discount": "number"  // Loyalty discount if applicable
    }
  ],
  "total_amount": "number",  // Full total amount of the receipt
  "loyalty_savings": "number"  // Total savings from loyalty card benefits
}
```
