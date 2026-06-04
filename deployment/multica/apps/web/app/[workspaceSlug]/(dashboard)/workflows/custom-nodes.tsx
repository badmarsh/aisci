"use client";

import React from "react";
import { Handle, Position } from "@xyflow/react";
import { Database, Server, Bot, Beaker, LayoutTemplate, Activity } from "lucide-react";

export type CustomNodeData = {
  label: string;
  type?: string;
  description?: string;
  path?: string;
  status?: string;
  config?: any;
};

function BaseNode({ data, icon: Icon, colorClass, borderClass, bgClass }: { data: CustomNodeData, icon: any, colorClass: string, borderClass: string, bgClass: string }) {
  return (
    <div className={`relative flex items-center p-3 rounded-xl border backdrop-blur-md shadow-sm min-w-[200px] transition-all duration-200 hover:shadow-md cursor-pointer ${bgClass} ${borderClass}`}>
      <Handle type="target" position={Position.Top} className="w-2 h-2 rounded-full !bg-muted-foreground border-none" />
      
      <div className={`flex items-center justify-center w-10 h-10 rounded-lg ${colorClass} bg-background/50 mr-3 shrink-0`}>
        <Icon className="w-5 h-5" />
      </div>
      
      <div className="flex flex-col">
        <span className="text-sm font-semibold text-foreground truncate">{data.label}</span>
        {data.type && <span className="text-xs text-muted-foreground truncate">{data.type}</span>}
      </div>

      {data.status === "active" && (
        <span className="absolute top-[-4px] right-[-4px] flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
        </span>
      )}

      <Handle type="source" position={Position.Bottom} className="w-2 h-2 rounded-full !bg-muted-foreground border-none" />
    </div>
  );
}

export function InfrastructureNode({ data }: { data: CustomNodeData }) {
  return <BaseNode data={data} icon={Database} colorClass="text-blue-500" borderClass="border-blue-500/20" bgClass="bg-blue-500/5 hover:bg-blue-500/10" />;
}

export function AgentNode({ data }: { data: CustomNodeData }) {
  return <BaseNode data={data} icon={Bot} colorClass="text-purple-500" borderClass="border-purple-500/20" bgClass="bg-purple-500/5 hover:bg-purple-500/10" />;
}

export function ScienceNode({ data }: { data: CustomNodeData }) {
  return <BaseNode data={data} icon={Beaker} colorClass="text-emerald-500" borderClass="border-emerald-500/20" bgClass="bg-emerald-500/5 hover:bg-emerald-500/10" />;
}

export function UINode({ data }: { data: CustomNodeData }) {
  return <BaseNode data={data} icon={LayoutTemplate} colorClass="text-orange-500" borderClass="border-orange-500/20" bgClass="bg-orange-500/5 hover:bg-orange-500/10" />;
}

export function ServiceNode({ data }: { data: CustomNodeData }) {
  return <BaseNode data={data} icon={Server} colorClass="text-rose-500" borderClass="border-rose-500/20" bgClass="bg-rose-500/5 hover:bg-rose-500/10" />;
}

export function GroupNode({ data }: { data: CustomNodeData }) {
  return (
    <div className="w-full h-full min-w-[300px] min-h-[300px] rounded-2xl border-2 border-dashed border-muted-foreground/20 bg-muted/5 pointer-events-none relative">
      <div className="absolute top-0 left-0 px-4 py-2 bg-muted-foreground/10 rounded-br-lg rounded-tl-xl backdrop-blur-sm flex items-center gap-2">
        <Activity className="w-4 h-4 text-muted-foreground" />
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{data.label}</span>
      </div>
    </div>
  );
}

export const customNodeTypes = {
  infrastructure: InfrastructureNode,
  agent: AgentNode,
  science: ScienceNode,
  ui: UINode,
  service: ServiceNode,
  group: GroupNode,
};
