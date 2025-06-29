"use client";

import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { useAgentState } from "./components/AgentStateProvider";
import Sidebar from "./Sidebar";
import ShoppingListSection from "./ShoppingListSection";
import MealPlanningSection from "./MealPlanningSection";
import AnalyticsSection from "./AnalyticsSection";
import RecipesSection from "./RecipesSection";
import { useCopilotAction } from "@copilotkit/react-core";
import ReceiptCard from "./components/chat/ReceiptCard";
import RecipeCard from "./components/chat/RecipeCard";
import PriceLookupCard from "./components/chat/PriceLookupCard";
import { ToolProcessingIndicator } from "./components/ToolProcessingIndicator";
import React, { useState } from "react";
import AgentStateInspector from "./components/debug/AgentStateInspector";
import { useTheme } from "@mui/material";
import useMediaQuery from "@mui/material/useMediaQuery";
import MobileNavigationBar from "./components/mobile/MobileNavigationBar";
import "./copilotchat-custom.css";

// Helper to determine dark mode
function useIsDarkMode() {
  const theme = useTheme();
  return theme.palette.mode === "dark";
}

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false); // default to slid in
  const [activeSection, setActiveSection] = useState("analytics");
  const [activeMobileView, setActiveMobileView] = useState<string>("chat");
  const isMobile = useMediaQuery("(max-width: 810px)");

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
  const isDarkMode = useIsDarkMode();

  // Main section for desktop
  let MainSection: React.ReactNode = null;
  if (activeSection === "shopping") {
    MainSection = <ShoppingListSection />;
  } else if (activeSection === "meal") {
    MainSection = <MealPlanningSection />;
  } else if (activeSection === "recipes") {
    MainSection = <RecipesSection />;
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

  // Main section for mobile
  let MobileMainSection: React.ReactNode = null;
  if (activeMobileView === "shopping") {
    MobileMainSection = <ShoppingListSection />;
  } else if (activeMobileView === "meal") {
    MobileMainSection = <MealPlanningSection />;
  } else if (activeMobileView === "recipes") {
    MobileMainSection = <RecipesSection />;
  } else if (activeMobileView === "analytics") {
    MobileMainSection = (
      <AnalyticsSection
        year={year}
        month={month}
        setYear={setYear}
        setMonth={setMonth}
      />
    );
  }

  return (
    <div
      className="app-container"
      style={{ display: "flex", height: "100vh", width: "100vw" }}
    >
      <AgentStateInspector state={state} />
      {isMobile ? (
        <MobileNavigationBar
          active={activeMobileView}
          setActive={setActiveMobileView}
        />
      ) : (
        <div className="sidebar">
          <Sidebar
            open={sidebarOpen}
            onToggle={() => setSidebarOpen((o) => !o)}
            activeSection={activeSection}
            setActiveSection={setActiveSection}
          />
        </div>
      )}
      <div
        className="main-content"
        style={{
          flex: 6,
          overflowY: "auto",
          padding: isMobile ? "24px 24px 24px 72px" : "24px 0 24px 0", // Remove all horizontal padding on desktop
          height: "100%",
        }}
      >
        {isMobile ? (
          activeMobileView === "chat" ? (
            <div
              className={`chat-box ${isDarkMode ? "dark-mode" : "light-mode"}`}
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
          ) : (
            MobileMainSection
          )
        ) : (
          <>
            {MainSection}
            <div
              className={`chat-box ${isDarkMode ? "dark-mode" : "light-mode"}`}
              style={{
                flex: 4,
                height: "calc(100vh - 32px)",
                minWidth: 320,
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
                background: isDarkMode
                  ? theme.palette.background.paper
                  : "#fff",
                borderRadius: 20,
                margin: 16,
                boxShadow: "none",
                border: `1px solid ${
                  isDarkMode ? theme.palette.divider : "#e0e3eb"
                }`,
              }}
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
          </>
        )}
      </div>
    </div>
  );
}
