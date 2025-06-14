import React from "react";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import RestaurantMenuIcon from "@mui/icons-material/RestaurantMenu";
import BarChartIcon from "@mui/icons-material/BarChart";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import { useTheme } from "@mui/material";

interface MobileSidebarProps {
  active: string;
  setActive: (section: string) => void;
}

export default function MobileSidebar({ active, setActive }: MobileSidebarProps) {
  // Add dark-mode/light-mode class to sidebar for theme CSS targeting
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";
  // Debugging output
  console.log("[MobileSidebar] theme.palette.mode:", theme.palette.mode, "isDarkMode:", isDarkMode);
  const sidebarClass = `sidebar ${isDarkMode ? "dark-mode" : "light-mode"}`;
  return (
    <div className={sidebarClass}>
      <button onClick={() => setActive("chat")} aria-label="Chat" style={{ background: active === "chat" ? "#4285f4" : "none", color: "#fff", border: "none", fontSize: 24, margin: 12, borderRadius: 8 }}>
        <ChatBubbleOutlineIcon />
      </button>
      <button onClick={() => setActive("analytics")} aria-label="Analytics" style={{ background: active === "analytics" ? "#4285f4" : "none", color: "#fff", border: "none", fontSize: 24, margin: 12, borderRadius: 8 }}>
        <BarChartIcon />
      </button>
      <button onClick={() => setActive("shopping")} aria-label="Shopping List" style={{ background: active === "shopping" ? "#4285f4" : "none", color: "#fff", border: "none", fontSize: 24, margin: 12, borderRadius: 8 }}>
        <ShoppingCartIcon />
      </button>
      <button onClick={() => setActive("meal")} aria-label="Meal Planning" style={{ background: active === "meal" ? "#4285f4" : "none", color: "#fff", border: "none", fontSize: 24, margin: 12, borderRadius: 8 }}>
        <RestaurantMenuIcon />
      </button>
    </div>
  );
}
