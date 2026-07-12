import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { fetchLiterature } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { BookOpen, Download } from "lucide-react";
import { Suspense, useState } from "react";
import { TableSkeleton } from "@/components/dashboard/SkeletonLoader";

export const Route = createFileRoute("/projects/$projectId/literature")({
  component: LiteraturePage,
});

function LiteraturePage() {
  const { projectId } = Route.useParams();
  const [searchQuery, setSearchQuery] = useState("");

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

      <Suspense fallback={<TableSkeleton rows={5} cols={2} />}>
        <LiteratureContent
          projectId={projectId}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
        />
      </Suspense>
    </PageShell>
  );
}

function LiteratureContent({
  projectId,
  searchQuery,
  setSearchQuery,
}: {
  projectId: string;
  searchQuery: string;
  setSearchQuery: (val: string) => void;
}) {
  const { data: literature } = useSuspenseQuery({
    queryKey: ["literature", projectId],
    queryFn: () => fetchLiterature(projectId),
  });

  const totalCount = literature?.length ?? 0;
  const arxivCount = literature?.filter((p: any) => p.source === "arXiv").length ?? 0;
  const openalexCount = literature?.filter((p: any) => p.source === "OpenAlex").length ?? 0;

  const filteredLiterature = (literature || []).filter(
    (p: any) =>
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="glass-card p-4 rounded-xl flex flex-col gap-1">
          <span className="text-xs text-muted-foreground uppercase font-medium">Total Papers</span>
          <span className="text-2xl font-semibold font-mono">{totalCount}</span>
        </div>
        <div className="glass-card p-4 rounded-xl flex flex-col gap-1">
          <span className="text-xs text-muted-foreground uppercase font-medium">arXiv Papers</span>
          <span className="text-2xl font-semibold font-mono">{arxivCount}</span>
        </div>
        <div className="glass-card p-4 rounded-xl flex flex-col gap-1">
          <span className="text-xs text-muted-foreground uppercase font-medium">OpenAlex Papers</span>
          <span className="text-2xl font-semibold font-mono">{openalexCount}</span>
        </div>
      </div>

      <section className="glass-card rounded-xl p-6">
        <header className="flex items-center gap-3 mb-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <BookOpen className="h-4 w-4" />
          </div>
          <h2 className="text-lg font-semibold">Research Database</h2>
        </header>

        <div
          className="recharts-responsive-container mb-6 rounded-lg flex items-center justify-center border border-border/30"
          style={{ width: "100%", height: "200px", backgroundColor: "rgba(255,255,255,0.02)" }}
        >
          <div className="text-center p-4">
            <BookOpen className="h-10 w-10 text-primary/40 mx-auto mb-2" />
            <p className="text-sm font-medium">Literature Source Distribution</p>
            <p className="text-xs text-muted-foreground mt-1">
              arXiv ({arxivCount}) vs OpenAlex ({openalexCount})
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search by title or category..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full max-w-sm px-3 py-2 border border-border rounded-md bg-secondary/50 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
            />
          </div>
          {!filteredLiterature.length ? (
            <div className="py-8 text-center text-muted-foreground">
              No papers matching the query found.
            </div>
          ) : (
            <table className="w-full text-sm text-left">
              <thead className="border-b border-border bg-secondary/30">
                <tr>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Category</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredLiterature.map((p: any, i: number) => (
                  <tr key={i} className="hover:bg-muted/30">
                    <td className="px-4 py-3 font-medium">{p.title}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-secondary text-foreground border border-border">
                        {p.category}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </>
  );
}

