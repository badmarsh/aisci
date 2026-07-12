import { createFileRoute, Link, useSearch } from "@tanstack/react-router";
import { useSuspenseQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchEvidence, updateEvidence, requestReview } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { FileText, ChevronDown, ChevronUp, Clock, BookOpen, Sigma, CheckCircle2, ListChecks, Send, Microscope, ShieldCheck, AlertTriangle } from "lucide-react";
import { Suspense, useState, Fragment, useEffect } from "react";
import { TableSkeleton } from "@/components/dashboard/SkeletonLoader";
import { cn } from "@/lib/utils";
import { QueryErrorBoundary } from "@/components/QueryErrorBoundary";
import ReactMarkdown from "react-markdown";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/projects/$projectId/evidence")({
  component: EvidencePage,
});

function EvidencePage() {
  const { projectId } = Route.useParams();
  
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [nextGateFilter, setNextGateFilter] = useState<string>("");
  const [runFilter, setRunFilter] = useState<string>("");

  return (
    <PageShell>
      <section className="mb-6 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Science Ledger</h1>
          <p className="text-muted-foreground mt-2">
            Evidence ledger claims for project: {projectId}
          </p>
        </div>
        <Link
          to="/projects/$projectId/literature"
          params={{ projectId }}
          className="inline-flex items-center justify-center whitespace-nowrap text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border border-input bg-background hover:bg-secondary hover:text-foreground h-9 px-4 py-2 rounded-md gap-2 shadow-sm"
        >
          <BookOpen className="w-4 h-4" />
          Literature Radar
        </Link>
      </section>

      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setStatusFilter(null)}
            className={cn(
              "px-3 py-1 rounded text-sm transition-colors border",
              !statusFilter
                ? "bg-primary text-primary-foreground border-primary font-medium"
                : "bg-secondary text-muted-foreground border-transparent hover:bg-secondary/80"
            )}
          >
            All Statuses
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
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Filter by Next Gate..."
            value={nextGateFilter}
            onChange={(e) => setNextGateFilter(e.target.value)}
            className="px-3 py-1 bg-secondary text-sm border-transparent rounded focus:outline-none focus:ring-1 focus:ring-primary"
          />
          <input
            type="text"
            placeholder="Filter by Run ID..."
            value={runFilter}
            onChange={(e) => setRunFilter(e.target.value)}
            className="px-3 py-1 bg-secondary text-sm border-transparent rounded focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>

      <QueryErrorBoundary>
        <Suspense fallback={<TableSkeleton rows={5} cols={4} />}>
          <EvidenceContent
            projectId={projectId}
            statusFilter={statusFilter}
            nextGateFilter={nextGateFilter}
            runFilter={runFilter}
          />
        </Suspense>
      </QueryErrorBoundary>
    </PageShell>
  );
}

function getStatusStyle(status: string) {
  const s = status.toLowerCase();
  if (s.includes("supported") || s.includes("validated") || s.includes("bulletproof")) return "bg-emerald-brand/10 text-emerald-brand border-emerald-brand/20";
  if (s.includes("sanity checked")) return "bg-amber-brand/10 text-amber-brand border-amber-brand/20";
  if (s.includes("tension") || s.includes("rejected")) return "bg-red-500/10 text-red-500 border-red-500/20";
  return "bg-secondary text-muted-foreground border-border";
}

