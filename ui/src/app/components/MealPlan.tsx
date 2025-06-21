import React from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import DeleteIcon from "@mui/icons-material/Delete";
import Box from "@mui/material/Box";
import Collapse from "@mui/material/Collapse";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import RecipeCard, { Recipe } from "./chat/RecipeCard";

export interface Meal {
  day: string;
  type: string;
  name: string;
  steps: string[];
  ingredients: string[];
}

export interface MealPlanData {
  name: string;
  meals: Meal[];
}

interface MealPlanProps {
  mealPlan: MealPlanData;
  onDeleteMeal: (index: number) => void;
}

export default function MealPlan({ mealPlan, onDeleteMeal }: MealPlanProps) {
  const [openIdx, setOpenIdx] = React.useState<number | null>(null);
  const handleToggle = (idx: number) => {
    setOpenIdx(openIdx === idx ? null : idx);
  };
  // Render each meal as a RecipeCard, passing meal data in RecipeCard's format
  return (
    <Box>
      <Typography
        variant="h5"
        sx={{
          mb: 2,
          fontWeight: 700,
          color: "primary.main",
          letterSpacing: 0.5,
        }}
      >
        {mealPlan.name}
      </Typography>
      {mealPlan.meals.length === 0 && (
        <Typography color="text.secondary" sx={{ mb: 2 }}>
          No meals in this plan.
        </Typography>
      )}
      {mealPlan.meals.map((meal, idx) => (
        <Box key={idx} sx={{ position: "relative", mb: 2 }}>
          {/* Header row with expand/collapse and delete */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              bgcolor: (theme) =>
                openIdx === idx
                  ? theme.palette.action.selected
                  : theme.palette.background.paper,
              borderRadius: 2,
              boxShadow: 1,
              px: 2,
              py: 1.5,
              cursor: "pointer",
              transition: "background 0.2s",
              "&:hover": {
                bgcolor: (theme) => theme.palette.action.hover,
              },
            }}
            onClick={() => handleToggle(idx)}
          >
            <IconButton
              edge="start"
              size="small"
              sx={{
                mr: 1,
                transform: openIdx === idx ? "rotate(180deg)" : "rotate(0deg)",
                transition: "transform 0.2s",
                color: (theme) => theme.palette.text.primary,
              }}
              onClick={(e) => {
                e.stopPropagation();
                handleToggle(idx);
              }}
              aria-label={openIdx === idx ? "Collapse" : "Expand"}
            >
              <ExpandMoreIcon />
            </IconButton>
            <Typography
              component="span"
              sx={{
                fontSize: 18,
                fontWeight: 500,
                color: (theme) => theme.palette.text.primary,
                flex: 1,
              }}
            >
              {meal.day}
              {meal.type ? ` (${meal.type})` : ""}{" "}
              <span style={{ color: "#1976d2", fontWeight: 600 }}>
                {meal.name}
              </span>
            </Typography>
            <IconButton
              edge="end"
              aria-label={`Delete meal for ${meal.day}${
                meal.type ? ` (${meal.type})` : ""
              }`}
              onClick={(e) => {
                e.stopPropagation();
                onDeleteMeal(idx);
              }}
              sx={{
                color: "error.main",
                bgcolor: (theme) =>
                  theme.palette.mode === "dark" ? "#2a2a2a" : "#fff",
                boxShadow: 1,
                zIndex: 2,
                "&:hover": {
                  bgcolor: (theme) =>
                    theme.palette.mode === "dark" ? "#442222" : "#fdecea",
                },
              }}
            >
              <DeleteIcon />
            </IconButton>
          </Box>
          <Collapse in={openIdx === idx} timeout="auto" unmountOnExit>
            <Box sx={{ mt: 1 }}>
              <RecipeCard
                recipe={{
                  name: meal.name,
                  description: null,
                  ingredients: meal.ingredients,
                  steps: meal.steps,
                  yields: null,
                  url: null,
                  cooking_time: null,
                  preparation_time: null,
                  tags: [meal.day, meal.type ?? ""],
                }}
                height={320}
              />
            </Box>
          </Collapse>
        </Box>
      ))}
    </Box>
  );
}
