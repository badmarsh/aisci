import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchFits, triggerPipeline } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { Sigma, Play, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Suspense, useState, Fragment } from "react";
import { TableSkeleton } from "@/components/dashboard/SkeletonLoader";
import { CorrelationHeatmap } from "@/components/dashboard/CorrelationHeatmap";
import { QueryErrorBoundary } from "@/components/QueryErrorBoundary";

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
  const { data: fitsData } = useSuspenseQuery({
    queryKey: ["fits", projectId],
    queryFn: () => fetchFits(projectId),
  });

  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  return (
    <>
      <p className="text-sm font-mono text-emerald-brand mb-4">
        Run ID: {fitsData?.runId || "unknown"}
      </p>

      <section className="glass-card rounded-xl p-6">
        <header className="flex items-center gap-3 mb-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <Sigma className="h-4 w-4" />
          </div>
          <h2 className="text-lg font-semibold">Fit Results</h2>
        </header>

        <div className="mb-4 p-4 bg-amber-500/10 border border-amber-500/20 text-amber-500 rounded-lg">
          Jacobian Correction Required
        </div>

        <div className="flex gap-2 mb-4">
          <button className="px-3 py-1 rounded bg-secondary text-sm">Jüttner/Boltzmann 1c</button>
        </div>

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
                  <th className="px-4 py-3 font-medium text-muted-foreground">χ²/ndf</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">AIC</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">BIC</th>
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
                              row.status === "Clean Fit"
                                ? "bg-emerald-brand/10 text-emerald-brand border border-emerald-brand/20"
                                : row.status === "Converged"
                                  ? "bg-amber-brand/10 text-amber-brand border border-amber-brand/20"
                                  : "bg-rose-brand/10 text-rose-brand border border-rose-brand/20",
                            )}
                          >
                            {row.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-mono text-xs">{row.chi2 ?? "—"}</td>
                        <td className="px-4 py-3 font-mono text-xs">{row.aic ?? "—"}</td>
                        <td className="px-4 py-3 font-mono text-xs">{row.bic ?? "—"}</td>
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
                                <span className="text-[10px] text-muted-foreground uppercase">
                                  Fit Quality: {row.quality || "UNKNOWN"}
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

