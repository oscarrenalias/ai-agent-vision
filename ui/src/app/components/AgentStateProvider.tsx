"use client";

import React, { createContext, useContext } from "react";
import { useCoAgent, useLangGraphInterrupt } from "@copilotkit/react-core";
import { AGENT_NAME, AgentState } from "../lib/types";
import AgentStateInspector from "./debug/AgentStateInspector";
import UploadCard from "./chat/UploadCard";

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

  useLangGraphInterrupt({
    render: ({ event, resolve }) => (
      <UploadCard event={event} resolve={resolve} />
    ),
  });

  const setAgentState = (newState: AgentState) => {
    setState((prevState) => {
      const merged = { ...prevState, ...newState };
      return merged;
    });
  };

  const getAgentState = () => {
    return state;
  };

  return (
    <AgentStateContext.Provider value={{ setAgentState, getAgentState }}>
      <AgentStateInspector state={state} />
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
