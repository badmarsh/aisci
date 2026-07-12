import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Terminal } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { PageShell } from "@/components/PageShell";
import { type Agent } from "@/lib/types";
import { useQuery } from "@tanstack/react-query";
import { fetchAgents } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

export const Route = createFileRoute("/agents")({
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

const statusStyles: Record<Agent["status"], string> = {
  ACTIVE: "bg-emerald-brand",
  IDLE: "bg-muted-foreground",
  WAITING: "bg-amber-brand",
};

function AgentsPage() {
  const [open, setOpen] = useState<Agent | null>(null);

  const {
    data: agents = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
  });

  if (isLoading) {
    return (
      <PageShell>
        <Skeleton className="h-[200px] w-full" />
      </PageShell>
    );
  }

  if (isError) {
    return (
      <PageShell>
        <div className="text-rose-brand">Error loading agents.</div>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-2">
        {agents.map((a: Agent) => (
          <Card key={a.name} className="glass-card fade-in-up transition hover:border-primary/40">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 text-base">
                  <span className="relative flex h-2 w-2">
                    {a.status === "ACTIVE" && (
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-brand opacity-60" />
                    )}
                    <span
                      className={`relative inline-flex h-2 w-2 rounded-full ${statusStyles[a.status]}`}
                    />
                  </span>
                  {a.name}
                </CardTitle>
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
              <p className="text-xs text-muted-foreground">
                Last run: <span className="font-mono">{a.last}</span>
              </p>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-xs text-foreground/80">{a.summary}</p>
              <div className="rounded-md border border-border bg-muted/50 p-2 font-mono text-[11px] leading-relaxed">
                {a.log.slice(0, 5).map((line, i) => (
                  <div key={i} className="truncate text-zinc-600 dark:text-zinc-400">
                    <span className="text-emerald-600/70 dark:text-emerald-500/70">›</span> {line}
                  </div>
                ))}
              </div>
              <div className="mt-3 flex justify-end">
                <Button variant="outline" size="sm" onClick={() => setOpen(a)} className="gap-1.5">
                  <Terminal className="h-3.5 w-3.5" /> View Full Log
                </Button>
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
              {open?.log.map((line, i) => (
                <div
                  key={i}
                  className={
                    line.toLowerCase().includes("error")
                      ? "text-rose-600 dark:text-rose-400"
                      : "text-emerald-600 dark:text-emerald-400"
                  }
                >
                  {line}
                </div>
              ))}
            </pre>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </PageShell>
  );
}
