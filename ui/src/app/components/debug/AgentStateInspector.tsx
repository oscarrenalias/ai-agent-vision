import React, { useState } from "react";

interface AgentStateInspectorProps {
  state: any;
}

const AgentStateInspector: React.FC<AgentStateInspectorProps> = ({ state }) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        style={{
          position: "fixed",
          top: 10,
          left: 10,
          zIndex: 1100,
          background: "#222",
          color: "#fff",
          border: "none",
          borderRadius: "50%",
          width: "44px",
          height: "44px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "22px",
          cursor: "pointer",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
        }}
        onClick={() => setOpen((v) => !v)}
        aria-label={
          open ? "Hide Agent State Inspector" : "Show Agent State Inspector"
        }
      >
        🔍
      </button>
      {open && (
        <div
          style={{
            position: "fixed",
            top: 50,
            left: 0,
            zIndex: 1000,
            padding: "1rem",
            borderBottomRightRadius: "8px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            height: "80vh",
            width: "600px",
            background: "rgba(18, 17, 17, 0.85)",
            fontSize: "12px",
            lineHeight: 1.4,
            backdropFilter: "blur(2px)",
            overflowY: "auto",
            minWidth: "400px",
            maxWidth: "600px",
            minHeight: "400px",
          }}
        >
          <h3 style={{ marginTop: 0, fontSize: "14px" }}>Agent State:</h3>
          <pre style={{ margin: 0, fontSize: "12px" }}>
            {JSON.stringify(state, null, 2)}
          </pre>
        </div>
      )}
    </>
  );
};

export default AgentStateInspector;
