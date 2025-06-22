import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Collapse from "@mui/material/Collapse";
import IconButton from "@mui/material/IconButton";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import RecipeCard, { Recipe } from "./chat/RecipeCard";

interface RecipeListProps {
  recipes: Recipe[];
}

export default function RecipeList({ recipes }: RecipeListProps) {
  const [openIdx, setOpenIdx] = React.useState<number | null>(null);
  const handleToggle = (idx: number) => {
    setOpenIdx(openIdx === idx ? null : idx);
  };

  if (!recipes || recipes.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ mb: 2 }}>
        No recipes found.
      </Typography>
    );
  }

  return (
    <Box>
      {recipes.map((recipe, idx) => (
        <Box key={idx} sx={{ position: "relative", mb: 2 }}>
          {/* Header row with expand/collapse */}
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
              {recipe.name}
            </Typography>
          </Box>
          <Collapse in={openIdx === idx} timeout="auto" unmountOnExit>
            <Box sx={{ mt: 1 }}>
              <RecipeCard recipe={recipe} height={540} />
            </Box>
          </Collapse>
        </Box>
      ))}
    </Box>
  );
}
