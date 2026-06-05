"use client";

import React from "react";
import { FileCode2, Info, Activity, Settings2, X } from "lucide-react";
import type { CustomNodeData } from "./custom-nodes";

interface NodeDetailsSheetProps {
  node: CustomNodeData | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function NodeDetailsSheet({ node, open, onOpenChange }: NodeDetailsSheetProps) {
  if (!node || !open) return null;

  return (
    <>
      <div 
        className="fixed inset-0 z-40 bg-background/50 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />
      <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[540px] border-l bg-background/95 backdrop-blur-xl shadow-2xl p-6 overflow-y-auto transform transition-transform duration-300 ease-in-out">
        <button 
          onClick={() => onOpenChange(false)}
          className="absolute top-4 right-4 p-2 rounded-md opacity-70 hover:opacity-100 hover:bg-muted transition-opacity"
        >
          <X className="w-5 h-5" />
        </button>
        
        <div className="mb-6 mt-2">
          <div className="flex items-center gap-2 mb-3">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border uppercase tracking-wider bg-transparent text-foreground">
              {node.type || "Component"}
            </span>
            {node.status === "active" && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500 text-white">
                Active
              </span>
            )}
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">{node.label}</h2>
          <p className="text-muted-foreground mt-2 text-sm">
            {node.description || "No description provided for this component."}
          </p>
        </div>

        <div className="space-y-6">
          {node.path && (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold flex items-center gap-2 text-foreground">
                <FileCode2 className="w-4 h-4 text-muted-foreground" />
                Location
              </h4>
              <div className="p-3 bg-muted/50 rounded-lg border text-sm font-mono text-muted-foreground break-all">
                {node.path}
              </div>
            </div>
          )}

          {node.config && (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold flex items-center gap-2 text-foreground">
                <Settings2 className="w-4 h-4 text-muted-foreground" />
                Configuration
              </h4>
              <div className="p-4 bg-muted/30 rounded-lg border overflow-x-auto">
                <pre className="text-xs font-mono text-muted-foreground">
                  {JSON.stringify(node.config, null, 2)}
                </pre>
              </div>
            </div>
          )}

          <div className="space-y-2">
            <h4 className="text-sm font-semibold flex items-center gap-2 text-foreground">
              <Activity className="w-4 h-4 text-muted-foreground" />
              Runtime Status
            </h4>
            <div className="p-4 bg-muted/30 rounded-lg border text-sm text-muted-foreground">
              This component is currently part of the active execution flow.
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
