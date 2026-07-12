import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { fetchLiterature } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { BookOpen } from "lucide-react";

export const Route = createFileRoute("/projects/$projectId/literature")({
  component: LiteraturePage,
});

function LiteraturePage() {
  const { projectId } = Route.useParams();
  const { data: literature, isLoading } = useQuery({
    queryKey: ["literature", projectId],
    queryFn: () => fetchLiterature(projectId),
  });

  return (
    <PageShell>
      <section className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight">Literature Radar</h1>
        <p className="text-muted-foreground mt-2">Ingested papers for project: {projectId}</p>
      </section>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="glass-card p-4 rounded-xl">Total Papers</div>
        <div className="glass-card p-4 rounded-xl">arXiv Papers</div>
        <div className="glass-card p-4 rounded-xl">OpenAlex Papers</div>
      </div>

      <section className="glass-card rounded-xl p-6">
        <header className="flex items-center gap-3 mb-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <BookOpen className="h-4 w-4" />
          </div>
          <h2 className="text-lg font-semibold">Research Database</h2>
        </header>

        <div
          className="recharts-responsive-container mb-6"
          style={{ width: "100%", height: "300px", backgroundColor: "rgba(255,255,255,0.05)" }}
        ></div>

        {isLoading ? (
          <div className="py-8 text-center text-muted-foreground">Loading literature...</div>
        ) : (
          <div className="overflow-x-auto">
            <div className="mb-4">
              <input
                type="text"
                placeholder="Search…"
                className="w-full max-w-sm px-3 py-2 border border-border rounded-md bg-secondary/50"
              />
            </div>
            <table className="w-full text-sm text-left">
              <thead className="border-b border-border bg-secondary/30">
                <tr>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Category</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {(literature || []).map((p: any, i: number) => (
                  <tr key={i} className="hover:bg-muted/30">
                    <td className="px-4 py-3 font-medium">{p.title}</td>
                    <td className="px-4 py-3">{p.category}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </PageShell>
  );
}
