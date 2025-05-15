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
import { YearlySpendChart } from "./components/charts/YearlySpendChart";
import { MonthlySpendChart } from "./components/charts/MonthlySpendChart";
import { DailySpendChart } from "./components/charts/DailySpendChart";
import { useState } from "react";

function MainContent() {
  const { getAgentState } = useAgentState();

  const state = getAgentState();

  const mealPlan = Array.isArray(state.last_meal_plan) ? state.last_meal_plan : [];
  const shoppingList =
    state.last_shopping_list && typeof state.last_shopping_list === "object" &&
    Array.isArray((state.last_shopping_list as any).shopping_list)
      ? (state.last_shopping_list as any).shopping_list
      : [];
  const receipt = state.last_receipt && typeof state.last_receipt === "object" ? state.last_receipt : null;

  const hasMealPlan = mealPlan.length > 0;
  const hasShoppingList = shoppingList.length > 0;
  const hasReceipt = receipt && Array.isArray(receipt.items) && receipt.items.length > 0;

  // Render actions for the agent
  useCopilotAction({
    name: "s_kaupat_price_lookup",
    available: "disabled",
    render: ({ status, args, result }) => {
      if (status === "executing") {
        return <ToolProcessingIndicator message="Processing price lookup..." /> as React.ReactElement;
      }
      if (status === "complete") {
        // name is not available, so remove it from the log
        console.log("Action complete: result=", result);
        return <PriceLookupCard args={args} items={result} /> as React.ReactElement;
      }
      // Always return a valid ReactElement (empty fragment) instead of null
      return <></>;
    },
  });

  // Lift year/month state up to here
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);

  return (
    <div>
      <div style={{ display: "flex", gap: 24, marginBottom: 24 }}>
        <div style={{ flex: 1 }}>
          <YearlySpendChart />
        </div>
        <div style={{ flex: 1 }}>
          <MonthlySpendChart
            year={year}
            month={month}
            setYear={setYear}
            setMonth={setMonth}
          />
        </div>
      </div>
      <DailySpendChart year={year} month={month} />
      {hasMealPlan && (
        <MealPlanCard meals={mealPlan} height={400} />
      )}
      {hasShoppingList && (
        <ShoppingListCard
          shopping_list={shoppingList}
          height={400}
        />
      )}
      {hasReceipt && receipt && <ReceiptCard receipt={receipt} height={400} />}
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
