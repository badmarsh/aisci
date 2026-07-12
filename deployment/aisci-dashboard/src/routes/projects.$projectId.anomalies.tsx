import { createFileRoute, Link } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { fetchAnomalies } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { AlertTriangle, CheckCircle, XCircle, ExternalLink, Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import { Suspense, useState } from "react";
import { TableSkeleton } from "@/components/dashboard/SkeletonLoader";
import { QueryErrorBoundary } from "@/components/QueryErrorBoundary";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export const Route = createFileRoute("/projects/$projectId/anomalies")({
  component: AnomaliesPage,
});

function AnomaliesPage() {
  const { projectId } = Route.useParams();

  return (
    <PageShell>
      <section className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Anomalies</h1>
          <p className="text-muted-foreground mt-2">
            Detected physics anomalies for project: {projectId}
          </p>
        </div>
      </section>

      <QueryErrorBoundary>
        <Suspense fallback={<TableSkeleton rows={4} cols={3} />}>
          <AnomaliesContent projectId={projectId} />
        </Suspense>
      </QueryErrorBoundary>
    </PageShell>
  );
}

function AnomaliesContent({ projectId }: { projectId: string }) {
  const { data: anomalies } = useSuspenseQuery({
    queryKey: ["anomalies", projectId],
    queryFn: () => fetchAnomalies(projectId),
  });

  const [triageState, setTriageState] = useState<Record<string, "acknowledged" | "ignored" | "pending">>({});

  const handleTriage = (id: string, action: "acknowledged" | "ignored") => {
    setTriageState(prev => ({ ...prev, [id]: action }));
    toast.success(`Anomaly marked as ${action}`);
  };

  return (
    <section className="glass-card rounded-xl p-6">
      <header className="flex items-center gap-3 mb-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-destructive/10 text-destructive">
          <AlertTriangle className="h-4 w-4" />
        </div>
        <h2 className="text-lg font-semibold">Anomaly Triage Queue</h2>
      </header>

      {!anomalies?.length ? (
        <div className="py-12 text-center text-muted-foreground flex flex-col items-center">
          <CheckCircle className="w-8 h-8 mb-3 text-emerald-500/50" />
          <p>No anomalies detected. Fits are stable.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {anomalies.map((a: any, i: number) => {
            const anomalyId = `${a.bin}-${a.model}-${i}`;
            const state = triageState[anomalyId] || "pending";
            
            return (
              <div 
                key={anomalyId} 
                className={cn(
                  "flex flex-col md:flex-row gap-4 p-5 border rounded-xl transition-all",
                  state === "pending" ? "bg-card border-border shadow-sm hover:border-primary/30" : 
                  state === "acknowledged" ? "bg-emerald-500/5 border-emerald-500/20 opacity-80" : 
                  "bg-muted/30 border-border/50 opacity-50 grayscale"
                )}
              >
                <div className="flex flex-col gap-2 shrink-0">
                  <div
                    className={cn(
                      "px-2.5 py-1 w-fit text-[10px] font-mono font-bold rounded uppercase tracking-wider",
                      a.severity === "high"
                        ? "bg-destructive text-destructive-foreground shadow-sm"
                        : "bg-amber-500/20 text-amber-500",
                    )}
                  >
                    {a.severity} SEV
                  </div>
                  {state !== "pending" && (
                    <div className={cn(
                      "text-[10px] font-mono uppercase px-2 py-0.5 rounded border w-fit",
                      state === "acknowledged" ? "text-emerald-500 border-emerald-500/20 bg-emerald-500/10" : "text-muted-foreground border-border bg-muted"
                    )}>
                      {state}
                    </div>
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <h3 className="font-semibold text-lg text-foreground tracking-tight">
                      {a.model} Fit Failure
                    </h3>
                    <span className="text-muted-foreground/30">•</span>
                    <span className="text-sm font-mono text-muted-foreground bg-secondary px-2 py-0.5 rounded">Bin: {a.bin}</span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3 leading-relaxed max-w-3xl">{a.message}</p>
                  
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="text-xs font-mono bg-secondary/50 px-2.5 py-1 rounded-md border border-border flex items-center gap-2">
                      <span className="text-muted-foreground uppercase text-[10px]">Type</span>
                      <span className="font-medium text-foreground">{a.type}</span>
                    </div>
                    <div className="text-xs font-mono bg-secondary/50 px-2.5 py-1 rounded-md border border-border flex items-center gap-2">
                      <span className="text-muted-foreground uppercase text-[10px]">Value</span>
                      <span className="font-medium text-rose-400">{a.value}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-row md:flex-col items-center justify-end gap-2 shrink-0 border-t md:border-t-0 md:border-l border-border pt-4 md:pt-0 md:pl-4 mt-2 md:mt-0">
                  <Link 
                    to="/projects/$projectId/fits" 
                    params={{ projectId }}
                    className="w-full"
                  >
                    <Button variant="outline" size="sm" className="w-full text-xs h-8 gap-1.5 shadow-sm">
                      <Activity className="w-3.5 h-3.5" /> Inspect Fit
                    </Button>
                  </Link>
                  
                  {state === "pending" ? (
                    <div className="flex md:flex-col gap-2 w-full">
                      <Button 
                        onClick={() => handleTriage(anomalyId, "acknowledged")} 
                        variant="secondary" 
                        size="sm" 
                        className="w-full text-xs h-8 gap-1.5 bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20 hover:text-emerald-600 border border-emerald-500/20 transition-colors"
                      >
                        <CheckCircle className="w-3.5 h-3.5" /> Acknowledge
                      </Button>
                      <Button 
                        onClick={() => handleTriage(anomalyId, "ignored")} 
                        variant="ghost" 
                        size="sm" 
                        className="w-full text-xs h-8 gap-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
                      >
                        <XCircle className="w-3.5 h-3.5" /> Ignore
                      </Button>
                    </div>
                  ) : (
                    <Button 
                      onClick={() => setTriageState(prev => { const n = {...prev}; delete n[anomalyId]; return n; })} 
                      variant="ghost" 
                      size="sm" 
                      className="w-full text-[10px] uppercase h-7 text-muted-foreground"
                    >
                      Undo Triage
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
