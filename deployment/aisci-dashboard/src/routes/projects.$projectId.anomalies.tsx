import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { fetchAnomalies } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/projects/$projectId/anomalies")({
  component: AnomaliesPage,
});

function AnomaliesPage() {
  const { projectId } = Route.useParams();
  const { data: anomalies, isLoading } = useQuery({
    queryKey: ["anomalies", projectId],
    queryFn: () => fetchAnomalies(projectId),
  });

  return (
    <PageShell>
      <section className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight">Anomalies</h1>
        <p className="text-muted-foreground mt-2">
          Detected physics anomalies for project: {projectId}
        </p>
      </section>

      <section className="glass-card rounded-xl p-6">
        <header className="flex items-center gap-3 mb-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-destructive/10 text-destructive">
            <AlertTriangle className="h-4 w-4" />
          </div>
          <h2 className="text-lg font-semibold">Anomaly Reports</h2>
        </header>

        {isLoading ? (
          <div className="py-8 text-center text-muted-foreground">Loading anomalies...</div>
        ) : !anomalies?.length ? (
          <div className="py-8 text-center text-muted-foreground">No anomalies found.</div>
        ) : (
          <div className="space-y-4">
            {anomalies.map((a: any, i: number) => (
              <div key={i} className="flex gap-4 p-4 border border-border rounded-lg bg-card">
                <div
                  className={cn(
                    "px-2 py-1 h-fit text-xs font-medium rounded uppercase",
                    a.severity === "high"
                      ? "bg-destructive text-destructive-foreground"
                      : "bg-amber-500/20 text-amber-500",
                  )}
                >
                  {a.severity}
                </div>
                <div>
                  <h3 className="font-semibold">
                    {a.model} ({a.bin})
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">{a.message}</p>
                  <p className="text-xs font-mono mt-2 text-muted-foreground">
                    Type: {a.type} | Value: {a.value}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </PageShell>
  );
}
