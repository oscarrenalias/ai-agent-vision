"use client";

import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { useAgentState } from "./components/AgentStateProvider";
import Sidebar from "./Sidebar";
import ShoppingListSection from "./ShoppingListSection";
import MealPlanningSection from "./MealPlanningSection";
import AnalyticsSection from "./AnalyticsSection";
import { useCopilotAction } from "@copilotkit/react-core";
import ReceiptCard from "./components/chat/ReceiptCard";
import RecipeCard from "./components/chat/RecipeCard";
import PriceLookupCard from "./components/chat/PriceLookupCard";
import { ToolProcessingIndicator } from "./components/ToolProcessingIndicator";
import React, { useState } from "react";

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeSection, setActiveSection] = useState("analytics");

  // State for analytics section
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);

  // Get agent state for meal plan and shopping list
  const { getAgentState } = useAgentState();
  const state = getAgentState();
  const mealPlan = Array.isArray(state.last_meal_plan)
    ? state.last_meal_plan
    : [];
  const shoppingList =
    state.last_shopping_list &&
    typeof state.last_shopping_list === "object" &&
    Array.isArray((state.last_shopping_list as any).shopping_list)
      ? (state.last_shopping_list as any).shopping_list
      : [];

  // Copilot actions for chat and tool feedback (needed for chat panel)
  useCopilotAction({
    name: "s_kaupat_price_lookup",
    available: "disabled",
    render: ({ status, args, result }) => {
      if (status === "executing") {
        return (
          <ToolProcessingIndicator message="Processing price lookup..." />
        ) as React.ReactElement;
      }
      if (status === "complete") {
        return (
          <PriceLookupCard args={args} items={result} />
        ) as React.ReactElement;
      }
      return <></>;
    },
  });
  useCopilotAction({
    name: "receipt_analyzer_tool",
    available: "disabled",
    render: ({ status, args, result }) => {
      if (status === "executing") {
        return (
          <ToolProcessingIndicator message="Processing receipt..." />
        ) as React.ReactElement;
      }
      if (status === "complete") {
        return (<ReceiptCard receipt={result} />) as React.ReactElement;
      }
      return <></>;
    },
  });
  useCopilotAction({
    name: "persist_receipt_tool",
    available: "disabled",
    render: ({ status, args, result }) => {
      if (status === "executing") {
        return (
          <ToolProcessingIndicator message="Saving receipt..." />
        ) as React.ReactElement;
      }
      return <></>;
    },
  });
  useCopilotAction({
    name: "get_receipts_by_date",
    available: "disabled",
    render: ({ status, args, result }) => {
      if (status === "executing") {
        return (
          <ToolProcessingIndicator message="Getting receipt data..." />
        ) as React.ReactElement;
      }
      return <></>;
    },
  });
  useCopilotAction({
    name: "get_items_per_item_type",
    available: "disabled",
    render: ({ status, args, result }) => {
      if (status === "executing") {
        return (
          <ToolProcessingIndicator message="Getting receipt data..." />
        ) as React.ReactElement;
      }
      return <></>;
    },
  });
  useCopilotAction({
    name: "page_retriever",
    available: "disabled",
    render: ({ status, args, result }) => {
      if (status === "executing") {
        return (
          <ToolProcessingIndicator message="Retrieving recipe" />
        ) as React.ReactElement;
      }
      return <></>;
    },
  });
  useCopilotAction({
    name: "recipe_parser",
    available: "disabled",
    render: ({ status, args, result }) => {
      if (status === "executing") {
        return (
          <ToolProcessingIndicator message="Processing recipe" />
        ) as React.ReactElement;
      }
      if (status === "complete") {
        return <RecipeCard recipe={result} height={550} />;
      }
      return <></>;
    },
  });
  useCopilotAction({
    name: "save_recipe_tool",
    available: "disabled",
    render: ({ status, args, result }) => {
      if (status === "executing") {
        return (
          <ToolProcessingIndicator message="Saving recipe" />
        ) as React.ReactElement;
      }
      return <></>;
    },
  });

  let MainSection: React.ReactNode = null;
  if (activeSection === "shopping") {
    MainSection = <ShoppingListSection />;
  } else if (activeSection === "meal") {
    MainSection = <MealPlanningSection />;
  } else {
    MainSection = (
      <AnalyticsSection
        year={year}
        month={month}
        setYear={setYear}
        setMonth={setMonth}
        mealPlan={mealPlan}
        shoppingList={shoppingList}
      />
    );
  }

  return (
    <div style={{ display: "flex", height: "100vh", width: "100vw" }}>
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen((o) => !o)}
        activeSection={activeSection}
        setActiveSection={setActiveSection}
      />
      <div style={{ flex: 6, overflowY: "auto", padding: 24, height: "100%" }}>
        {MainSection}
      </div>
      <div
        style={{
          flex: 4,
          height: "100%",
          minWidth: 320,
          display: "flex",
          flexDirection: "column",
          overflowY: "auto",
          background: "#181a1b",
          boxShadow: "-4px 0 12px -4px rgba(0,0,0,0.15)",
        }}
      >
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
  );
}
