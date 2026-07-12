import { Activity, Cpu, GitCommitHorizontal } from "lucide-react";

export function AppFooter() {
  return (
    <footer className="flex h-9 items-center justify-between border-t border-border bg-background/60 px-4 text-[11px] text-muted-foreground backdrop-blur-md">
      <div className="flex items-center gap-4">
        <span className="flex items-center gap-1.5">
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-brand opacity-70" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-brand" />
          </span>
          AiSci Local System
        </span>
      </div>
      <div className="flex items-center gap-1.5 font-mono">
        <Activity className="h-3 w-3" />
        Operational
      </div>
    </footer>
  );
}
