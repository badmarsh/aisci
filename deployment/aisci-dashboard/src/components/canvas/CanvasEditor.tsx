import { useState, useCallback, useRef } from 'react';
import {
  ReactFlow,
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  Connection,
  Edge,
  Node
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { nodeTypes } from './CustomNodes';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileCode2, Activity, Play, ShieldCheck, Download, Plus } from "lucide-react";
import { toast } from "sonner";

// Mock Data for Palette
const PALETTE_CLAIMS = [
  { id: "c1", type: "claim", data: { text: "Tsallis distribution perfectly describes the spectra up to 5 GeV", status: "Weak", csPotential: "High" } },
  { id: "c2", type: "claim", data: { text: "Temperature T = 120 MeV implies early freeze-out", status: "Needs CS upgrade", csPotential: "High" } }
];

const PALETTE_PIPELINES = [
  { id: "p1", type: "pipeline", data: { name: "GPU Monte Carlo", desc: "Large parameter explorations.", complexity: "GPU" } },
  { id: "p2", type: "pipeline", data: { name: "Auto-diff Re-fit", desc: "Re-fit with VI/HMC.", complexity: "Compute" } },
  { id: "p3", type: "pipeline", data: { name: "Symbolic Verification", desc: "Jacobian trace analysis.", complexity: "API" } }
];

const PALETTE_EVIDENCE = [
  { id: "e1", type: "evidence", data: { title: "Basic analysis of Tsallis distribution", authors: "J. Doe", summary: "Used basic Boltzmann assumptions, neglected collective flow.", heuristics: { no_chi2: true } } }
];

let id = 0;
const getId = () => `dndnode_${id++}`;

