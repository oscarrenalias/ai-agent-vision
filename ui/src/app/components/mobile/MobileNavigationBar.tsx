import React from "react";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import RestaurantMenuIcon from "@mui/icons-material/RestaurantMenu";
import BarChartIcon from "@mui/icons-material/BarChart";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import { useTheme } from "@mui/material";

interface MobileNavigationBarProps {
  active: string;
  setActive: (section: string) => void;
}

export default function MobileNavigationBar({
  active,
  setActive,
}: MobileNavigationBarProps) {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";
  const tabBarClass = `mobile-tab-bar ${
    isDarkMode ? "dark-mode" : "light-mode"
  }`;
  return (
    <nav className={tabBarClass}>
      <button
        className={active === "chat" ? "active" : ""}
        onClick={() => setActive("chat")}
        aria-label="Chat"
      >
        <ChatBubbleOutlineIcon />
      </button>
      <button
        className={active === "analytics" ? "active" : ""}
        onClick={() => setActive("analytics")}
        aria-label="Analytics"
      >
        <BarChartIcon />
      </button>
      <button
        className={active === "shopping" ? "active" : ""}
        onClick={() => setActive("shopping")}
        aria-label="Shopping List"
      >
        <ShoppingCartIcon />
      </button>
      <button
        className={active === "meal" ? "active" : ""}
        onClick={() => setActive("meal")}
        aria-label="Meal Planning"
      >
        <RestaurantMenuIcon />
      </button>
      <button
        className={active === "recipes" ? "active" : ""}
        onClick={() => setActive("recipes")}
        aria-label="Recipes"
      >
        <MenuBookIcon />
      </button>
    </nav>
  );
}
