import React from "react";

export type ToolProcessingIndicatorProps = {
  message?: string;
};

export const ToolProcessingIndicator: React.FC<
  ToolProcessingIndicatorProps
> = ({ message = "Processing, please wait..." }) => {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        fontSize: "0.85em", // smaller font
        color: "#666",
        margin: "8px 0",
      }}
    >
      <span
        style={{
          width: 16,
          height: 16,
          marginRight: 8,
          border: "2px solid #ccc",
          borderTop: "2px solid #333",
          borderRadius: "50%",
          display: "inline-block",
          animation: "spin 1s linear infinite",
        }}
      />
      <span>{message}</span>
      <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
    </div>
  );
};
