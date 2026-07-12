import { createFileRoute, Link } from "@tanstack/react-router";
import { useSuspenseQuery, useQuery } from "@tanstack/react-query";
import { fetchLiterature, fetchSciteTally } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { BookOpen, Download, Link as LinkIcon, ExternalLink, ChevronDown, ChevronUp, Search, Filter, Box, Network, Send } from "lucide-react";
import { Suspense, useState, Fragment, useMemo } from "react";
import { TableSkeleton } from "@/components/dashboard/SkeletonLoader";
import { QueryErrorBoundary } from "@/components/QueryErrorBoundary";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/projects/$projectId/literature")({
  component: LiteraturePage,
});

function LiteraturePage() {
  const { projectId } = Route.useParams();

  return (
    <PageShell>
      <section className="mb-6 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Literature Radar</h1>
          <p className="text-muted-foreground mt-2">Ingested papers for project: {projectId}</p>
        </div>
        <a
          href={`http://localhost:8001/api/projects/${projectId}/export/bibtex`}
          download="bibliography.bib"
          className="inline-flex items-center justify-center whitespace-nowrap text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border border-input bg-background hover:bg-secondary hover:text-foreground h-9 px-4 py-2 rounded-md gap-2 shadow-sm"
        >
          <Download className="w-4 h-4" />
          Export BibTeX
        </a>
      </section>

      <QueryErrorBoundary>
        <Suspense fallback={<TableSkeleton rows={5} cols={4} />}>
          <LiteratureContent projectId={projectId} />
        </Suspense>
      </QueryErrorBoundary>
    </PageShell>
  );
}

function SciteBadge({ projectId, doi }: { projectId: string; doi: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["scite", projectId, doi],
    queryFn: () => fetchSciteTally(projectId, doi),
    staleTime: 1000 * 60 * 60,
  });

  if (isLoading) return <span className="px-2 py-0.5 rounded text-[10px] bg-secondary/50 text-muted-foreground animate-pulse">scite loading</span>;

  if (error || data?.status !== "ok" || !data?.tally) {
    return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-secondary text-muted-foreground border border-border">scite N/A</span>;
  }

  const t = data.tally;
  return (
    <div className="flex items-center gap-1 text-[10px] font-mono group relative">
      <span className="text-muted-foreground mr-1">scite:</span>
      {t.supporting > 0 && <span className="bg-emerald-500/10 text-emerald-500 px-1 rounded border border-emerald-500/20" title="Supporting">{t.supporting} S</span>}
      {t.contradicting > 0 && <span className="bg-red-500/10 text-red-500 px-1 rounded border border-red-500/20" title="Contradicting">{t.contradicting} C</span>}
      <span className="bg-secondary text-muted-foreground px-1 rounded border border-border" title="Mentioning">{t.mentioning || 0} M</span>
      <div className="absolute bottom-full mb-1 hidden group-hover:block w-48 p-2 bg-popover text-popover-foreground border border-border rounded shadow-lg text-[10px] leading-tight z-50">
        Requires SCITE_API_KEY. Tallies citations only; does not provide contextual reasoning.
      </div>
    </div>
  );
}

function getConfidenceColor(conf: string) {
  const c = conf.toLowerCase();
  if (c === "high") return "bg-emerald-500/10 text-emerald-500 border-emerald-500/20";
  if (c === "medium") return "bg-amber-500/10 text-amber-500 border-amber-500/20";
  return "bg-secondary text-muted-foreground border-border";
}

