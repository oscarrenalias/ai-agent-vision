export type MealPlanItem = Record<string, any>;

/**
 * overall type fo agent state
 */
export type AgentState = {
  messages: string[] | null;

  last_receipt: Receipt | null;
  meal_plan: MealPlanItem | null;
  shopping_list: {} | null;

  // for receipt processing
  receipt_image_path: string | null;
};

export const AGENT_NAME = "mighty_assistant";

/*

Type of a receipt object:

{
  "items": [
    {
      "has_loyalty_discount": false,
      "item_category": {
        "level_1": "food",
        "level_2": "dairy",
        "level_3": "yogurt drinks"
      },
      "loyalty_discount": null,
      "name_en": "Danone Actimel strawberry",
      "name_fi": "Danone Actimel 12x100g mansikka",
      "quantity": 1,
      "total_price": 6.59,
      "unit_of_measure": "pkg",
      "unit_price": null
    },
    {
      "has_loyalty_discount": false,
      "item_category": {
        "level_1": "food",
        "level_2": "dairy",
        "level_3": "milk"
      },
      "loyalty_discount": null,
      "name_en": "Pirkka whole milk 1l",
      "name_fi": "Pirkka täysmaito 1l",
      "quantity": 4,
      "total_price": 5.16,
      "unit_of_measure": "unit",
      "unit_price": 1.29
    }
  ],
  "receipt_data": {
    "date": "182.91",
    "place": "K-Citymarket Sello",
    "total": 181.18,
    "total_savings": "1.73"
  }
}
*/

export type ItemCategory = {
  level_1: string;
  level_2: string;
  level_3: string;
};

export type ReceiptListItem = {
  has_loyalty_discount: boolean;
  item_category: ItemCategory;
  loyalty_discount: number | null;
  name_en: string;
  name_fi: string;
  quantity: number;
  total_price: number;
  unit_of_measure: string;
  unit_price: number | null;
};

export type ReceiptData = {
  date: string;
  place: string;
  total: number;
  total_savings: string;
};

export type Receipt = {
  items: ReceiptListItem[];
  receipt_data: ReceiptData;
};

/**
 * Types for a shopping list
 */
export type ShoppingListItem = {
  description: string;
  matched_product_name: string;
  price: number;
  quantity_needed: number;
  unit_of_measurement: string;
};

export type ShoppingList = {
  shopping_list: ShoppingListItem[];
};
