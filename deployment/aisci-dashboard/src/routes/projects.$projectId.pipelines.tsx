import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchPipelines, triggerPipeline, PipelineSpec } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { Play, Loader2, Network, FileText, Code2, CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Suspense, useMemo } from "react";
import { TableSkeleton } from "@/components/dashboard/SkeletonLoader";
import { QueryErrorBoundary } from "@/components/QueryErrorBoundary";

export const Route = createFileRoute("/projects/$projectId/pipelines")({
  component: PipelinesPage,
});

function PipelinesPage() {
  const { projectId } = Route.useParams();

  return (
    <PageShell>
      <section className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight">Computational Pipelines</h1>
        <p className="text-muted-foreground mt-2">
          First-class computational procedures for project: {projectId}
        </p>
      </section>

      <QueryErrorBoundary>
        <Suspense fallback={<TableSkeleton rows={4} cols={3} />}>
          <PipelinesContent projectId={projectId} />
        </Suspense>
      </QueryErrorBoundary>
    </PageShell>
  );
}

function PipelinesContent({ projectId }: { projectId: string }) {
  const { data: pipelines } = useSuspenseQuery({
    queryKey: ["pipelines", projectId],
    queryFn: () => fetchPipelines(projectId),
  });

  const groupedPipelines = useMemo(() => {
    const userPipelines = pipelines?.filter(p => p.owner !== "Robert") || [];
    const robertPipelines = pipelines?.filter(p => p.owner === "Robert") || [];
    return { userPipelines, robertPipelines };
  }, [pipelines]);

  return (
    <div className="space-y-8">
      {groupedPipelines.userPipelines.length > 0 && (
        <section className="glass-card rounded-xl p-6">
          <header className="flex items-center gap-3 mb-6">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
              <Network className="h-4 w-4" />
            </div>
            <h2 className="text-lg font-semibold">My Pipelines</h2>
          </header>
          <div className="grid gap-4 md:grid-cols-2">
            {groupedPipelines.userPipelines.map(p => (
              <PipelineCard key={p.id} pipeline={p} projectId={projectId} />
            ))}
          </div>
        </section>
      )}

      <section className="glass-card rounded-xl p-6">
        <header className="flex items-center gap-3 mb-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-secondary text-muted-foreground border border-border">
            <Network className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">Robert's Pipelines</h2>
            <p className="text-xs text-muted-foreground mt-1">Autonomous system procedures</p>
          </div>
        </header>
        {!groupedPipelines.robertPipelines.length ? (
          <div className="py-8 text-center text-muted-foreground">No system pipelines found.</div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {groupedPipelines.robertPipelines.map(p => (
              <PipelineCard key={p.id} pipeline={p} projectId={projectId} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function PipelineCard({ pipeline, projectId }: { pipeline: PipelineSpec; projectId: string }) {
  const queryClient = useQueryClient();

  const { mutate: runPipeline, isPending } = useMutation({
    mutationFn: () => triggerPipeline(projectId, pipeline.id),
    onSuccess: () => {
      toast.success(`Triggered pipeline: ${pipeline.name}`);
      queryClient.invalidateQueries();
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : "Failed to trigger pipeline"),
  });

  return (
    <div className="p-5 border border-border rounded-xl bg-card hover:shadow-md hover:border-primary/20 transition-all flex flex-col justify-between h-full group">
      <div>
        <div className="flex justify-between items-start mb-3">
          <h3 className="font-semibold text-lg">{pipeline.name}</h3>
          <span className={cn(
            "text-[10px] font-mono px-2 py-0.5 rounded-full uppercase border flex items-center gap-1",
            pipeline.available
              ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
              : "bg-amber-500/10 text-amber-500 border-amber-500/20"
          )}>
            {pipeline.available ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
            {pipeline.available ? "Ready" : "Unavailable"}
          </span>
        </div>

        {pipeline.description && (
          <p className="text-sm text-muted-foreground mb-4 leading-relaxed">
            {pipeline.description}
          </p>
        )}

        <div className="space-y-2 mb-6">
          {pipeline.citation && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/50 p-2 rounded-md border border-border">
              <FileText className="w-3.5 h-3.5 shrink-0" />
              <span className="font-mono truncate" title={pipeline.citation}>{pipeline.citation}</span>
            </div>
          )}
          {pipeline.entrypoint && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/50 p-2 rounded-md border border-border">
              <Code2 className="w-3.5 h-3.5 shrink-0" />
              <span className="font-mono truncate" title={pipeline.entrypoint}>{pipeline.entrypoint}</span>
            </div>
          )}
        </div>
      </div>

      <div className="mt-auto flex justify-end">
        <Button
          variant="default"
          size="sm"
          onClick={() => runPipeline()}
          disabled={!pipeline.available || isPending}
          className="gap-1.5 shadow-sm"
        >
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Run Pipeline
        </Button>
      </div>
    </div>
  );
}