function LiteratureContent({ projectId }: { projectId: string }) {
  const { data: literature } = useSuspenseQuery({
    queryKey: ["literature", projectId],
    queryFn: () => fetchLiterature(projectId),
  });

  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [bridgeFilter, setBridgeFilter] = useState(false);
  const [confidenceFilter, setConfidenceFilter] = useState("All");
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const categories = useMemo(() => {
    const cats = new Set((literature || []).map((p: any) => p.category));
    return ["All", ...Array.from(cats)].sort();
  }, [literature]);

  const filteredLiterature = (literature || []).filter((p: any) => {
    if (searchQuery && !p.title.toLowerCase().includes(searchQuery.toLowerCase()) && !p.abstract.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    if (categoryFilter !== "All" && p.category !== categoryFilter) return false;
    if (bridgeFilter && !p.bridge) return false;
    if (confidenceFilter !== "All") {
      const hasConfidence = p.claimList?.some((c: any) => c.confidence.toLowerCase() === confidenceFilter.toLowerCase());
      if (!hasConfidence) return false;
    }
    return true;
  });

  const totalCount = literature?.length ?? 0;
  const arxivCount = literature?.filter((p: any) => p.source === "arXiv").length ?? 0;
  const openalexCount = literature?.filter((p: any) => p.source === "OpenAlex").length ?? 0;

  return (
    <>
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="glass-card p-4 rounded-xl flex flex-col gap-1">
          <span className="text-xs text-muted-foreground uppercase font-medium">Total Papers</span>
          <span className="text-2xl font-semibold font-mono">{totalCount}</span>
        </div>
        <div className="glass-card p-4 rounded-xl flex flex-col gap-1">
          <span className="text-xs text-muted-foreground uppercase font-medium">arXiv Sources</span>
          <span className="text-2xl font-semibold font-mono">{arxivCount}</span>
        </div>
        <div className="glass-card p-4 rounded-xl flex flex-col gap-1">
          <span className="text-xs text-muted-foreground uppercase font-medium">OpenAlex Sources</span>
          <span className="text-2xl font-semibold font-mono">{openalexCount}</span>
        </div>
      </div>

      <section className="glass-card rounded-xl p-6">
        <header className="flex items-center justify-between gap-3 mb-6">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
              <BookOpen className="h-4 w-4" />
            </div>
            <h2 className="text-lg font-semibold">Research Database</h2>
          </div>
          
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search title or abstract..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-48 lg:w-64 pl-8 pr-3 py-1.5 border border-border rounded-md bg-secondary/50 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all"
              />
            </div>
            <div className="flex items-center gap-2 border border-border rounded-md px-2 bg-secondary/50">
              <Filter className="w-3.5 h-3.5 text-muted-foreground" />
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="bg-transparent text-sm py-1.5 focus:outline-none cursor-pointer"
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat === "All" ? "All Categories" : cat}</option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2 border border-border rounded-md px-2 bg-secondary/50">
              <select
                value={confidenceFilter}
                onChange={(e) => setConfidenceFilter(e.target.value)}
                className="bg-transparent text-sm py-1.5 focus:outline-none cursor-pointer"
              >
                <option value="All">All Confidences</option>
                <option value="High">High Confidence</option>
                <option value="Medium">Medium Confidence</option>
                <option value="Low">Low Confidence</option>
              </select>
            </div>
            <label className="flex items-center gap-2 text-sm cursor-pointer border border-border rounded-md px-3 py-1.5 bg-secondary/50 hover:bg-secondary transition-colors">
              <input
                type="checkbox"
                checked={bridgeFilter}
                onChange={(e) => setBridgeFilter(e.target.checked)}
                className="rounded border-border bg-background"
              />
              Bridge only
            </label>
          </div>
        </header>

        <div className="overflow-x-auto">
          {!filteredLiterature.length ? (
            <div className="py-12 text-center text-muted-foreground flex flex-col items-center">
              <Search className="w-8 h-8 mb-3 opacity-20" />
              <p>No papers matching the filters found.</p>
            </div>
          ) : (
            <table className="w-full text-sm text-left border-collapse">
              <thead className="border-b border-border bg-secondary/30">
                <tr>
                  <th className="px-4 py-3 w-8"></th>
                  <th className="px-4 py-3">Title & Source</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3 text-center">Claims</th>
                  <th className="px-4 py-3">Scite Summary</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredLiterature.map((p: any, i: number) => {
                  const isExpanded = expandedRow === i;
                  return (
                    <Fragment key={i}>
                      <tr
                        className={cn("hover:bg-muted/30 cursor-pointer transition-colors", isExpanded && "bg-muted/10")}
                        onClick={() => setExpandedRow(isExpanded ? null : i)}
                      >
                        <td className="px-4 py-4 text-muted-foreground">
                          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex items-start gap-2 max-w-xl">
                            <Box className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                            <div>
                              <div className="font-medium text-foreground leading-tight mb-1">{p.title}</div>
                              <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground">
                                <span className="bg-secondary px-1.5 py-0.5 rounded uppercase">{p.source}</span>
                                {p.bridge && (
                                  <span className="bg-violet-500/10 text-violet-500 px-1.5 py-0.5 rounded border border-violet-500/20 flex items-center gap-1">
                                    <Network className="w-2.5 h-2.5" /> Interdisciplinary bridge
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4">
                          <span className="px-2 py-1 rounded text-[10px] font-mono uppercase bg-secondary/50 text-foreground border border-border">
                            {p.category}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-center">
                          <Badge variant="outline" className={cn("font-mono font-medium", p.claims > 0 ? "text-primary border-primary/30 bg-primary/5" : "text-muted-foreground opacity-50")}>
                            {p.claims}
                          </Badge>
                        </td>
                        <td className="px-4 py-4">
                          {p.id && (p.id.startsWith("10.") || p.id.startsWith("arXiv")) ? (
                            <SciteBadge projectId={projectId} doi={p.id} />
                          ) : (
                            <span className="text-muted-foreground text-xs">—</span>
                          )}
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr className="bg-secondary/5">
                          <td colSpan={5} className="p-0 border-b border-primary/10">
                            <div className="p-6 pl-12">
                              
                              <div className="flex gap-6 flex-col lg:flex-row">
                                <div className="flex-1 space-y-4">
                                  <div>
                                    <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Abstract</h4>
                                    <p className="text-sm leading-relaxed text-foreground/80 bg-background/50 p-4 rounded-md border border-border/50">
                                      {p.abstract}
                                    </p>
                                  </div>
                                  
                                  {p.url && (
                                    <a href={p.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline">
                                      <ExternalLink className="w-3.5 h-3.5" /> View original source
                                    </a>
                                  )}
                                </div>
                                
                                <div className="w-full lg:w-96 space-y-4">
                                  <div className="bg-background/80 p-4 rounded-xl border border-border shadow-sm">
                                    <div className="flex items-center justify-between mb-3 pb-2 border-b border-border/50">
                                      <h4 className="text-sm font-semibold flex items-center gap-2">
                                        <BookOpen className="w-4 h-4 text-primary" /> Extracted Claims
                                      </h4>
                                      <span className="text-xs text-muted-foreground font-mono">{p.claimList?.length || 0} total</span>
                                    </div>
                                    
                                    {(!p.claimList || p.claimList.length === 0) ? (
                                      <p className="text-xs text-muted-foreground italic">No distinct physical claims extracted.</p>
                                    ) : (
                                      <ul className="space-y-3 max-h-64 overflow-y-auto pr-2 scroll-slim">
                                        {p.claimList.map((c: any, idx: number) => (
                                          <li key={idx} className="text-xs flex flex-col gap-1.5 pb-3 border-b border-border/40 last:border-0 last:pb-0">
                                            <span className="text-foreground/90">{c.text}</span>
                                            <div className="flex items-center justify-between">
                                              <span className={cn("px-1.5 py-0.5 rounded-[4px] text-[9px] font-mono uppercase border", getConfidenceColor(c.confidence))}>
                                                {c.confidence} conf
                                              </span>
                                              <Link to="/projects/$projectId/evidence" params={{ projectId }} search={{ q: c.text.slice(0, 20) }} className="opacity-0 group-hover:opacity-100 transition-opacity">
                                                <Button variant="ghost" size="sm" className="h-5 px-1.5 text-[9px] text-primary">
                                                  View in Ledger
                                                </Button>
                                              </Link>
                                            </div>
                                          </li>
                                        ))}
                                      </ul>
                                    )}
                                    
                                    <div className="mt-4 pt-3 border-t border-border flex justify-end">
                                      <Link to="/projects/$projectId/evidence" params={{ projectId }} search={{ q: p.title.slice(0, 30) }}>
                                        <Button size="sm" variant="secondary" className="gap-1.5 text-xs h-8">
                                          <Send className="w-3.5 h-3.5" /> Promote to Ledger
                                        </Button>
                                      </Link>
                                    </div>
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
          )}
        </div>
      </section>
    </>
  );
}

