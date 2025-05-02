/*

Generates a card out of a shopping list, with the following properties:

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

/*export interface ReceiptCardProps {
  receipt: Receipt;
}*/

import React from "react";

interface ReceiptCardProps {
  receipt: Receipt;
  height?: string | number;
}

const ReceiptCard: React.FC<ReceiptCardProps> = ({ receipt, height = 400 }) => {
  if (!receipt || !receipt.items || receipt.items.length === 0) return null;

  return (
    <div
      style={{
        boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
        borderRadius: 12,
        padding: 24,
        background: "var(--card-bg)",
        color: "var(--card-fg)",
        height: typeof height === "number" ? `${height}px` : height,
        display: "flex",
        flexDirection: "column",
        overflowY: "auto",
        minWidth: 280,
        maxWidth: 420,
        margin: "0 auto",
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: 16 }}>🧾 Receipt</h2>
      <div style={{ fontSize: 15, marginBottom: 16 }}>
        <strong>Store:</strong> {receipt.receipt_data.place} <br />
        <strong>Date:</strong> {receipt.receipt_data.date} <br />
        <strong>Total:</strong> {receipt.receipt_data.total} € <br />
        <strong>Savings:</strong> {receipt.receipt_data.total_savings} €
      </div>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {receipt.items.map((item, idx) => (
          <li
            key={idx}
            style={{
              borderBottom:
                idx !== receipt.items.length - 1 ? "1px solid #eee" : undefined,
              paddingBottom: 12,
              marginBottom: 12,
            }}
          >
            <div style={{ fontWeight: 600 }}>
              {item.name_en} ({item.name_fi})
            </div>
            <div style={{ fontSize: 14, color: "#666" }}>
              Category: {item.item_category.level_1} /{" "}
              {item.item_category.level_2} / {item.item_category.level_3}
              <br />
              Qty: {item.quantity} {item.unit_of_measure} | Total:{" "}
              {item.total_price} €
              {item.unit_price !== null && (
                <>
                  <br />
                  Unit price: {item.unit_price} €
                </>
              )}
              {item.has_loyalty_discount && item.loyalty_discount !== null && (
                <>
                  <br />
                  Loyalty discount: {item.loyalty_discount} €
                </>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ReceiptCard;
