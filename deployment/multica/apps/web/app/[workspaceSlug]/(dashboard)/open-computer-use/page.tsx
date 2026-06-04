import React from "react";
import { PageHeader } from "@multica/views/layout";

export default function OpenComputerUsePage() {
  return (
    <div className="flex h-full flex-col">
      <PageHeader>
        <div className="flex flex-col">
          <h1 className="text-lg font-semibold tracking-tight">OpenComputer Use</h1>
          <p className="text-xs text-muted-foreground">Anthropic / Coasty.ai open-computer-use</p>
        </div>
      </PageHeader>
      <div className="flex-1 overflow-hidden p-6 bg-muted/20">
        <div className="h-full w-full overflow-hidden rounded-xl border border-border bg-background shadow-sm">
          <iframe 
            src="http://[::1]:3004" 
            className="h-full w-full border-none"
            title="OpenComputer Use"
          />
        </div>
      </div>
    </div>
  );
}
