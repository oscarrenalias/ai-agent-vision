import React from "react";
import { useAgentState } from "./components/AgentStateProvider";
import MealPlan, { MealPlanData } from "./components/MealPlan";
import Typography from "@mui/material/Typography";

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

  return (
    <div>
      <Typography
        variant="h5"
        component="h2"
        sx={{ mt: 2, mb: 1, fontWeight: 600 }}
      >
        Meal Plan
      </Typography>
      {mealPlan ? (
        <MealPlan mealPlan={mealPlan} onDeleteMeal={handleDeleteMeal} />
      ) : (
        <div>No meal plan available.</div>
      )}
    </div>
  );
}
