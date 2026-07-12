import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useSuspenseQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchJobs, retryJob, cancelJob, fetchJobLogs } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { Activity, RotateCcw, XCircle, Terminal, FileText, AlertTriangle, Clock } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Suspense, useState } from "react";
import { TableSkeleton } from "@/components/dashboard/SkeletonLoader";
import { QueryErrorBoundary } from "@/components/QueryErrorBoundary";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import ReactMarkdown from "react-markdown";

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
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

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

  const { data: logData, isLoading: isLogLoading } = useQuery({
    queryKey: ["jobLogs", projectId, selectedJobId],
    queryFn: () => fetchJobLogs(projectId, selectedJobId!),
    enabled: !!selectedJobId,
  });

  const formatDuration = (start: string, end?: string | null) => {
    if (!end) return "Running...";
    const diff = new Date(end).getTime() - new Date(start).getTime();
    if (diff < 1000) return "< 1s";
    return `${(diff / 1000).toFixed(1)}s`;
  };

  return (
    <section className="glass-card rounded-xl p-6">
      <header className="flex items-center gap-3 mb-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
          <Activity className="h-4 w-4" />
        </div>
        <h2 className="text-lg font-semibold">Job History</h2>
      </header>

      {!jobs?.length ? (
        <div className="py-8 text-center text-muted-foreground">No jobs found.</div>
      ) : (
        <div className="grid gap-4">
          {jobs.map((job: any) => (
            <div key={job.id} className="flex flex-col md:flex-row gap-4 p-5 border border-border rounded-xl bg-card hover:border-primary/30 transition-colors shadow-sm">
              <div className="flex flex-col gap-2 shrink-0">
                <span
                  className={cn(
                    "px-2.5 py-1 w-fit text-[10px] font-mono font-bold rounded uppercase tracking-wider text-center",
                    job.status === "completed"
                      ? "bg-emerald-brand/10 text-emerald-brand border border-emerald-brand/20 shadow-sm"
                      : job.status === "running"
                        ? "bg-amber-brand/10 text-amber-brand border border-amber-brand/20 shadow-sm"
                        : job.status === "failed"
                          ? "bg-rose-brand/10 text-rose-brand border border-rose-brand/20 shadow-sm"
                          : "bg-secondary/50 text-secondary-foreground",
                  )}
                >
                  {job.status}
                </span>
                
                {job.exit_code !== null && job.exit_code !== undefined && (
                  <div className="text-[10px] font-mono uppercase px-2 py-0.5 rounded border border-border bg-muted flex flex-col items-center">
                    <span className="text-muted-foreground/70">Exit</span>
                    <span className={job.exit_code === 0 ? "text-emerald-500" : "text-rose-500 font-bold"}>
                      {job.exit_code}
                    </span>
                  </div>
                )}
              </div>
              
              <div className="flex-1 min-w-0 flex flex-col justify-center">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <h3 className="font-semibold text-lg text-foreground tracking-tight">
                    {job.pipeline_id}
                  </h3>
                  <span className="text-muted-foreground/30">•</span>
                  <span className="text-sm font-mono text-muted-foreground bg-secondary px-2 py-0.5 rounded border border-border/50">ID: {job.id.slice(0, 8)}</span>
                  
                  {job.retry_of_job_id && (
                    <span className="ml-1 px-1.5 py-0.5 rounded text-[10px] font-mono bg-muted text-muted-foreground border border-border">
                      <RotateCcw className="w-3 h-3 inline-block mr-1" />
                      Retry of {job.retry_of_job_id.slice(0, 8)}
                    </span>
                  )}
                </div>
                
                <div className="flex items-center gap-4 mt-2">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-mono bg-secondary/30 px-2 py-1 rounded">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Created: {new Date(job.created_at).toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-mono bg-secondary/30 px-2 py-1 rounded">
                    <Activity className="w-3.5 h-3.5" />
                    <span>Duration: {formatDuration(job.created_at, job.updated_at)}</span>
                  </div>
                </div>

                {job.error && (
                  <div className="mt-3 p-3 rounded-md bg-rose-500/10 border border-rose-500/20 text-xs font-mono text-rose-500 flex gap-2 overflow-x-auto">
                    <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                    <div className="whitespace-pre-wrap">{job.error}</div>
                  </div>
                )}
              </div>

              <div className="flex flex-row md:flex-col items-center justify-end gap-2 shrink-0 border-t md:border-t-0 md:border-l border-border pt-4 md:pt-0 md:pl-4 mt-2 md:mt-0">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setSelectedJobId(job.id)} 
                  className="w-full text-xs h-8 gap-1.5 shadow-sm bg-secondary/30 hover:bg-secondary/60"
                >
                  <Terminal className="w-3.5 h-3.5" /> Raw Log
                </Button>
                
                {(job.status === "failed" || job.status === "cancelled" || job.status === "completed") && (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleRetry(job.id)} 
                    className="w-full text-xs h-8 gap-1.5 text-foreground hover:bg-primary/10 hover:text-primary hover:border-primary/30 transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" /> Retry Job
                  </Button>
                )}
                
                {(job.status === "running" || job.status === "pending") && (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => handleCancel(job.id)} 
                    className="w-full text-xs h-8 gap-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
                  >
                    <XCircle className="w-3.5 h-3.5" /> Cancel
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <Dialog open={!!selectedJobId} onOpenChange={(o) => !o && setSelectedJobId(null)}>
        <DialogContent className="max-w-3xl h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-primary" />
              Raw Execution Log: {selectedJobId?.slice(0, 8)}
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="flex-1 mt-4 rounded-md border border-border bg-zinc-100 dark:bg-black/95 p-4">
            {isLogLoading ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Activity className="w-4 h-4 animate-spin" /> Fetching logs...
              </div>
            ) : logData?.logs ? (
              <pre className="font-mono text-xs leading-relaxed text-zinc-800 dark:text-zinc-300 whitespace-pre-wrap">
                {logData.logs}
              </pre>
            ) : (
              <div className="text-muted-foreground italic text-sm">No log data available or log file is empty.</div>
            )}
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </section>
  );
}
