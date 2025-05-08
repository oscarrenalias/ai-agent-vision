"use client";
import React from "react";
import {
  ThemeProvider,
  CssBaseline,
  createTheme,
  useMediaQuery,
} from "@mui/material";

export default function ThemeRegistry({
  children,
}: {
  children: React.ReactNode;
}) {
  const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");
  const theme = React.useMemo(
    () =>
      createTheme({
        palette: {
          mode: prefersDarkMode ? "dark" : "light",
          background: {
            default: prefersDarkMode ? "#1e1e1e" : "#fafafa",
            paper: prefersDarkMode ? "#23272e" : "#fff",
          },
          text: {
            primary: prefersDarkMode ? "#e0e0e0" : "#23272e",
            secondary: prefersDarkMode ? "#bdbdbd" : "#333",
          },
        },
        typography: {
          fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
        },
      }),
    [prefersDarkMode]
  );
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
