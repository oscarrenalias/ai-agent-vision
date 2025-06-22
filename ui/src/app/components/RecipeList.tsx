import React, { useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Collapse from "@mui/material/Collapse";
import IconButton from "@mui/material/IconButton";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import DeleteIcon from "@mui/icons-material/Delete";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import RecipeCard, { Recipe } from "./chat/RecipeCard";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";

interface RecipeListProps {
  recipes: Recipe[];
  onDeleteRecipe?: (idx: number) => void; // Optional callback for parent
}

export default function RecipeList({
  recipes,
  onDeleteRecipe,
}: RecipeListProps) {
  const [openIdx, setOpenIdx] = useState<number | null>(null);
  const [deleteIdx, setDeleteIdx] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [localRecipes, setLocalRecipes] = useState(recipes);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: "success" | "error";
  }>({ open: false, message: "", severity: "success" });

  const handleToggle = (idx: number) => {
    setOpenIdx(openIdx === idx ? null : idx);
  };

  const handleSnackbarClose = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason === "clickaway") return;
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const handleDelete = async () => {
    if (deleteIdx === null) return;
    setDeleting(true);
    setError(null);
    const recipe = localRecipes[deleteIdx];
    try {
      const res = await fetch(`/api/recipes/${recipe.id}`, {
        method: "DELETE",
      });
      const data: { message?: string } = await res.json();
      if (!res.ok) {
        throw new Error(data?.message || "Failed to delete recipe");
      }
      const updated = localRecipes.filter((_, i) => i !== deleteIdx);
      setLocalRecipes(updated);
      setDeleteIdx(null);
      setOpenIdx(null);
      setSnackbar({
        open: true,
        message: "Recipe deleted successfully!",
        severity: "success",
      });
      if (onDeleteRecipe) onDeleteRecipe(deleteIdx);
    } catch (e: any) {
      setError(e.message || "Unknown error");
      setSnackbar({
        open: true,
        message: e.message || "Failed to delete recipe.",
        severity: "error",
      });
    } finally {
      setDeleting(false);
    }
  };

  if (!localRecipes || localRecipes.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ mb: 2 }}>
        No recipes found.
      </Typography>
    );
  }

  return (
    <Box>
      {localRecipes.map((recipe, idx) => (
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
              {recipe.name}
            </Typography>
            <IconButton
              edge="end"
              aria-label={`Delete recipe ${recipe.name}`}
              onClick={(e) => {
                e.stopPropagation();
                setDeleteIdx(idx);
              }}
              sx={{
                color: "error.main",
                bgcolor: (theme) =>
                  theme.palette.mode === "dark" ? "#2a2a2a" : "#fff",
                boxShadow: 1,
                zIndex: 2,
                ml: 1,
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
              <RecipeCard recipe={recipe} height={540} />
            </Box>
          </Collapse>
        </Box>
      ))}
      {/* Delete confirmation dialog */}
      <Dialog open={deleteIdx !== null} onClose={() => setDeleteIdx(null)}>
        <DialogTitle>Delete Recipe</DialogTitle>
        <DialogContent>
          Are you sure you want to delete the recipe "
          {deleteIdx !== null ? localRecipes[deleteIdx].name : ""}"?
          {error && (
            <Typography color="error" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteIdx(null)} disabled={deleting}>
            Cancel
          </Button>
          <Button
            onClick={handleDelete}
            color="error"
            disabled={deleting}
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
      <Snackbar
        open={snackbar.open}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: "100%", color: "#fff" }} // Force white text
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
