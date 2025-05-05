import React, { createContext, useContext, useState, useEffect } from "react";
import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { AGENT_NAME, AgentState } from "../lib/types";

type AgentStateContextType = {
  setAgentState: (newState: AgentState) => void;
  getAgentState: () => AgentState;
};

const AgentStateContext = createContext<AgentStateContextType | undefined>(
  undefined
);

export const AgentStateProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const { state, setState } = useCoAgent<AgentState>({
    name: AGENT_NAME,
    initialState: {
      last_receipt: "",
      last_meal_plan: "",
      last_shopping_list: "",
      receipt_image_path: "",
    },
  });

  useEffect(() => {
    console.log("AgentStateProvider status changed:", state);
  }, [state]);

  const setAgentState = (newState: AgentState) => {
    setState((prevState) => {
      console.log("Previous state:", prevState);
      console.log("New state to merge:", newState);
      const merged = { ...prevState, ...newState };
      console.log("Merged state:", merged);
      return merged;
    });
  };

  const getAgentState = () => {
    return state;
  };

  return (
    <AgentStateContext.Provider value={{ setAgentState, getAgentState }}>
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          zIndex: 1000,
          padding: "1rem",
          borderBottomRightRadius: "8px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          maxHeight: "40vh",
          overflowY: "auto",
          maxWidth: "350px",
        }}
      >
        <h3>Agent State:</h3>
        <pre>{JSON.stringify(state, null, 2)}</pre>
      </div>
      {children}
    </AgentStateContext.Provider>
  );
};

export function useAgentState() {
  const ctx = useContext(AgentStateContext);
  if (!ctx)
    throw new Error("useAgentState must be used within AgentStateProvider");
  return ctx;
}
