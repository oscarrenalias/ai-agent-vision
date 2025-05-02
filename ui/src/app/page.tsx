"use client";

import Image from "next/image";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCoAgent } from "@copilotkit/react-core";
import { v4 as uuidv4 } from "uuid";
import "@copilotkit/react-ui/styles.css";
import { Main } from "next/document";
import {
  ShoppingListCard,
  ShoppingListItem,
  ShoppingListProps,
} from "./components/ShoppingListCard";
import { MealPlanCard, MealPlanProps } from "./components/MealPlanCard";
import ReceiptCard from "./components/ReceiptCard";
import "./copilotchat-custom.css";

const AGENT_NAME = "mighty_assistant";

// Define the AgentState type

type AgentState = {
  last_receipt: {} | null;
  last_meal_plan: MealPlanProps | null;
  last_shopping_list: {} | null;
};

function MainContent() {
  const { state } = useCoAgent<AgentState>({
    name: AGENT_NAME,
    initialState: {
      last_receipt: "",
      last_meal_plan: "",
      last_shopping_list: "",
    },
  });

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
        <div style={{ flex: 6, overflowY: "auto", padding: 24 }}>
          <MainContent />
          <div style={{ height: 1200 }} />
        </div>
        <div
          style={{
            flex: 4,
            borderLeft: "1px solid #eee",
            height: "100vh",
            minWidth: 320,
            display: "flex",
            flexDirection: "column",
            overflowY: "auto",
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
