"use client";

import Image from "next/image";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCoAgent } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";
import { Main } from "next/document";
import ShoppingListCard from "./components/ShoppingListCard";
import MealPlanCard from "./components/MealPlanCard";
import "./copilotchat-custom.css";

const AGENT_NAME = "mighty_assistant";

// Define the AgentState type
type MealListProps = {
  meals: Record<string, any>[];
};

type ShoppingListItem = {
  description: string;
  matched_product_name: string;
  price: number;
  quantity_needed: number;
  unit_of_measurement: string;
};
type ShoppingListProps = {
  shopping_list: ShoppingListItem[];
};

type AgentState = {
  last_receipt: {} | null;
  last_meal_plan: MealListProps | null;
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
    </div>
  );
}

export default function Home() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent={AGENT_NAME} threadId="123">
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
