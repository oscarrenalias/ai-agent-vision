import React from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Chip from "@mui/material/Chip";

// Define the Recipe type
export type Recipe = {
  id: string;
  name: string;
  description: string | null;
  ingredients: string[];
  steps: string[];
  yields: number | null;
  url: string | null;
  cooking_time: number | null;
  preparation_time: number | null;
  tags: string[];
};

interface RecipeCardProps {
  recipe: Recipe;
  height?: string | number;
}

const RecipeCard: React.FC<RecipeCardProps> = ({ recipe, height = 400 }) => {
  if (!recipe) return null;

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
          🍽️ {recipe.name}
        </Typography>

        {recipe.description && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {recipe.description}
          </Typography>
        )}

        {/* Tags */}
        {recipe.tags && recipe.tags.length > 0 && (
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mb: 2 }}>
            {recipe.tags.map((tag, index) => (
              <Chip
                key={index}
                label={tag}
                size="small"
                sx={{ fontSize: 12 }}
              />
            ))}
          </Box>
        )}

        {/* Recipe meta information */}
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, mb: 2 }}>
          {recipe.preparation_time && (
            <Typography variant="body2" sx={{ fontSize: 14 }}>
              👨‍🍳 Prep: {recipe.preparation_time} min
            </Typography>
          )}

          {recipe.cooking_time && (
            <Typography variant="body2" sx={{ fontSize: 14 }}>
              ⏱️ Cook: {recipe.cooking_time} min
            </Typography>
          )}

          {recipe.yields && (
            <Typography variant="body2" sx={{ fontSize: 14 }}>
              👥 Serves: {recipe.yields}
            </Typography>
          )}

          {recipe.url && (
            <Typography variant="body2" sx={{ fontSize: 14 }}>
              <a
                href={recipe.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#1976d2", textDecoration: "none" }}
              >
                🔗 Source
              </a>
            </Typography>
          )}
        </Box>

        <Divider sx={{ my: 1 }} />

        <Box
          sx={{
            overflowY: "auto",
            maxHeight: typeof height === "number" ? height - 180 : undefined, // Adjust for header content
          }}
        >
          {/* Ingredients Section */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
              🥕 Ingredients
            </Typography>
            <ul style={{ paddingLeft: 20, margin: 0 }}>
              {recipe.ingredients.map((ingredient, index) => (
                <li key={index} style={{ fontSize: 14, marginBottom: 4 }}>
                  {ingredient}
                </li>
              ))}
            </ul>
          </Box>

          {/* Instructions Section */}
          <Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
              📝 Instructions
            </Typography>
            <ol
              style={{
                paddingLeft: 20,
                margin: 0,
                listStyle: "decimal", // Explicitly set list style to decimal numbers
                listStylePosition: "outside", // Position numbers outside the content
              }}
            >
              {recipe.steps.map((step, index) => (
                <li
                  key={index}
                  style={{
                    fontSize: 14,
                    marginBottom: 8,
                    paddingLeft: 4,
                    display: "list-item", // Force list item display
                  }}
                >
                  {step}
                </li>
              ))}
            </ol>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default RecipeCard;
