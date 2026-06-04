import React from "react";
import { PageHeader } from "@multica/views/layout";

export default function BrowserAgentPage() {
  return (
    <div className="flex h-full flex-col">
      <PageHeader>
        <div className="flex flex-col">
          <h1 className="text-lg font-semibold tracking-tight">Browser Agent</h1>
          <p className="text-xs text-muted-foreground">browser-use / Chat UI Concept</p>
        </div>
      </PageHeader>
      <div className="flex-1 overflow-hidden p-6 bg-muted/20">
        <div className="h-full w-full overflow-hidden rounded-xl border border-border bg-background shadow-sm">
          <iframe 
            src="http://localhost:3001" 
            className="h-full w-full border-none"
            title="Browser Agent (chat-ui-example)"
          />
        </div>
      </div>
    </div>
  );
}
