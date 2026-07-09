import { useRouterState } from "@tanstack/react-router";
import { Bell, Loader2, Play } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";

const titles: Record<string, { title: string; crumb: string }> = {
  "/": { title: "Overview", crumb: "Dashboard / Overview" },
  "/fits": { title: "Physics Fits", crumb: "Dashboard / Physics Fits" },
  "/literature": { title: "Literature Intake", crumb: "Dashboard / Literature Intake" },
  "/evidence": { title: "Evidence Ledger", crumb: "Dashboard / Evidence Ledger" },
  "/tasks": { title: "Task Queue", crumb: "Dashboard / Task Queue" },
  "/agents": { title: "Agents", crumb: "Dashboard / Agents" },
};

export function AppHeader() {
  const pathname = useRouterState({ select: (r) => r.location.pathname });
  const meta = titles[pathname] ?? { title: "AiSci", crumb: "Dashboard" };
  const [running, setRunning] = useState(false);

  function runIngest() {
    if (running) return;
    setRunning(true);
    toast("Ingest pipeline started.", {
      description: "Fetching from arXiv + OpenAlex...",
    });
    setTimeout(() => {
      setRunning(false);
      toast.success("Ingest complete.", { description: "8 new papers added." });
    }, 3000);
  }

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur-md">
      <SidebarTrigger />
      <Separator orientation="vertical" className="h-6" />
      <div className="flex flex-col leading-tight">
        <h1 className="text-sm font-semibold tracking-tight">{meta.title}</h1>
        <span className="text-[11px] text-muted-foreground">{meta.crumb}</span>
      </div>

      <div className="ml-auto flex items-center gap-2">
        <Button
          onClick={runIngest}
          disabled={running}
          size="sm"
          className="gap-1.5 bg-primary text-primary-foreground hover:bg-primary/90"
        >
          {running ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Play className="h-3.5 w-3.5" />
          )}
          {running ? "Running…" : "Run Ingest Now"}
        </Button>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-4 w-4" />
          <Badge className="absolute -right-0.5 -top-0.5 h-4 min-w-4 justify-center rounded-full bg-rose-brand p-0 px-1 text-[10px] text-white">
            3
          </Badge>
        </Button>
        <Avatar className="h-8 w-8 ring-1 ring-border">
          <AvatarFallback className="bg-primary/15 text-xs font-semibold text-primary">
            RB
          </AvatarFallback>
        </Avatar>
      </div>
    </header>
  );
}
