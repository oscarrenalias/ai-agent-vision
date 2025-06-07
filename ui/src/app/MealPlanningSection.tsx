import React from "react";
import { MealPlanCard } from "./components/MealPlanCard";

export default function MealPlanningSection() {
  // Placeholder for meal planning UI
  return (
    <div style={{ padding: 24 }}>
      <h2>Meal Planning</h2>
      <MealPlanCard meals={[]} height={400} />
    </div>
  );
}
