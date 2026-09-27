import * as React from "react";
import { AIAssistantInterface } from "@/components/ui/ai-assistant-interface";
import AIThinkingBlock from "@/components/ui/ai-thinking-block";

export function Demo() {
  return (
    <div className="w-screen">
      <AIAssistantInterface />
    </div>
  );
}

export function DemoOne() {
  return <AIThinkingBlock />;
}

export default DemoOne;
