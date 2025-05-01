import React from "react";

export type ShoppingListItem = {
  description: string;
  matched_product_name: string;
  price: number;
  quantity_needed: number;
  unit_of_measurement: string;
};

export type ShoppingListProps = {
  shopping_list: ShoppingListItem[];
};

interface ShoppingListCardProps extends ShoppingListProps {
  height?: string | number; // e.g., '400px' or 400
}

const ShoppingListCard: React.FC<ShoppingListCardProps> = ({
  shopping_list,
  height = 400,
}) => {
  if (!shopping_list || shopping_list.length === 0) return null;

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
      <h2 style={{ marginTop: 0, marginBottom: 16 }}>🛒 Shopping List</h2>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {shopping_list.map((item, idx) => (
          <li
            key={idx}
            style={{
              borderBottom:
                idx !== shopping_list.length - 1 ? "1px solid #eee" : undefined,
              paddingBottom: 12,
              marginBottom: 12,
            }}
          >
            <div style={{ fontWeight: 600 }}>{item.description}</div>
            <div style={{ fontSize: 14, color: "#666" }}>
              Matched: {item.matched_product_name}
              <br />
              Price: {item.price} €&nbsp;| &nbsp;Qty: {item.quantity_needed}{" "}
              {item.unit_of_measurement}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ShoppingListCard;
