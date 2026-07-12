import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchJobs, retryJob, cancelJob } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { Activity, RotateCcw, XCircle } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Suspense } from "react";
import { TableSkeleton } from "@/components/dashboard/SkeletonLoader";
import { QueryErrorBoundary } from "@/components/QueryErrorBoundary";

export const Route = createFileRoute("/projects/$projectId/jobs")({
  component: JobsPage,
});

function JobsPage() {
  const { projectId } = Route.useParams();

  return (
    <PageShell>
      <section className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight">Job Executions</h1>
        <p className="text-muted-foreground mt-2">
          Active and completed jobs for project: {projectId}
        </p>
      </section>

      <QueryErrorBoundary>
        <Suspense fallback={<TableSkeleton rows={5} cols={5} />}>
          <JobsContent projectId={projectId} />
        </Suspense>
      </QueryErrorBoundary>
    </PageShell>
  );
}

function JobsContent({ projectId }: { projectId: string }) {
  const queryClient = useQueryClient();
  const { data: jobs } = useSuspenseQuery({
    queryKey: ["jobs", projectId],
    queryFn: () => fetchJobs(projectId),
    refetchInterval: 5000,
  });

  const { mutate: handleRetry } = useMutation({
    mutationFn: (jobId: string) => retryJob(projectId, jobId),
    onSuccess: () => {
      toast.success("Job retry initiated");
      queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
    },
    onError: () => toast.error("Failed to retry job")
  });

  const { mutate: handleCancel } = useMutation({
    mutationFn: (jobId: string) => cancelJob(projectId, jobId),
    onSuccess: () => {
      toast.success("Job cancelled");
      queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
    },
    onError: () => toast.error("Failed to cancel job")
  });

  return (
    <section className="glass-card rounded-xl p-6">
      <header className="flex items-center gap-3 mb-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
          <Activity className="h-4 w-4" />
        </div>
        <h2 className="text-lg font-semibold">Job History</h2>
      </header>

      {!jobs?.length ? (
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
                <th className="px-4 py-3 font-medium text-muted-foreground text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {jobs.map((job: any, i: number) => (
                <tr key={i} className="hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3 font-medium">
                    {job.pipeline_id}
                    {job.retry_of_job_id && (
                      <span className="ml-2 px-1.5 py-0.5 rounded text-[9px] font-mono bg-muted text-muted-foreground border">
                        Retry of {job.retry_of_job_id.slice(0, 8)}
                      </span>
                    )}
                  </td>
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
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-2">
                      {(job.status === "failed" || job.status === "cancelled" || job.status === "completed") && (
                        <Button variant="outline" size="sm" onClick={() => handleRetry(job.id)} className="h-7 px-2 text-xs">
                          <RotateCcw className="w-3 h-3 mr-1" /> Retry
                        </Button>
                      )}
                      {(job.status === "running" || job.status === "pending") && (
                        <Button variant="destructive" size="sm" onClick={() => handleCancel(job.id)} className="h-7 px-2 text-xs">
                          <XCircle className="w-3 h-3 mr-1" /> Cancel
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
