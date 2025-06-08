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
import AgentStateInspector from "./components/debug/AgentStateInspector";
import { useTheme } from "@mui/material";
import "./copilotchat-custom.css";

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false); // default to slid in
  const [activeSection, setActiveSection] = useState("analytics");

  // State for analytics section
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);

  // Get agent state for meal plan and shopping list
  const { getAgentState } = useAgentState();
  const state = getAgentState();

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
  useCopilotAction({
    name: "add_to_shopping_list",
    available: "disabled",
    render: ({ status, args, result }) => {
      if (status === "executing") {
        return (
          <ToolProcessingIndicator message="Adding to shopping list" />
        ) as React.ReactElement;
      }
      return <></>;
    },
  });
  useCopilotAction({
    name: "get_shopping_list",
    available: "disabled",
    render: ({ status, args, result }) => {
      if (status === "executing") {
        return (
          <ToolProcessingIndicator message="Getting shopping list" />
        ) as React.ReactElement;
      }
      return <></>;
    },
  });

  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";

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
      />
    );
  }

  return (
    <div style={{ display: "flex", height: "100vh", width: "100vw" }}>
      <AgentStateInspector state={state} />
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen((o) => !o)}
        activeSection={activeSection}
        setActiveSection={setActiveSection}
      />
      <div
        style={{
          flex: 6,
          overflowY: "auto",
          padding: "24px 24px 24px 72px",
          height: "100%",
        }}
      >
        {MainSection}
      </div>
      <div
        style={
          {
            flex: 4,
            height: "calc(100vh - 32px)",
            minWidth: 320,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            background: isDarkMode ? theme.palette.background.paper : "#fff",
            borderRadius: 20,
            margin: 16,
            boxShadow: "none",
            border: `1px solid ${
              isDarkMode ? theme.palette.divider : "#e0e3eb"
            }`,
            // CopilotChat theme variables
            "--copilot-kit-background-color": isDarkMode
              ? theme.palette.background.paper
              : "#fff",
            "--copilot-kit-contrast-color": isDarkMode
              ? theme.palette.text.primary
              : "#23272f",
            "--copilot-kit-input-background-color": isDarkMode
              ? "#23272f"
              : "#f5f5f5",
            "--copilot-kit-secondary-color": isDarkMode ? "#23272f" : "#fafafa",
            "--copilot-kit-secondary-contrast-color": isDarkMode
              ? "#e0e0e0"
              : "#333333",
            "--copilot-kit-separator-color": isDarkMode ? "#35373a" : "#e0e3eb",
            "--copilot-kit-muted-color": isDarkMode ? "#44474a" : "#717171",
          } as React.CSSProperties
        }
        className={isDarkMode ? "dark-mode" : "light-mode"}
      >
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "flex-end",
            padding: 5,
            overflowY: "auto",
            color: isDarkMode ? theme.palette.text.primary : "inherit",
          }}
        >
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
