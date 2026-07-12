import { createFileRoute, useParams, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Terminal, Play, Loader2, Clock, Activity, Target } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { PageShell } from "@/components/PageShell";
import { type Agent } from "@/lib/api";
import { useSuspenseQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAgents, fetchPipelines, triggerPipeline } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { Suspense } from "react";
import { QueryErrorBoundary } from "@/components/QueryErrorBoundary";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export const Route = createFileRoute("/projects/$projectId/agents")({
  head: () => ({
    meta: [
      { title: "Agents — AiSci" },
      {
        name: "description",
        content:
          "Active agent sessions running the AiSci autonomous research pipeline with live logs.",
      },
    ],
  }),
  component: AgentsPage,
});

const statusStyles: Record<Agent["status"] | string, string> = {
  ACTIVE: "bg-emerald-brand",
  IDLE: "bg-muted-foreground",
  WAITING: "bg-amber-brand",
};

function AgentsPage() {
  const { projectId } = useParams({ strict: false }) as { projectId: string };

  return (
    <PageShell>
      <QueryErrorBoundary>
        <Suspense fallback={<Skeleton className="h-[200px] w-full mt-6" />}>
          <AgentsContent projectId={projectId} />
        </Suspense>
      </QueryErrorBoundary>
    </PageShell>
  );
}

function AgentsContent({ projectId }: { projectId: string }) {
  const [open, setOpen] = useState<Agent | null>(null);
  const [selectedPipeline, setSelectedPipeline] = useState<string>("");
  const queryClient = useQueryClient();

  const { data: agents = [] } = useSuspenseQuery({
    queryKey: ["agents", projectId],
    queryFn: () => fetchAgents(projectId as string),
  });

  const { data: pipelines } = useSuspenseQuery({
    queryKey: ["pipelines", projectId],
    queryFn: () => fetchPipelines(projectId as string),
  });

  const { mutate: runPipeline, isPending: isRunning } = useMutation({
    mutationFn: () => triggerPipeline(projectId, selectedPipeline),
    onSuccess: () => {
      toast.success("Pipeline dispatched successfully");
      queryClient.invalidateQueries({ queryKey: ["agents", projectId] });
      queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to trigger pipeline");
    },
  });

  return (
    <>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Active Agents</h1>
          <p className="text-muted-foreground mt-2">
            Autonomous research agents assigned to project: {projectId}
          </p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 bg-card/50 glass-card p-4 rounded-xl border border-border mb-6 shadow-sm">
        <div className="text-sm font-medium whitespace-nowrap text-foreground/80">Dispatch Pipeline:</div>
        <div className="flex gap-3 w-full sm:w-auto items-center">
          <Select value={selectedPipeline} onValueChange={setSelectedPipeline}>
            <SelectTrigger className="w-[220px] bg-background">
              <SelectValue placeholder="Select pipeline..." />
            </SelectTrigger>
            <SelectContent>
              {pipelines?.map(p => (
                <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
              ))}
              {!pipelines?.length && <SelectItem value="none" disabled>No pipelines found</SelectItem>}
            </SelectContent>
          </Select>
          <Button
            onClick={() => runPipeline()}
            disabled={!selectedPipeline || selectedPipeline === "none" || isRunning}
            className="gap-2 bg-gradient-to-r from-primary to-primary/80 shadow-md shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all"
          >
            {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current" />}
            Run
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-2">
        {agents.map((a: Agent | any) => (
          <Card key={a.name} className="glass-card fade-in-up transition hover:border-primary/40 flex flex-col">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between mb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <span className="relative flex h-2 w-2">
                    {a.status === "ACTIVE" && (
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-brand opacity-60" />
                    )}
                    <span
                      className={`relative inline-flex h-2 w-2 rounded-full ${statusStyles[a.status] || "bg-muted-foreground"}`}
                    />
                  </span>
                  {a.name}
                </CardTitle>
                <div className="flex gap-2">
                  {a.provider && (
                    <Badge
                      variant="outline"
                      className="border-border text-muted-foreground font-mono"
                    >
                      {a.provider}
                    </Badge>
                  )}
                  <Badge
                    className={
                      a.status === "ACTIVE"
                        ? "bg-emerald-brand/15 text-emerald-brand ring-1 ring-emerald-brand/40"
                        : a.status === "IDLE"
                          ? "bg-muted text-muted-foreground ring-1 ring-border"
                          : "bg-amber-brand/15 text-amber-brand ring-1 ring-amber-brand/40"
                    }
                  >
                    {a.status}
                  </Badge>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-border/50">
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] uppercase font-semibold text-muted-foreground flex items-center gap-1"><Target className="w-3 h-3" /> Scope</span>
                  <span className="text-xs font-mono">{a.scope || (a.name.toLowerCase().includes("fit") ? "Physics Fits" : "Literature")}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] uppercase font-semibold text-muted-foreground flex items-center gap-1"><Clock className="w-3 h-3" /> Last Run</span>
                  <span className="text-xs font-mono">{a.last || "Never"} <span className="text-muted-foreground">({a.duration || "—"})</span></span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] uppercase font-semibold text-muted-foreground flex items-center gap-1"><Activity className="w-3 h-3" /> Error Rate</span>
                  <span className="text-xs font-mono">{a.errorRate || "0%"}</span>
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col">
              <p className="mb-3 text-sm text-foreground/80 leading-relaxed border-l-2 border-primary/20 pl-3">
                {a.summary}
              </p>
              
              <div className="rounded-md border border-border bg-muted/50 p-2.5 font-mono text-[11px] leading-relaxed mb-4 flex-1">
                {a.log?.length > 0 ? a.log.slice(0, 5).map((line: string, i: number) => (
                  <div key={i} className="truncate text-zinc-600 dark:text-zinc-400">
                    <span className="text-emerald-600/70 dark:text-emerald-500/70">›</span> {line}
                  </div>
                )) : (
                  <div className="text-zinc-500 italic opacity-50 flex items-center gap-2">
                    <Terminal className="w-3 h-3" /> No recent logs
                  </div>
                )}
              </div>
              
              <div className="mt-auto flex justify-between items-center border-t border-border/50 pt-3">
                <Link to="/projects/$projectId/jobs" params={{ projectId }} className="text-[11px] font-medium text-muted-foreground hover:text-primary transition-colors flex items-center gap-1">
                  <Activity className="w-3 h-3" /> View Job History
                </Link>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => setOpen(a)} className="gap-1.5 h-8 text-xs">
                    <Terminal className="h-3.5 w-3.5" /> Full Log
                  </Button>
                  <Button variant="secondary" size="sm" className="gap-1.5 h-8 text-xs bg-primary/10 text-primary hover:bg-primary/20 hover:text-primary border border-primary/20" onClick={() => toast.success("Agent sequence triggered")}>
                    <Play className="h-3 w-3" /> Run
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={!!open} onOpenChange={(o) => !o && setOpen(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Terminal className="h-4 w-4 text-primary" />
              {open?.name} — Full Log
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="h-[400px] rounded-md border border-border bg-zinc-100 dark:bg-black/95 p-3">
            <pre className="font-mono text-[11px] leading-relaxed">
              {open?.log?.length ? open.log.map((line, i) => (
                <div
                  key={i}
                  className={
                    line.toLowerCase().includes("error") || line.toLowerCase().includes("fail")
                      ? "text-rose-600 dark:text-rose-400"
                      : "text-emerald-600 dark:text-emerald-400"
                  }
                >
                  {line}
                </div>
              )) : (
                <div className="text-muted-foreground">No logs available for this agent session.</div>
              )}
            </pre>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </>
  );
}
