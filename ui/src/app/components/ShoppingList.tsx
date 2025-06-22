import React, { useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import Box from "@mui/material/Box";

interface ShoppingListProps {
  items: string[];
  onAdd: (item: string) => void;
  onDelete: (index: number) => void;
}

export default function ShoppingList({
  items,
  onAdd,
  onDelete,
}: ShoppingListProps) {
  const [input, setInput] = useState("");

  const handleAdd = () => {
    if (input.trim()) {
      onAdd(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleAdd();
    }
  };

  return (
    <Card
      sx={{
        maxWidth: "70%",
        width: "100%",
        borderRadius: 3,
        boxShadow: 2,
        bgcolor: "background.paper",
      }}
    >
      <CardContent>
        {/*<Typography variant="h6" sx={{ mb: 2 }}>
          Shopping List
        </Typography>*/}
        <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Add an item..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            variant="outlined"
            sx={{ mr: 1 }}
          />
          <IconButton
            color="primary"
            onClick={handleAdd}
            aria-label="Add item"
            sx={{
              bgcolor: "primary.main",
              color: "#fff",
              "&:hover": { bgcolor: "primary.dark" },
            }}
          >
            <AddIcon />
          </IconButton>
        </Box>
        <List dense>
          {items.map((item, idx) => (
            <ListItem
              key={idx}
              secondaryAction={
                <IconButton
                  edge="end"
                  aria-label={`Delete ${item}`}
                  onClick={() => onDelete(idx)}
                >
                  <DeleteIcon />
                </IconButton>
              }
            >
              <ListItemIcon sx={{ minWidth: 0, mr: 1 }}>
                <span
                  style={{
                    width: 20,
                    height: 20,
                    borderRadius: "50%",
                    border: "2px solid #1976d2",
                    display: "inline-block",
                    background: "transparent",
                  }}
                />
              </ListItemIcon>
              <ListItemText
                primary={item}
                primaryTypographyProps={{ fontSize: 18 }}
              />
            </ListItem>
          ))}
        </List>
        <Box sx={{ textAlign: "right", mt: 2 }}>
          <Typography variant="subtitle1" color="text.secondary">
            Total: {items.length}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
