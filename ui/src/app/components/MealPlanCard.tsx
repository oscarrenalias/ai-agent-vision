import React from "react";

export type MealPlanItem = Record<string, any>;

export type MealPlanProps = {
  meals: MealPlanItem[];
  height?: string | number;
};

const MealPlanCard: React.FC<MealPlanProps> = ({ meals, height = 400 }) => {
  const mealArray = Array.isArray(meals) ? meals : Object.values(meals || {});
  if (!mealArray || mealArray.length === 0) return null;

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
        margin: "0 auto 24px auto",
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: 16 }}>🍽️ Meal Plan</h2>
      {mealArray.length === 0 ? (
        <div style={{ color: "#888" }}>No meals planned.</div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {mealArray.map((meal, idx) => (
            <li
              key={idx}
              style={{
                borderBottom:
                  idx !== mealArray.length - 1 ? "1px solid #eee" : undefined,
                paddingBottom: 12,
                marginBottom: 12,
              }}
            >
              {Object.entries(meal).map(([key, value]) => (
                <div key={key}>
                  <strong>{key}:</strong>{" "}
                  {Array.isArray(value)
                    ? value.length > 0
                      ? value.map((item, index) => (
                          <span key={index}>
                            {item}
                            {index < value.length - 1 ? ", " : ""}
                          </span>
                        ))
                      : "No items"
                    : String(value)}
                </div>
              ))}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default MealPlanCard;
