import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { fetchEvidence } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { FileText } from "lucide-react";

export const Route = createFileRoute("/projects/$projectId/evidence")({
  component: EvidencePage,
});

function EvidencePage() {
  const { projectId } = Route.useParams();
  const { data: evidence, isLoading } = useQuery({
    queryKey: ["evidence", projectId],
    queryFn: () => fetchEvidence(projectId),
  });

  return (
    <PageShell>
      <section className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight">Science Ledger</h1>
        <p className="text-muted-foreground mt-2">
          Evidence ledger claims for project: {projectId}
        </p>
      </section>

      <div className="flex gap-2 mb-6">
        <div className="px-3 py-1 bg-secondary rounded">Supported</div>
        <div className="px-3 py-1 bg-secondary rounded">Sanity Checked</div>
        <div className="px-3 py-1 bg-secondary rounded">Proposed</div>
      </div>

      <section className="glass-card rounded-xl p-6">
        <header className="flex items-center gap-3 mb-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <FileText className="h-4 w-4" />
          </div>
          <h2 className="text-lg font-semibold">Ledger</h2>
        </header>

        {isLoading ? (
          <div className="py-8 text-center text-muted-foreground">Loading evidence...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="border-b border-border bg-secondary/30">
                <tr>
                  <th className="px-4 py-3">Claim</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Narrative</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {(evidence || []).map((e: any, i: number) => (
                  <tr key={i} className="hover:bg-muted/30">
                    <td className="px-4 py-3 font-medium">{e.claim}</td>
                    <td className="px-4 py-3">{e.status}</td>
                    <td className="px-4 py-3 text-muted-foreground">{e.narrative}</td>
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
