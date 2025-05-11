"use client";

import { CopilotKit, useLangGraphInterrupt } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCopilotAction } from "@copilotkit/react-core";
import { v4 as uuidv4 } from "uuid";
import "@copilotkit/react-ui/styles.css";
import { ShoppingListCard } from "./components/ShoppingListCard";
import { MealPlanCard } from "./components/MealPlanCard";
import ReceiptCard from "./components/ReceiptCard";
import "./copilotchat-custom.css";
import { ToolProcessingIndicator } from "./components/ToolProcessingIndicator";
import PriceLookupCard from "./components/chat/PriceLookupCard";
import {
  AgentStateProvider,
  useAgentState,
} from "./components/AgentStateProvider";
import { AgentState, AGENT_NAME } from "./lib/types";
import { useCoAgentStateRender } from "@copilotkit/react-core";
import { YearlySpendBarChart } from "./components/YearlySpendBarChart";

function MainContent() {
  const { getAgentState } = useAgentState();

  const state = getAgentState();

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
    name: "s_kaupat_price_lookup",
    available: "disabled",
    render: ({ name, args, status, result, handler, respond }) => {
      if (status === "executing") {
        return <ToolProcessingIndicator message="Processing price lookup..." />;
      }

      if (status === "complete") {
        console.log("Action complete: name=", name, "result=", result);
        return <PriceLookupCard args={args} items={result} />;
      }
    },
  });

  return (
    <div>
      <YearlySpendBarChart />
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

export default function Home() {
  // generate a new unique threadId for each user
  const threadId = uuidv4();

  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent={AGENT_NAME}
      threadId={threadId}
    >
      <AgentStateProvider>
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
            <div style={{ marginTop: "auto", paddingBottom: 24 }}>
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
      </AgentStateProvider>
    </CopilotKit>
  );
}
