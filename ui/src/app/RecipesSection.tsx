import React, { useEffect } from "react";
import RecipeList from "./components/RecipeList";
import { Recipe } from "./components/chat/RecipeCard";
import Typography from "@mui/material/Typography";

export default function RecipesSection() {
  const [recipes, setRecipes] = React.useState<Recipe[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    setLoading(true);
    fetch("/api/recipes")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch recipes");
        return res.json();
      })
      .then((data) => {
        setRecipes(data.recipes || []);
        setError(null);
      })
      .catch((err) => {
        setError(err.message || "Unknown error");
        setRecipes([]);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div style={{ padding: 24 }}>Loading recipes...</div>;
  }
  if (error) {
    return <div style={{ color: "red", padding: 24 }}>Error: {error}</div>;
  }

  return (
    <div>
      <Typography
        variant="h5"
        component="h2"
        sx={{ mt: 2, mb: 1, fontWeight: 600 }}
      >
        Recipes
      </Typography>
      <RecipeList recipes={recipes} />
    </div>
  );
}