function EvidenceContent({
  projectId,
  statusFilter,
  nextGateFilter,
  runFilter,
}: {
  projectId: string;
  statusFilter: string | null;
  nextGateFilter: string;
  runFilter: string;
}) {
  const queryClient = useQueryClient();
  const searchParams = useSearch({ strict: false });
  const [searchQuery, setSearchQuery] = useState((searchParams as any).q || "");

  const { data: evidence } = useSuspenseQuery({
    queryKey: ["evidence", projectId],
    queryFn: () => fetchEvidence(projectId),
  });
  
  const { mutate: updateStatus } = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => updateEvidence(projectId, id, status),
    onSuccess: () => {
      toast.success("Claim status updated");
      queryClient.invalidateQueries({ queryKey: ["evidence", projectId] });
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to update status");
    },
  });

  const { mutate: bulkRequestReview, isPending: isRequestingReview } = useMutation({
    mutationFn: async (ids: number[]) => {
      await Promise.all(ids.map(id => requestReview(projectId, id.toString(), "Review", "evidence")));
    },
    onSuccess: () => {
      toast.success("Review requested for selected claims");
      setSelectedClaims(new Set());
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to request review");
    }
  });

  const [expandedRow, setExpandedRow] = useState<number | null>(null);
  const [selectedClaims, setSelectedClaims] = useState<Set<number>>(new Set());

  const filteredEvidence = (evidence || []).filter((e: any) => {
    if (statusFilter && e.status !== statusFilter) return false;
    if (nextGateFilter && !e.nextGate?.toLowerCase().includes(nextGateFilter.toLowerCase())) return false;
    if (runFilter) {
        const matchesRun = e.run?.toLowerCase().includes(runFilter.toLowerCase());
        const matchesRunId = e.run_id?.toLowerCase().includes(runFilter.toLowerCase());
        if (!matchesRun && !matchesRunId) return false;
    }
    if (searchQuery && !e.claim.toLowerCase().includes(searchQuery.toLowerCase()) && !e.narrative.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const toggleSelection = (id: number, ev: React.MouseEvent) => {
    ev.stopPropagation();
    const newSet = new Set(selectedClaims);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setSelectedClaims(newSet);
  };

  const selectAll = () => {
    if (selectedClaims.size === filteredEvidence.length) {
      setSelectedClaims(new Set());
    } else {
      setSelectedClaims(new Set(filteredEvidence.map((e: any) => e.id)));
    }
  };

  return (
    <section className="glass-card rounded-xl p-6">
      <header className="flex items-center justify-between gap-3 mb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <FileText className="h-4 w-4" />
          </div>
          <h2 className="text-lg font-semibold">Ledger</h2>
        </div>
        
        <div className="flex items-center gap-3">
          {selectedClaims.size > 0 && (
            <div className="flex items-center gap-2 mr-2 bg-primary/5 pl-3 pr-1 py-1 rounded-md border border-primary/20">
              <span className="text-xs font-medium text-primary">{selectedClaims.size} selected</span>
              <Button 
                size="sm" 
                variant="default" 
                className="h-7 text-xs gap-1.5"
                onClick={() => bulkRequestReview(Array.from(selectedClaims))}
                disabled={isRequestingReview}
              >
                <Send className="w-3 h-3" />
                {isRequestingReview ? "Requesting..." : "Request Review"}
              </Button>
            </div>
          )}
          
          <input
            type="text"
            placeholder="Search claims or narrative..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-48 lg:w-64 px-3 py-1.5 border border-border rounded-md bg-secondary/50 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all"
          />
        </div>
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
                <th className="px-4 py-3 w-8">
                  <input 
                    type="checkbox" 
                    checked={selectedClaims.size > 0 && selectedClaims.size === filteredEvidence.length}
                    onChange={selectAll}
                    className="rounded border-border bg-background cursor-pointer"
                  />
                </th>
                <th className="px-4 py-3 w-8"></th>
                <th className="px-4 py-3">Claim & Type</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredEvidence.map((e: any, i: number) => {
                const isExpanded = expandedRow === i;
                const isLiterature = e.nextGate?.toLowerCase().includes("literature");
                
                return (
                  <Fragment key={i}>
                    <tr
                      className={cn("hover:bg-muted/30 cursor-pointer transition-colors", isExpanded && "bg-muted/10")}
                      onClick={() => setExpandedRow(isExpanded ? null : i)}
                    >
                      <td className="px-4 py-3" onClick={ev => ev.stopPropagation()}>
                        <input 
                          type="checkbox" 
                          checked={selectedClaims.has(e.id)}
                          onChange={(ev) => {
                            const newSet = new Set(selectedClaims);
                            if (newSet.has(e.id)) newSet.delete(e.id);
                            else newSet.add(e.id);
                            setSelectedClaims(newSet);
                          }}
                          className="rounded border-border bg-background cursor-pointer"
                        />
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-medium text-foreground mb-1">{e.claim}</div>
                        <div className="flex items-center gap-2">
                           <span className="text-[10px] font-mono text-muted-foreground bg-secondary px-1.5 py-0.5 rounded flex items-center gap-1 w-fit">
                             {isLiterature ? <BookOpen className="w-3 h-3 text-violet-400" /> : <Microscope className="w-3 h-3 text-emerald-400" />}
                             {isLiterature ? "Literature Finding" : "Computational Result"}
                           </span>
                           {e.nextGate && (
                             <span className="text-[10px] text-muted-foreground">Gate: {e.nextGate}</span>
                           )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={cn(
                            "px-2 py-1 rounded text-[10px] font-mono uppercase whitespace-nowrap border",
                            getStatusStyle(e.status)
                          )}
                        >
                          {e.status}
                        </span>
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr className="bg-secondary/5">
                        <td colSpan={4} className="p-0 border-b border-primary/10">
                          <div className="p-6 pl-16">
                            
                            <div className="mb-6 bg-background/50 p-4 rounded-md border border-border shadow-sm">
                              <h4 className="text-sm font-semibold mb-2 flex items-center gap-2 text-foreground">
                                <FileText className="w-4 h-4 text-primary" />
                                Narrative Context
                              </h4>
                              <div className="text-sm text-muted-foreground prose prose-sm dark:prose-invert max-w-none">
                                <ReactMarkdown>{e.narrative}</ReactMarkdown>
                              </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-2">
                              <div>
                                <h4 className="text-sm font-semibold mb-3 flex items-center gap-2 text-foreground">
                                  <Sigma className="w-4 h-4 text-primary" />
                                  Provenance & Linkages
                                </h4>
                                <div className="space-y-3 bg-background/50 p-4 rounded-md border border-border">
                                  <p className="text-sm text-muted-foreground flex flex-wrap items-center gap-2">
                                    <span className="font-medium min-w-24">Validating Run:</span>
                                    {e.run ? <span className="font-mono text-xs bg-secondary px-1.5 py-0.5 rounded border border-border">{e.run}</span> : <span className="text-xs italic">None</span>}
                                    {e.run_id && (
                                      <Link to="/projects/$projectId/fits" params={{ projectId }} className="text-xs bg-blue-500/10 text-blue-500 hover:text-blue-400 hover:bg-blue-500/20 px-1.5 py-0.5 rounded border border-blue-500/20 transition-colors">
                                        ID: {e.run_id}
                                      </Link>
                                    )}
                                  </p>
                                  <p className="text-sm text-muted-foreground flex flex-wrap items-center gap-2">
                                    <span className="font-medium min-w-24">Literature:</span>
                                    <Link to="/projects/$projectId/literature" params={{ projectId }} search={{ q: "bridge" }} className="text-xs bg-violet-500/10 text-violet-400 hover:text-violet-300 hover:bg-violet-500/20 px-1.5 py-0.5 rounded border border-violet-500/20 transition-colors flex items-center gap-1">
                                      <BookOpen className="w-3 h-3" /> View Sources
                                    </Link>
                                  </p>
                                </div>

                                <h4 className="text-sm font-semibold mt-6 mb-3 flex items-center gap-2 text-foreground">
                                  <ListChecks className="w-4 h-4 text-primary" />
                                  Quick Actions
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                  <button 
                                    onClick={(ev) => { ev.stopPropagation(); updateStatus({ id: e.id, status: "Supported" }); }} 
                                    disabled={e.status === "Supported"}
                                    className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-emerald-brand/10 text-emerald-brand border border-emerald-brand/20 hover:bg-emerald-brand/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    <CheckCircle2 className="w-3.5 h-3.5" /> 
                                    Mark Supported
                                  </button>
                                  <button 
                                    onClick={(ev) => { ev.stopPropagation(); updateStatus({ id: e.id, status: "Sanity Checked" }); }} 
                                    disabled={e.status === "Sanity Checked"}
                                    className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-amber-brand/10 text-amber-brand border border-amber-brand/20 hover:bg-amber-brand/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    <ShieldCheck className="w-3.5 h-3.5" /> 
                                    Mark Sanity Checked
                                  </button>
                                  <button 
                                    onClick={(ev) => { ev.stopPropagation(); updateStatus({ id: e.id, status: "Tension" }); }} 
                                    disabled={e.status === "Tension"}
                                    className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    <AlertTriangle className="w-3.5 h-3.5" /> 
                                    Mark Tension
                                  </button>
                                </div>
                              </div>

                              <div>
                                <h4 className="text-sm font-semibold mb-3 flex items-center gap-2 text-foreground">
                                  <Clock className="w-4 h-4 text-primary" />
                                  Audit Timeline
                                </h4>
                                <div className="bg-background/50 p-4 rounded-md border border-border h-[calc(100%-2rem)]">
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
                                    <p className="text-sm text-muted-foreground italic flex flex-col items-center justify-center h-full gap-2 opacity-50">
                                      <Clock className="w-6 h-6" />
                                      No audit history available.
                                    </p>
                                  )}
                                </div>
                              </div>
                            </div>
                            
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
  );
}


