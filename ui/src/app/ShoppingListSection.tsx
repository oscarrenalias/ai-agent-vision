import React from "react";
import { useAgentState } from "./components/AgentStateProvider";
import ShoppingList from "./components/ShoppingList";
import Typography from "@mui/material/Typography";

export default function ShoppingListSection() {
  const { getAgentState, setAgentState } = useAgentState();
  const state = getAgentState();
  const shoppingList: string[] = Array.isArray(state.shopping_list)
    ? state.shopping_list
    : [];

  const handleAdd = (item: string) => {
    const newList = [...shoppingList, item];
    setAgentState({
      ...state,
      shopping_list: newList,
    });
  };

  const handleDelete = (idx: number) => {
    const newList = shoppingList.filter((_, i: number) => i !== idx);
    setAgentState({
      ...state,
      shopping_list: newList,
    });
  };

  return (
    <div>
      <Typography
        variant="h5"
        component="h2"
        sx={{ mt: 2, mb: 1, fontWeight: 600 }}
      >
        Shopping List
      </Typography>
      <ShoppingList
        items={shoppingList}
        onAdd={handleAdd}
        onDelete={handleDelete}
      />
    </div>
  );
}
