import React from "react";
import { useAgentState } from "./components/AgentStateProvider";
import MealPlan, { MealPlanData } from "./components/MealPlan";

export default function MealPlanningSection() {
  const { getAgentState, setAgentState } = useAgentState();
  const state = getAgentState();
  const mealPlan: MealPlanData | null = state.meal_plan || null;

  const handleDeleteMeal = (idx: number) => {
    if (!mealPlan) return;
    const newMeals = mealPlan.meals.filter((_, i) => i !== idx);
    setAgentState({
      ...state,
      meal_plan: { ...mealPlan, meals: newMeals },
    });
  };

  if (!mealPlan) {
    return <div style={{ padding: 24 }}>No meal plan available.</div>;
  }

  return (
    <div style={{ padding: 24 }}>
      <MealPlan mealPlan={mealPlan} onDeleteMeal={handleDeleteMeal} />
    </div>
  );
}
