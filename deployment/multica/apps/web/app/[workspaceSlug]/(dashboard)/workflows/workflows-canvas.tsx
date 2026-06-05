"use client";

import React, { useCallback, useMemo, useState } from "react";
import { ReactFlow, Background, Controls, useNodesState, useEdgesState } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { customNodeTypes } from "./custom-nodes";
import type { CustomNodeData } from "./custom-nodes";
import { NodeDetailsSheet } from "./node-details-sheet";

interface WorkflowsCanvasProps {
  initialNodes: Node[];
  initialEdges: Edge[];
}

export function WorkflowsCanvas({ initialNodes, initialEdges }: WorkflowsCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  
  const [selectedNodeData, setSelectedNodeData] = useState<CustomNodeData | null>(null);
  const [isSheetOpen, setIsSheetOpen] = useState(false);

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    if (node.type === "group") return; // Ignore group node clicks
    setSelectedNodeData(node.data as CustomNodeData);
    setIsSheetOpen(true);
  }, []);

  return (
    <>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={customNodeTypes}
        fitView
        className="bg-background"
      >
        <Background color="#64748b" gap={16} />
        <Controls />
      </ReactFlow>

      <NodeDetailsSheet 
        node={selectedNodeData} 
        open={isSheetOpen} 
        onOpenChange={setIsSheetOpen} 
      />
    </>
  );
}
