import Image from "next/image";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

export default function Home() {
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
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
      </main>
    </div>
  );
}