function Sidebar() {
  const onDragStart = (event: React.DragEvent, nodeType: string, data: any) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.setData('application/reactflow/data', JSON.stringify(data));
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div className="w-64 bg-sidebar border-r border-border/50 p-4 flex flex-col h-full overflow-y-auto">
      <h3 className="font-semibold text-sm mb-4">Palette</h3>
      
      <div className="mb-6">
        <h4 className="text-xs font-semibold text-muted-foreground uppercase mb-2">Claims</h4>
        <div className="space-y-2">
          {PALETTE_CLAIMS.map(claim => (
            <div 
              key={claim.id}
              className="border border-border/50 bg-background rounded-md p-2 cursor-grab hover:border-primary/50 text-xs"
              draggable
              onDragStart={(e) => onDragStart(e, 'claim', claim.data)}
            >
              <div className="flex items-center gap-1.5 mb-1 font-semibold text-foreground">
                <FileCode2 className="w-3 h-3 text-primary" /> Extracted Claim
              </div>
              <p className="line-clamp-2 text-muted-foreground">{claim.data.text}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <h4 className="text-xs font-semibold text-muted-foreground uppercase mb-2">Pipelines</h4>
        <div className="space-y-2">
          {PALETTE_PIPELINES.map(pipe => (
            <div 
              key={pipe.id}
              className="border border-border/50 bg-background rounded-md p-2 cursor-grab hover:border-primary/50 text-xs"
              draggable
              onDragStart={(e) => onDragStart(e, 'pipeline', pipe.data)}
            >
              <div className="flex items-center gap-1.5 mb-1 font-semibold text-foreground">
                <Activity className="w-3 h-3 text-primary" /> {pipe.data.name}
              </div>
              <Badge variant="secondary" className="text-[9px]">{pipe.data.complexity}</Badge>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <h4 className="text-xs font-semibold text-muted-foreground uppercase mb-2">External Evidence</h4>
        <div className="space-y-2">
          {PALETTE_EVIDENCE.map(ev => (
            <div 
              key={ev.id}
              className="border border-border/50 bg-indigo-950/20 rounded-md p-2 cursor-grab hover:border-indigo-500/50 text-xs"
              draggable
              onDragStart={(e) => onDragStart(e, 'evidence', ev.data)}
            >
              <div className="flex items-center gap-1.5 mb-1 font-semibold text-indigo-400">
                <Download className="w-3 h-3 text-indigo-400" /> Literature
              </div>
              <p className="line-clamp-2 text-muted-foreground">{ev.data.title}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Inspector({ selectedNode }: { selectedNode: any | null }) {
  if (!selectedNode) {
    return (
      <div className="w-72 bg-sidebar border-l border-border/50 p-4 flex flex-col h-full items-center justify-center text-muted-foreground text-sm">
        Select a node to inspect
      </div>
    );
  }

  return (
    <div className="w-72 bg-sidebar border-l border-border/50 p-4 flex flex-col h-full overflow-y-auto">
      <h3 className="font-semibold text-sm mb-4 capitalize">{selectedNode.type} Details</h3>
      
      <div className="space-y-4">
        <div className="space-y-1 text-xs">
          <span className="text-muted-foreground font-medium uppercase text-[10px]">Node ID</span>
          <p className="font-mono">{selectedNode.id}</p>
        </div>

        {selectedNode.type === 'claim' && (
          <>
            <div className="space-y-1 text-xs">
              <span className="text-muted-foreground font-medium uppercase text-[10px]">Claim Text</span>
              <p className="font-medium bg-background p-2 rounded border border-border/50">{selectedNode.data.text}</p>
            </div>
            <div className="space-y-1 text-xs">
              <span className="text-muted-foreground font-medium uppercase text-[10px]">Status</span>
              <p>{selectedNode.data.status}</p>
            </div>
          </>
        )}

        {selectedNode.type === 'pipeline' && (
          <>
            <div className="space-y-1 text-xs">
              <span className="text-muted-foreground font-medium uppercase text-[10px]">Pipeline Name</span>
              <p className="font-medium">{selectedNode.data.name}</p>
            </div>
            <div className="space-y-1 text-xs">
              <span className="text-muted-foreground font-medium uppercase text-[10px]">Description</span>
              <p className="text-muted-foreground">{selectedNode.data.desc}</p>
            </div>
            <div className="space-y-2 mt-4 pt-4 border-t border-border/50">
              <Button size="sm" className="w-full text-xs">Configure Pipeline...</Button>
            </div>
          </>
        )}

        {selectedNode.type === 'result' && (
          <>
            <div className="space-y-1 text-xs">
              <span className="text-muted-foreground font-medium uppercase text-[10px]">Summary</span>
              <p className="font-medium text-amber-500">{selectedNode.data.summary}</p>
            </div>
            <div className="space-y-1 text-xs">
              <span className="text-muted-foreground font-medium uppercase text-[10px]">Detail</span>
              <p className="text-muted-foreground bg-background p-2 rounded border border-border/50">{selectedNode.data.detail}</p>
            </div>
            <div className="space-y-2 mt-4 pt-4 border-t border-border/50">
              <Button size="sm" variant="default" className="w-full text-xs">Create Manuscript Patch</Button>
              <Button size="sm" variant="outline" className="w-full text-xs">Send to Evidence Ledger</Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'claim',
    data: { text: "Tsallis distribution perfectly describes the spectra up to 5 GeV", status: "Weak", csPotential: "High" },
    position: { x: 100, y: 150 },
  }
];

export function CanvasEditor({ paperId }: { paperId: string }) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  // Load state on mount
  useState(() => {
    fetch(`http://localhost:8001/api/studio/papers/${paperId}/canvas`)
      .then(res => res.json())
      .then(data => {
        if (data.nodes && data.nodes.length > 0) {
          setNodes(data.nodes);
          setEdges(data.edges || []);
        } else {
          setNodes(initialNodes);
        }
      })
      .catch(err => {
        console.error("Failed to load canvas state", err);
        setNodes(initialNodes);
      });
  });

  const saveCanvasState = () => {
    fetch(`http://localhost:8001/api/studio/papers/${paperId}/canvas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nodes, edges })
    })
    .then(res => res.json())
    .then(() => toast.success("Layout saved to Paper Studio workspace"))
    .catch(err => toast.error("Failed to save layout"));
  };

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge({ ...params, animated: true, type: 'default' }, eds)),
    [setEdges],
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      
      const type = event.dataTransfer.getData('application/reactflow');
      const dataStr = event.dataTransfer.getData('application/reactflow/data');

      if (typeof type === 'undefined' || !type || !reactFlowWrapper.current) {
        return;
      }

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const position = {
        x: event.clientX - reactFlowBounds.left - 100,
        y: event.clientY - reactFlowBounds.top - 50,
      };

      const data = dataStr ? JSON.parse(dataStr) : {};
      
      const newNode = {
        id: getId(),
        type,
        position,
        data,
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes],
  );

  const handleNodeClick = (_: React.MouseEvent, node: any) => {
    setSelectedNode(node);
  };

  const handlePaneClick = () => {
    setSelectedNode(null);
  };

  const handleRunGraph = () => {
    // Simulate pipeline execution
    setNodes(nds => nds.map(n => {
      if (n.type === 'pipeline') {
        return { ...n, data: { ...n.data, isRunning: true } };
      }
      return n;
    }));

    toast.success("Starting graph execution...");

    setTimeout(() => {
      setNodes(nds => {
        const newNodes = nds.map(n => {
          if (n.type === 'pipeline') {
            return { ...n, data: { ...n.data, isRunning: false } };
          }
          return n;
        });

        // Add a mock result node for each pipeline connected to a claim
        const resultNodes: any[] = [];
        const newEdges: any[] = [];
        
        edges.forEach(e => {
          const sourceNode = nds.find(n => n.id === e.source);
          const targetNode = nds.find(n => n.id === e.target);
          
          if (sourceNode?.type === 'claim' && targetNode?.type === 'pipeline') {
            const resId = getId();
            resultNodes.push({
              id: resId,
              type: 'result',
              position: { x: targetNode.position.x + 350, y: targetNode.position.y },
              data: { 
                summary: "Fit is under-optimized.", 
                detail: `Pipeline ${targetNode.data.name} suggests checking higher bounds. Local minima hit.`,
                isWarning: true 
              }
            });
            newEdges.push({
              id: `e-${targetNode.id}-${resId}`,
              source: targetNode.id,
              target: resId,
              animated: true
            });
          }
        });

        if (resultNodes.length > 0) {
          toast.success("Graph execution complete. Results generated.");
          setEdges(eds => [...eds, ...newEdges]);
          return [...newNodes, ...resultNodes];
        } else {
          toast("No pipelines connected to claims.");
          return newNodes;
        }
      });
    }, 2500);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] rounded-xl overflow-hidden border border-border/50 shadow-sm relative">
      {/* Top Toolbar */}
      <div className="h-12 bg-background border-b border-border/50 flex items-center justify-between px-4 z-10">
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30">Canvas Mode</Badge>
          <span className="text-sm font-medium text-muted-foreground ml-2">Drag claims and pipelines to construct your analysis</span>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="h-8 text-xs" onClick={saveCanvasState}>
            <Download className="w-3 h-3 mr-2" /> Save Layout
          </Button>
          <Button size="sm" className="h-8 text-xs" onClick={handleRunGraph}>
            <Play className="w-3 h-3 mr-2" /> Run Graph
          </Button>
        </div>
      </div>
      
      {/* Editor Body */}
      <div className="flex flex-1 overflow-hidden">
        <ReactFlowProvider>
          <Sidebar />
          
          <div className="flex-1 h-full bg-muted/10 relative" ref={reactFlowWrapper}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onInit={() => {}}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onNodeClick={handleNodeClick}
              onPaneClick={handlePaneClick}
              nodeTypes={nodeTypes}
              fitView
              className="bg-muted/10"
            >
              <Controls />
              <Background gap={16} size={1} />
            </ReactFlow>
          </div>

          <Inspector selectedNode={selectedNode} />
        </ReactFlowProvider>
      </div>
    </div>
  );
}
