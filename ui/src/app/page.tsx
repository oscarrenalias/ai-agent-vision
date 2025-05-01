import Image from "next/image";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

export default function Home() {
  return (
    <div style={{ display: "flex", height: "100vh", width: "100vw" }}>
      {/* Left side: scrollable, for backend agent state info */}
      <div style={{ flex: 6, overflowY: "auto", padding: 24 }}>
        {/* Replace this with your backend agent state info */}
        <h1>Agent State Information</h1>
        <p>
          This area will display information from your backend agent state. Add
          your content here.
        </p>
        {/* Example long content for scrolling */}
        <div style={{ height: 1200 }} />
      </div>
      {/* Right side: CopilotChat, always visible */}
      <div
        style={{
          flex: 4,
          borderLeft: "1px solid #eee",
          height: "100vh",
          position: "sticky",
          top: 0,
          minWidth: 320,
        }}
      >
        <CopilotKit runtimeUrl="/api/copilotkit" agent="mighty_assistant">
          <CopilotChat
            instructions={
              "You are assisting the user as best as you can. Answer in the best way possible given the data you have."
            }
            labels={{
              title: "Your Assistant",
              initial: "Hi! 👋 How can I assist you today?",
            }}
          />
        </CopilotKit>
      </div>
    </div>
  );
}
