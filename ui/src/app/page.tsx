"use client";

import Image from "next/image";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { v4 as uuidv4 } from "uuid";
import "@copilotkit/react-ui/styles.css";
import { Main } from "next/document";
import { ShoppingListCard } from "./components/ShoppingListCard";
import { MealPlanCard, MealPlanProps } from "./components/MealPlanCard";
import ReceiptCard from "./components/ReceiptCard";
import "./copilotchat-custom.css";
import React from "react";
import type { AgentState } from "./lib/types";

const AGENT_NAME = "mighty_assistant";

function MainContent() {
  const { state } = useCoAgent<AgentState>({
    name: AGENT_NAME,
    initialState: {
      last_receipt: "",
      last_meal_plan: "",
      last_shopping_list: "",
    },
  });

  // visibility checks
  const hasMealPlan =
    state.last_meal_plan &&
    Array.isArray(state.last_meal_plan) &&
    state.last_meal_plan.length > 0;

  const hasShoppingList =
    state.last_shopping_list &&
    Array.isArray(state.last_shopping_list.shopping_list) &&
    state.last_shopping_list.shopping_list.length > 0;

  const hasReceipt =
    state.last_receipt &&
    state.last_receipt.items &&
    Array.isArray(state.last_receipt.items) &&
    state.last_receipt.items.length > 0;

  // Render actions for the agent
  useCopilotAction({
    name: "*",
    available: "disabled", // Don't allow the agent or UI to call this tool as its only for rendering
    render: ({ name, args, status, result, handler, respond }) => {
      // show a progress message while status="executing", render the result when status="complete"
      console.log(
        "Rendering action: name=",
        name,
        "args=",
        args,
        "status=",
        status
      );
      if (status === "executing") {
        if (name.includes("price_lookup")) {
          return (
            <ToolProcessingIndicator message="Processing price lookup..." />
          );
        } else {
          return <ToolProcessingIndicator />;
        }
      }

      if (status === "complete") {
        console.log("result", result);
      }
    },
  });

  return (
    <div>
      {hasMealPlan && (
        <MealPlanCard meals={state.last_meal_plan} height={400} />
      )}
      {hasShoppingList && (
        <ShoppingListCard
          shopping_list={state.last_shopping_list.shopping_list}
          height={400}
        />
      )}
      {hasReceipt && <ReceiptCard receipt={state.last_receipt} height={400} />}
    </div>
  );
}

type ToolProcessingIndicatorProps = {
  message?: string;
};

const ToolProcessingIndicator: React.FC<ToolProcessingIndicatorProps> = ({
  message = "Processing, please wait...",
}) => {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        fontSize: "0.85em", // smaller font
        color: "#666",
        margin: "8px 0",
      }}
    >
      <span
        style={{
          width: 16,
          height: 16,
          marginRight: 8,
          border: "2px solid #ccc",
          borderTop: "2px solid #333",
          borderRadius: "50%",
          display: "inline-block",
          animation: "spin 1s linear infinite",
        }}
      />
      <span>{message}</span>
      <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default function Home() {
  // generate a new unique threadId for each user
  const threadId = uuidv4();

  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent={AGENT_NAME}
      threadId={threadId}
    >
      <div style={{ display: "flex", height: "100vh", width: "100vw" }}>
        <div
          style={{ flex: 6, overflowY: "auto", padding: 24, height: "100%" }}
        >
          <MainContent />
        </div>
        <div
          style={{
            flex: 4,
            height: "100%",
            minWidth: 320,
            display: "flex",
            flexDirection: "column",
            overflowY: "auto",
            background: "#181a1b", // Match chat window background
            boxShadow: "-4px 0 12px -4px rgba(0,0,0,0.15)", // Subtle shadow to the left
          }}
        >
          {/* threadId here should change depending on the user */}
          <div style={{ marginTop: "auto" }}>
            <CopilotChat
              instructions={
                "You are assisting the user as best as you can. Answer in the best way possible given the data you have."
              }
              labels={{
                title: "Your Assistant",
                initial: "Hi! 👋 How can I assist you today?",
              }}
            />
          </div>
        </div>
      </div>
    </CopilotKit>
  );
}
