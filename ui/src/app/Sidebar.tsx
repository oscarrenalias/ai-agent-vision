import React from "react";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import IconButton from "@mui/material/IconButton";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import RestaurantMenuIcon from "@mui/icons-material/RestaurantMenu";
import BarChartIcon from "@mui/icons-material/BarChart";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import MenuBookIcon from "@mui/icons-material/MenuBook";

interface SidebarProps {
  open: boolean;
  onToggle: () => void;
  activeSection: string;
  setActiveSection: (section: string) => void;
}

const sections = [
  { key: "shopping", icon: <ShoppingCartIcon />, label: "Shopping List" },
  { key: "meal", icon: <RestaurantMenuIcon />, label: "Meal Planning" },
  { key: "analytics", icon: <BarChartIcon />, label: "Analytics" },
  { key: "recipes", icon: <MenuBookIcon />, label: "Recipes" },
];

export default function Sidebar({
  open,
  onToggle,
  activeSection,
  setActiveSection,
}: SidebarProps) {
  return (
    <Drawer
      variant="permanent"
      open={open}
      PaperProps={{
        sx: {
          width: open ? 200 : 56,
          transition: "width 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
          overflowX: "hidden",
          boxSizing: "border-box",
        },
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: open ? "flex-end" : "center",
          alignItems: "center",
          padding: 8,
        }}
      >
        <IconButton onClick={onToggle} size="small">
          {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </div>
      <List>
        {sections.map((section) => (
          <ListItem disablePadding sx={{ display: "block" }} key={section.key}>
            <ListItemButton
              selected={activeSection === section.key}
              onClick={() => setActiveSection(section.key)}
              sx={{
                justifyContent: open ? "initial" : "center",
                px: 2.5,
                minHeight: 48,
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: open ? 2 : "auto",
                  justifyContent: "center",
                }}
              >
                {section.icon}
              </ListItemIcon>
              {open && <ListItemText primary={section.label} />}
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}
