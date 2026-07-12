import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { fetchEvidence } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { FileText, ChevronDown, ChevronUp, Clock } from "lucide-react";
import { Suspense, useState, Fragment } from "react";
import { TableSkeleton } from "@/components/dashboard/SkeletonLoader";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/projects/$projectId/evidence")({
  component: EvidencePage,
});

function EvidencePage() {
  const { projectId } = Route.useParams();
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  return (
    <PageShell>
      <section className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight">Science Ledger</h1>
        <p className="text-muted-foreground mt-2">
          Evidence ledger claims for project: {projectId}
        </p>
      </section>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setStatusFilter(null)}
          className={cn(
            "px-3 py-1 rounded text-sm transition-colors border",
            !statusFilter
              ? "bg-primary text-primary-foreground border-primary font-medium"
              : "bg-secondary text-muted-foreground border-transparent hover:bg-secondary/80"
          )}
        >
          All
        </button>
        {["Supported", "Sanity Checked", "Proposed"].map((status) => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={cn(
              "px-3 py-1 rounded text-sm transition-colors border",
              statusFilter === status
                ? "bg-primary text-primary-foreground border-primary font-medium"
                : "bg-secondary text-muted-foreground border-transparent hover:bg-secondary/80"
            )}
          >
            {status}
          </button>
        ))}
      </div>

      <Suspense fallback={<TableSkeleton rows={5} cols={3} />}>
        <EvidenceContent projectId={projectId} statusFilter={statusFilter} />
      </Suspense>
    </PageShell>
  );
}

function EvidenceContent({
  projectId,
  statusFilter,
}: {
  projectId: string;
  statusFilter: string | null;
}) {
  const { data: evidence } = useSuspenseQuery({
    queryKey: ["evidence", projectId],
    queryFn: () => fetchEvidence(projectId),
  });
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const filteredEvidence = statusFilter
    ? (evidence || []).filter((e: any) => e.status === statusFilter)
    : (evidence || []);

  return (
    <section className="glass-card rounded-xl p-6">
      <header className="flex items-center gap-3 mb-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
          <FileText className="h-4 w-4" />
        </div>
        <h2 className="text-lg font-semibold">Ledger</h2>
      </header>

      {!filteredEvidence.length ? (
        <div className="py-8 text-center text-muted-foreground">
          No claims matching the filter found.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="border-b border-border bg-secondary/30">
              <tr>
                <th className="px-4 py-3 w-8"></th>
                <th className="px-4 py-3">Claim</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Narrative</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredEvidence.map((e: any, i: number) => (
                <Fragment key={i}>
                  <tr 
                    className="hover:bg-muted/30 cursor-pointer"
                    onClick={() => setExpandedRow(expandedRow === i ? null : i)}
                  >
                    <td className="px-4 py-3 text-muted-foreground">
                      {expandedRow === i ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </td>
                    <td className="px-4 py-3 font-medium">{e.claim}</td>
                    <td className="px-4 py-3">
                      <span
                        className={cn(
                          "px-2 py-1 rounded text-[10px] font-mono uppercase whitespace-nowrap",
                          e.status === "Supported"
                            ? "bg-emerald-brand/10 text-emerald-brand border border-emerald-brand/20"
                            : e.status === "Sanity Checked"
                              ? "bg-amber-brand/10 text-amber-brand border border-amber-brand/20"
                              : "bg-secondary text-muted-foreground border border-border"
                        )}
                      >
                        {e.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{e.narrative}</td>
                  </tr>
                  {expandedRow === i && (
                    <tr className="bg-secondary/10">
                      <td colSpan={4} className="p-0">
                        <div className="p-4 pl-12 border-b border-border">
                          <div className="mb-6">
                            <h4 className="text-sm font-semibold mb-2 flex items-center gap-2 text-foreground">
                              <FileText className="w-4 h-4 text-primary" />
                              Provenance
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              Validated in run: {e.run ? <span className="font-mono text-xs bg-secondary px-1.5 py-0.5 rounded border border-border">{e.run}</span> : "None"}
                            </p>
                          </div>
                          <h4 className="text-sm font-semibold mb-4 flex items-center gap-2 text-foreground">
                            <Clock className="w-4 h-4 text-primary" /> 
                            Audit Timeline
                          </h4>
                          {e.status_history?.length > 0 ? (
                            <div className="space-y-4 pl-3 border-l-2 border-primary/20">
                              {e.status_history.map((hist: any, hIdx: number) => (
                                <div key={hIdx} className="relative pl-5">
                                  <div className="absolute w-2.5 h-2.5 rounded-full bg-background border-2 border-primary -left-[6px] top-1.5" />
                                  <div className="flex flex-col">
                                    <div className="flex items-center gap-2 text-sm font-medium">
                                      <span className="text-muted-foreground">{hist.from}</span>
                                      <span className="text-primary">→</span>
                                      <span>{hist.to}</span>
                                    </div>
                                    <div className="text-xs text-muted-foreground mt-0.5">
                                      {new Date(hist.timestamp).toLocaleString()} • by {hist.reviewer}
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-sm text-muted-foreground italic">No audit history available.</p>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

