import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { fetchJobs } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { Activity } from "lucide-react";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/projects/$projectId/jobs")({
  component: JobsPage,
});

function JobsPage() {
  const { projectId } = Route.useParams();
  const { data: jobs, isLoading } = useQuery({
    queryKey: ["jobs", projectId],
    queryFn: () => fetchJobs(projectId),
  });

  return (
    <PageShell>
      <section className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight">Job Executions</h1>
        <p className="text-muted-foreground mt-2">
          Active and completed jobs for project: {projectId}
        </p>
      </section>

      <section className="glass-card rounded-xl p-6">
        <header className="flex items-center gap-3 mb-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <Activity className="h-4 w-4" />
          </div>
          <h2 className="text-lg font-semibold">Job History</h2>
        </header>

        {isLoading ? (
          <div className="py-8 text-center text-muted-foreground">Loading jobs...</div>
        ) : !jobs?.length ? (
          <div className="py-8 text-center text-muted-foreground">No jobs found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="border-b border-border bg-secondary/30">
                <tr>
                  <th className="px-4 py-3 font-medium text-muted-foreground">Pipeline</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">Status</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">Created At</th>
                  <th className="px-4 py-3 font-medium text-muted-foreground">Exit Code</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {jobs.map((job: any, i: number) => (
                  <tr key={i} className="hover:bg-muted/30 transition-colors">
                    <td className="px-4 py-3 font-medium">{job.pipeline_id}</td>
                    <td className="px-4 py-3">
                      <span
                        className={cn(
                          "px-2 py-1 rounded text-[10px] font-mono uppercase",
                          job.status === "completed"
                            ? "bg-emerald-brand/10 text-emerald-brand border border-emerald-brand/20"
                            : job.status === "running"
                              ? "bg-amber-brand/10 text-amber-brand border border-amber-brand/20"
                              : job.status === "failed"
                                ? "bg-rose-brand/10 text-rose-brand border border-rose-brand/20"
                                : "bg-secondary/50 text-secondary-foreground",
                        )}
                      >
                        {job.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs">{job.exit_code ?? "—"}</td>
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
