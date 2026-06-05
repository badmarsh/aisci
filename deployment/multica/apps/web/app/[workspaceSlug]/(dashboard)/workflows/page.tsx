import React from "react";
import { WorkflowsCanvas } from "./workflows-canvas";
import { getArchitectureMap } from "./architecture-parser";

export const dynamic = "force-dynamic";

export default async function WorkflowsPage() {
  const { nodes, edges } = await getArchitectureMap();
  
  return (
    <div className="flex h-full w-full flex-col">
      <div className="p-6 pb-2">
        <h1 className="text-2xl font-semibold tracking-tight">System Architecture Map</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Visualizing the entire AISCI ecosystem across Infrastructure, Orchestration, and Science layers.
        </p>
      </div>
      <div className="flex-1 p-6 pt-2 h-[calc(100vh-120px)]">
        <div className="border rounded-xl h-full w-full overflow-hidden bg-background">
          <WorkflowsCanvas initialNodes={nodes} initialEdges={edges} />
        </div>
      </div>
    </div>
  );
}
