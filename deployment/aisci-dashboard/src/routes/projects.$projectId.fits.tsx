import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchFits, triggerPipeline, fetchFitRuns, type FitRunMetadata } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import { PageShell } from "@/components/PageShell";
import { Sigma, Play, Loader2, Bot, Info, Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Suspense, useState, Fragment, useMemo } from "react";
import { TableSkeleton } from "@/components/dashboard/SkeletonLoader";
import { CorrelationHeatmap } from "@/components/dashboard/CorrelationHeatmap";
import { QueryErrorBoundary } from "@/components/QueryErrorBoundary";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";

export const Route = createFileRoute("/projects/$projectId/fits")({
  component: FitsPage,
});

function FitsPage() {
  const { projectId } = Route.useParams();
  const queryClient = useQueryClient();

  const { mutate: runFit, isPending: isRunningFit } = useMutation({
    mutationFn: () => triggerPipeline(projectId, "fit-validation"),
    onSuccess: () => {
      toast.success("Fitting pipeline triggered successfully");
      queryClient.invalidateQueries({ queryKey: ["fits", projectId] });
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to trigger fitting pipeline");
    },
  });

  return (
    <PageShell>
      <section className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Active Fits</h1>
          <p className="text-muted-foreground mt-2">
            Latest physics fit data for project: {projectId}
          </p>
        </div>
        <Button
          onClick={() => runFit()}
          disabled={isRunningFit}
          className="gap-2 bg-gradient-to-r from-primary to-primary/80 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-md shadow-primary/20"
        >
          {isRunningFit ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current" />}
          Run New Fit
        </Button>
      </section>

      <QueryErrorBoundary>
        <Suspense fallback={<TableSkeleton rows={5} cols={9} />}>
          <FitsContent projectId={projectId} />
        </Suspense>
      </QueryErrorBoundary>
    </PageShell>
  );
}

function FitsContent({ projectId }: { projectId: string }) {
  const [selectedRun, setSelectedRun] = useState<string>("");
  const [compareRun, setCompareRun] = useState<string>("");

  const { data: runsData } = useSuspenseQuery({
    queryKey: ["fitRuns", projectId],
    queryFn: () => fetchFitRuns(projectId),
  });

  const { data: fitsData } = useSuspenseQuery({
    queryKey: ["fits", projectId, selectedRun, compareRun],
    queryFn: () => fetchFits(projectId, selectedRun || undefined, compareRun || undefined),
  });

  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  // Merge chi2Series and compareSeries for Recharts
  const mergedChartData = useMemo(() => {
    if (!fitsData?.chi2Series) return [];
    if (!fitsData.compareSeries) return fitsData.chi2Series;
    
    return fitsData.chi2Series.map((row, i) => {
      const compRow = fitsData.compareSeries?.[i] || {};
      const merged: Record<string, any> = { ...row };
      Object.keys(compRow).forEach(k => {
        if (k !== "bin" && k !== "name") {
          merged[`${k}_compare`] = compRow[k];
        }
      });
      return merged;
    });
  }, [fitsData]);

  return (
    <>
      <div className="flex flex-col xl:flex-row gap-4 mb-6 p-4 rounded-xl glass-card border border-border items-start xl:items-center">
        <div className="flex gap-2 items-center shrink-0">
          <span className="text-sm font-medium text-muted-foreground w-24">Primary Run:</span>
          <Select value={selectedRun || fitsData?.runId || ""} onValueChange={setSelectedRun}>
            <SelectTrigger className="w-[300px] bg-background/50">
              <SelectValue placeholder="Select a run" />
            </SelectTrigger>
            <SelectContent>
              {runsData?.runs?.map((run: FitRunMetadata) => (
                <SelectItem key={run.id} value={run.id}>
                  {run.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div className="flex gap-2 items-center shrink-0">
          <span className="text-sm font-medium text-muted-foreground w-24 xl:text-right xl:w-auto">Compare:</span>
          <Select value={compareRun} onValueChange={setCompareRun}>
            <SelectTrigger className="w-[300px] bg-background/50">
              <SelectValue placeholder="None (Select to compare)" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">None</SelectItem>
              {runsData?.runs?.map((run: FitRunMetadata) => (
                <SelectItem key={run.id} value={run.id}>
                  {run.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {(() => {
        const currentRun = runsData?.runs?.find(r => r.id === (selectedRun || fitsData?.runId));
        if (!currentRun || (!currentRun.summary && !currentRun.references && !currentRun.interpretation)) return null;
        return (
          <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            {currentRun.interpretation && (
              <div className="p-5 rounded-xl bg-violet-500/5 border border-violet-500/20 shadow-sm relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/10 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none" />
                <h3 className="text-sm font-semibold mb-3 text-violet-500 flex items-center gap-2">
                  <Bot className="w-4 h-4" /> 🤖 Robert says:
                </h3>
                <div className="text-sm text-foreground/90 prose prose-sm dark:prose-invert max-w-none prose-p:leading-relaxed">
                  <ReactMarkdown>{currentRun.interpretation}</ReactMarkdown>
                </div>
              </div>
            )}
            
            <div className="flex flex-col gap-4">
              {currentRun.summary && (
                <div className="p-5 rounded-xl bg-secondary/20 border border-border shadow-sm flex-1">
                  <h3 className="text-sm font-semibold mb-2 text-foreground flex items-center gap-2">
                    <Info className="w-4 h-4 text-primary" /> Run Summary
                  </h3>
                  <div className="text-sm text-muted-foreground prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{currentRun.summary}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      })()}

      <section className="glass-card rounded-xl p-6 mb-6">
        <header className="flex items-center gap-3 mb-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <Activity className="h-4 w-4" />
          </div>
          <h2 className="text-lg font-semibold">χ² / ndf Over Centrality</h2>
        </header>

        {mergedChartData.length > 0 ? (
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mergedChartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "rgba(10, 10, 10, 0.9)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px" }}
                  itemStyle={{ fontSize: "12px" }}
                  labelStyle={{ fontSize: "12px", color: "#888", marginBottom: "4px" }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: "12px" }} />
                
                {Object.keys(mergedChartData[0] || {}).filter(k => k !== "name" && k !== "bin" && !k.endsWith("_compare")).map((key, i) => {
                  const colors = ["#10b981", "#3b82f6", "#f59e0b", "#ec4899", "#8b5cf6"];
                  const color = colors[i % colors.length];
                  
                  return (
                    <Fragment key={key}>
                      <Line type="monotone" dataKey={key} stroke={color} strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
                      {compareRun && (
                        <Line type="monotone" dataKey={`${key}_compare`} name={`${key} (Compare)`} stroke={color} strokeWidth={2} strokeDasharray="5 5" dot={{ r: 3 }} />
                      )}
                    </Fragment>
                  );
                })}
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="py-12 text-center text-muted-foreground flex flex-col items-center">
            <Activity className="w-8 h-8 mb-3 opacity-20" />
            <p>No sequence data available for chart.</p>
          </div>
        )}
      </section>

      <section className="glass-card rounded-xl p-6">
        <header className="flex items-center gap-3 mb-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <Sigma className="h-4 w-4" />
          </div>
          <h2 className="text-lg font-semibold">Fit Matrix</h2>
        </header>

        {!fitsData?.fitRows?.length ? (
          <div className="py-8 text-center text-muted-foreground">
            No fits available for this project.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="border-b border-border bg-secondary/30">
                <tr>
                  <th className="px-4 py-3 font-medium text-muted-foreground">Bin</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">Model</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">Status</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">Seed Index</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">χ²/ndf</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">AIC / BIC</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">T (GeV)</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">β / U</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground text-right">Telemetry</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {fitsData.fitRows.map((row: any, i: number) => {
                  const rowKey = `${row.bin}|${row.model}`;
                  const isExpanded = expandedRow === rowKey;
                  return (
                    <Fragment key={i}>
                      <tr className="hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3 font-mono text-xs">{row.bin}</td>
                        <td className="px-4 py-3 font-medium">{row.model}</td>
                        <td className="px-4 py-3">
                          <span
                            className={cn(
                              "px-2 py-1 rounded text-[10px] font-mono uppercase",
                              row.status === "Clean Fit" || row.status === "OK"
                                ? "bg-emerald-brand/10 text-emerald-brand border border-emerald-brand/20"
                                : row.status === "Converged"
                                  ? "bg-amber-brand/10 text-amber-brand border border-amber-brand/20"
                                  : "bg-rose-brand/10 text-rose-brand border border-rose-brand/20",
                            )}
                          >
                            {row.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-mono text-xs">{row.seedIndex ?? "—"}</td>
                        <td className="px-4 py-3 font-mono text-xs text-primary">{row.chi2 ?? "—"}</td>
                        <td className="px-4 py-3 font-mono text-xs">
                          {row.aic ?? "—"} <span className="text-muted-foreground/50">/</span> {row.bic ?? "—"}
                        </td>
                        <td className="px-4 py-3 font-mono text-xs">{row.T}</td>
                        <td className="px-4 py-3 font-mono text-xs">{row.beta}</td>
                        <td className="px-4 py-3 text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            className={cn(
                              "h-7 px-2.5 font-mono text-[10px] uppercase border transition-all",
                              isExpanded
                                ? "bg-primary text-primary-foreground border-primary font-medium"
                                : "bg-transparent text-muted-foreground border-border hover:text-foreground hover:bg-secondary/40"
                            )}
                            onClick={() => setExpandedRow(isExpanded ? null : rowKey)}
                          >
                            {isExpanded ? "Hide Matrix" : "Correlations"}
                          </Button>
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr>
                          <td colSpan={9} className="px-6 py-4 bg-secondary/5 border-l-2 border-primary">
                            <div className="flex flex-col gap-3">
                              <div className="flex justify-between items-center">
                                <h4 className="text-xs font-semibold flex items-center gap-1.5 text-foreground uppercase tracking-wider">
                                  <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                                  Correlation Matrix ({row.model} — Bin: {row.bin})
                                </h4>
                                <span className="text-[10px] text-muted-foreground uppercase bg-secondary px-2 py-0.5 rounded border border-border">
                                  Fit Quality: <span className={row.quality === "GOOD" || row.quality === "OK" ? "text-emerald-500" : row.quality === "POOR" ? "text-rose-500" : "text-amber-500"}>{row.quality || "UNKNOWN"}</span>
                                </span>
                              </div>
                              <CorrelationHeatmap correlations={row.correlations || {}} />
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}

