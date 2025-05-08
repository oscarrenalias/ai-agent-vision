import { Receipt } from "../lib/types";
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
        background: "var(--card-bg, #fff)",
        color: "var(--card-fg, #23272e)",
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
                idx !== receipt.items.length - 1
                  ? "1px solid var(--card-border, #eee)"
                  : undefined,
              paddingBottom: 12,
              marginBottom: 12,
            }}
          >
            <div style={{ fontWeight: 600 }}>
              {item.name_en} ({item.name_fi})
            </div>
            <div style={{ fontSize: 14, color: "var(--card-muted, #666)" }}>
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
