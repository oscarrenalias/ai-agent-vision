import { Receipt } from "../../lib/types";
import React, { useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

// Emoji mapping for categories
const CATEGORY_EMOJI: Record<string, string> = {
  // Level 1
  Food: "🍎",
  Household: "🧹",
  Other: "📦",
  // Level 2
  Fruits: "🍏",
  Vegetables: "🥦",
  Meats: "🥩",
  "Fish & Seafood": "🐟",
  Dairy: "🧀",
  "Bread & Bakery": "🍞",
  "Grains & Pasta": "🍝",
  "Sauces & Condiments": "🥫",
  "Snacks & Sweets": "🍬",
  Beverages: "🥤",
  "Legumes & Pulses": "🌰",
  "Herbs & Spices": "🌿",
  "Prepared Foods": "🍲",
  "Other Food": "🍽️",
  "Cleaning Products": "🧴",
  "Paper Goods": "🧻",
  Laundry: "🧺",
  "Kitchen Supplies": "🍳",
  "Personal Hygiene": "🧼",
  Deposits: "♻️",
  "Unknown / Miscellaneous": "❓",
  // Level 3 (examples)
  Pork: "🐖",
  Beef: "🐄",
  Poultry: "🐔",
  Mixed: "🥩",
  Tuna: "🐟",
  Salmon: "🐟",
  Shrimp: "🦐",
  Milk: "🥛",
  Yoghurt: "🥣",
  Cheese: "🧀",
  Butter: "🧈",
  Flatbread: "🫓",
  "Sliced Bread": "🍞",
  "Sweet Bakery": "🧁",
  Juice: "🧃",
  Water: "💧",
  "Soft Drink": "🥤",
  Alcohol: "🍺",
  "Sports Drink": "🥤",
  Sauces: "🥫",
  Soups: "🥣",
  "Ready Meals": "🍱",
  "Toilet Cleaner": "🚽",
  "Surface Cleaner": "🧽",
  Dishwashing: "🍽️",
  "Bottle Deposit": "🍾",
  "Can Deposit": "🥫",
};

function CategoryEmoji({ item }: { item: any }) {
  const { level_1, level_2, level_3 } = item.item_category;
  // Pick the most specific non-null category
  const category = level_3 ?? level_2 ?? level_1;
  return <span title={category}>{CATEGORY_EMOJI[category] || "❓"}</span>;
}

interface ReceiptCardProps {
  receipt: Receipt;
  height?: string | number;
}

const ReceiptCard: React.FC<ReceiptCardProps> = ({ receipt, height = 400 }) => {
  if (!receipt || !receipt.items || receipt.items.length === 0) return null;

  return (
    <Card
      sx={{
        width: "100%",
        borderRadius: 3,
        boxShadow: 3,
        position: "relative",
        mb: 2,
        maxHeight: typeof height === "number" ? height : undefined,
        display: "flex",
        flexDirection: "column",
      }}
    >
      <CardContent
        sx={{
          pb: 1,
          pt: 2,
          px: 2,
          flex: 1,
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Typography
          variant="h6"
          gutterBottom
          sx={{ fontWeight: 600, mb: 1, fontSize: 18 }}
        >
          🛒 Receipt
        </Typography>
        <Box
          sx={{
            overflowY: "auto",
            maxHeight: typeof height === "number" ? height - 60 : undefined, // 60px for header and padding
          }}
        >
          <div style={{ fontSize: 15, marginBottom: 16 }}>
            <strong>Store:</strong> {receipt.receipt_data.place} <br />
            <strong>Date:</strong> {receipt.receipt_data.date} <br />
            <strong>Total:</strong> {receipt.receipt_data.total} € <br />
            <strong>Savings:</strong> {receipt.receipt_data.total_savings} €
          </div>
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {receipt.items.map((item, idx) => {
              const [flipped, setFlipped] = useState(false);
              return (
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
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      fontWeight: 600,
                    }}
                  >
                    <span
                      style={{ cursor: "pointer" }}
                      onClick={() => setFlipped((f) => !f)}
                      title={flipped ? item.name_fi : item.name_en}
                    >
                      <CategoryEmoji item={item} />{" "}
                      {flipped ? item.name_fi : item.name_en}
                    </span>
                    <span
                      style={{
                        fontWeight: 500,
                        fontSize: 15,
                        whiteSpace: "nowrap",
                        marginLeft: 16,
                      }}
                    >
                      {item.total_price} €
                    </span>
                  </div>
                  <div
                    style={{ fontSize: 14, color: "var(--card-muted, #666)" }}
                  >
                    Category:{" "}
                    {item.item_category.level_3 ??
                      item.item_category.level_2 ??
                      item.item_category.level_1}
                    <br />
                    Qty: {item.quantity} {item.unit_of_measure}
                    {item.unit_price !== null && (
                      <>
                        <br />
                        Unit price: {item.unit_price} €
                      </>
                    )}
                    {item.has_loyalty_discount &&
                      item.loyalty_discount !== null && (
                        <>
                          <br />
                          Loyalty discount: {item.loyalty_discount} €
                        </>
                      )}
                  </div>
                </li>
              );
            })}
          </ul>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ReceiptCard;
