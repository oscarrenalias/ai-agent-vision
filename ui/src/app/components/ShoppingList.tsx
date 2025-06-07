import React, { useState } from "react";

interface ShoppingListProps {
  items: string[];
  onAdd: (item: string) => void;
  onDelete: (index: number) => void;
}

export default function ShoppingList({
  items,
  onAdd,
  onDelete,
}: ShoppingListProps) {
  const [input, setInput] = useState("");

  const handleAdd = () => {
    if (input.trim()) {
      onAdd(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleAdd();
    }
  };

  return (
    <div
      style={{
        background: "#e57373",
        borderRadius: 12,
        padding: 20,
        width: 320,
        boxShadow: "0 4px 16px 0 rgba(0,0,0,0.10)",
        color: "#fff",
        fontFamily: "inherit",
      }}
    >
      {/* <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
        <input
          type="text"
          placeholder="Add an item..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          style={{
            flex: 1,
            border: "none",
            borderRadius: 6,
            padding: "8px 12px",
            fontSize: 18,
            background: "#f8bdbd",
            color: "#fff",
            outline: "none",
            marginRight: 8,
          }}
        />
        <button
          onClick={handleAdd}
          style={{
            background: "#f8bdbd",
            border: "none",
            borderRadius: 6,
            width: 36,
            height: 36,
            color: "#fff",
            fontSize: 24,
            cursor: "pointer",
          }}
          aria-label="Add item"
        >
          +
        </button>
      </div> */}
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {items.map((item, idx) => (
          <li
            key={idx}
            style={{ display: "flex", alignItems: "center", marginBottom: 12 }}
          >
            <span
              style={{
                width: 24,
                height: 24,
                borderRadius: "50%",
                border: "2px solid #fff",
                display: "inline-block",
                marginRight: 12,
                background: "transparent",
              }}
            />
            <span style={{ flex: 1, fontSize: 20 }}>{item}</span>
            {/*<button
              onClick={() => onDelete(idx)}
              style={{
                background: "transparent",
                border: "none",
                color: "#fff",
                fontSize: 20,
                marginLeft: 8,
                cursor: "pointer",
              }}
              aria-label={`Delete ${item}`}
            >
              &times;
            </button>*/}
          </li>
        ))}
      </ul>
      <div style={{ textAlign: "right", marginTop: 16, fontSize: 18 }}>
        Total: {items.length}
      </div>
    </div>
  );
}
