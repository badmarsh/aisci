import { Handle, Position } from '@xyflow/react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, AlertTriangle, FileCode2, ShieldCheck, Activity, BookOpen } from "lucide-react";

export function ClaimNode({ data }: { data: any }) {
  return (
    <div className="w-[280px] bg-background border-2 border-primary/20 rounded-lg shadow-md overflow-hidden relative">
      <div className="bg-muted/30 px-3 py-2 border-b flex justify-between items-center">
        <span className="font-semibold text-xs text-foreground flex items-center gap-1.5">
          <FileCode2 className="w-3 h-3 text-primary" /> Claim
        </span>
        <Badge variant="outline" className={
          data.csPotential === "High" ? "bg-violet-500/10 text-violet-500 border-violet-500/30 text-[10px]" : "text-[10px]"
        }>
          CS Potential: {data.csPotential || "Low"}
        </Badge>
      </div>
      <div className="p-3">
        <p className="text-xs leading-relaxed font-medium">{data.text}</p>
        <div className="mt-2 flex items-center gap-2">
           <Badge variant="outline" className={
              data.status === "Weak" ? "text-amber-500 border-amber-500/30 text-[9px]" :
              data.status === "Needs CS upgrade" ? "text-destructive border-destructive/30 text-[9px]" :
              "text-emerald-500 border-emerald-500/30 text-[9px]"
            }>{data.status}</Badge>
        </div>
      </div>
      
      {/* Target for incoming connections (none typically for a root claim, but maybe manuscript sources) */}
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-muted-foreground border-2 border-background" />
      {/* Source for pipelines to attach to */}
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-primary border-2 border-background" />
    </div>
  );
}

export function PipelineNode({ data }: { data: any }) {
  return (
    <div className="w-[240px] bg-sidebar border-2 border-border/50 rounded-lg shadow-sm overflow-hidden relative group hover:border-primary/50 transition-colors">
      <div className="bg-muted/10 px-3 py-2 border-b flex justify-between items-center">
        <span className="font-semibold text-xs text-foreground flex items-center gap-1.5">
          <Activity className="w-3 h-3 text-primary" /> Pipeline
        </span>
        <Badge variant="secondary" className="text-[10px] uppercase">{data.complexity}</Badge>
      </div>
      <div className="p-3">
        <p className="text-xs font-semibold mb-1">{data.name}</p>
        <p className="text-[10px] text-muted-foreground line-clamp-2">{data.desc}</p>
        
        {data.isRunning && (
          <div className="mt-2 text-[10px] text-primary flex items-center gap-1">
            <Activity className="w-3 h-3 animate-spin" /> Running...
          </div>
        )}
      </div>

      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-primary border-2 border-background" />
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-emerald-500 border-2 border-background" />
    </div>
  );
}

export function ResultNode({ data }: { data: any }) {
  return (
    <div className="w-[260px] bg-background border-2 border-emerald-500/30 rounded-lg shadow-lg overflow-hidden relative">
      <div className="bg-emerald-500/10 px-3 py-2 border-b border-emerald-500/20 flex justify-between items-center">
        <span className="font-semibold text-xs text-emerald-500 flex items-center gap-1.5">
          <ShieldCheck className="w-3 h-3" /> Result
        </span>
      </div>
      <div className="p-3">
        <div className="flex items-start gap-2 mb-2">
          {data.isWarning ? (
            <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
          )}
          <p className="text-xs font-medium">{data.summary}</p>
        </div>
        <p className="text-[10px] text-muted-foreground">{data.detail}</p>
      </div>

      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-emerald-500 border-2 border-background" />
    </div>
  );
}

export function EvidenceNode({ data, isConnectable }: { data: any, isConnectable: boolean }) {
  return (
    <div className="bg-background border-2 border-indigo-500/50 rounded-xl shadow-lg w-72 overflow-hidden">
      <Handle type="source" position={Position.Right} isConnectable={isConnectable} className="w-3 h-3 bg-indigo-500" />
      <div className="bg-indigo-500/10 p-3 border-b border-indigo-500/20 flex items-center justify-between">
        <div className="flex items-center gap-2 text-indigo-400 font-semibold text-xs">
          <BookOpen className="w-4 h-4" />
          EXTERNAL EVIDENCE
        </div>
        <Badge variant="outline" className="text-[10px] bg-background border-indigo-500/50 text-indigo-400">
          Literature
        </Badge>
      </div>
      <div className="p-3">
        <p className="text-sm font-medium leading-snug mb-2">
          {data.title}
        </p>
        <p className="text-xs text-muted-foreground mb-3 font-mono">
          {data.authors}
        </p>
        <div className="bg-muted/30 p-2 rounded text-xs border border-border/50 text-muted-foreground">
          {data.summary}
        </div>
      </div>
    </div>
  );
}

export const nodeTypes = {
  claim: ClaimNode,
  pipeline: PipelineNode,
  result: ResultNode,
  evidence: EvidenceNode
};
