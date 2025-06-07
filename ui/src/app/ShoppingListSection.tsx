import React from "react";
import { useCoAgentStateRender } from "@copilotkit/react-core";
import { useAgentState } from "./components/AgentStateProvider";
import ShoppingList from "./components/ShoppingList";

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
    <div style={{ padding: 24 }}>
      <ShoppingList
        items={shoppingList}
        onAdd={handleAdd}
        onDelete={handleDelete}
      />
    </div>
  );
}
