import type { Metadata } from "next";
import "./globals.css";

import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";
import ThemeRegistry from "./components/ThemeRegistry";
import { AgentStateProvider } from "./components/AgentStateProvider";
import { v4 as uuidv4 } from "uuid";
import { CopilotKit } from "@copilotkit/react-core";
import { AGENT_NAME } from "./lib/types";

export const metadata: Metadata = {
  title: "Home Assistant Copilot",
  applicationName: "Home Assistant Copilot",
  description: "Home Assistant Copilot",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const threadId = uuidv4();

  return (
    <html lang="en">
      <body>
        <ThemeRegistry>
          <CopilotKit
            runtimeUrl="/api/copilotkit"
            agent={AGENT_NAME}
            threadId={threadId}
          >
            <AgentStateProvider>{children}</AgentStateProvider>
          </CopilotKit>
        </ThemeRegistry>
      </body>
    </html>
  );
}
