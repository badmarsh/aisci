import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchTasks, updateTask, Task } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { CheckSquare, Loader2, Play, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export const Route = createFileRoute("/projects/$projectId/tasks")({
  component: TasksPage,
});

function TasksPage() {
  const { projectId } = Route.useParams();
  const { data: tasks, isLoading } = useQuery({
    queryKey: ["tasks", projectId],
    queryFn: () => fetchTasks(projectId),
  });

  return (
    <PageShell>
      <section className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight">Tasks</h1>
        <p className="text-muted-foreground mt-2">
          Active tasks and operations for project: {projectId}
        </p>
      </section>

      <div className="flex gap-2 mb-6">
        <button className="px-4 py-2 bg-secondary rounded-lg">Active</button>
        <button className="px-4 py-2 bg-secondary rounded-lg">Blocked</button>
        <button className="px-4 py-2 bg-secondary rounded-lg">Proposed</button>
      </div>

      <section className="glass-card rounded-xl p-6">
        <header className="flex items-center gap-3 mb-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <CheckSquare className="h-4 w-4" />
          </div>
          <h2 className="text-lg font-semibold">Task Queue</h2>
        </header>

        {isLoading ? (
          <div className="py-8 text-center text-muted-foreground">Loading tasks...</div>
        ) : !tasks?.length ? (
          <div className="py-8 text-center text-muted-foreground">No tasks found.</div>
        ) : (
          <div className="space-y-4">
            {tasks.map((t: Task) => (
              <TaskItem key={t.id} task={t} projectId={projectId} />
            ))}
          </div>
        )}
      </section>
    </PageShell>
  );
}

function TaskItem({ task, projectId }: { task: Task; projectId: string }) {
  const queryClient = useQueryClient();

  const { mutate: setStatus, isPending } = useMutation({
    mutationFn: (newStatus: string) => updateTask(projectId, task.id, newStatus),
    onSuccess: (_, newStatus) => {
      toast.success(`Task status updated to ${newStatus}`);
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to update task");
    },
  });

  return (
    <div className="p-4 border border-border rounded-xl bg-card/50 glass-card flex flex-col sm:flex-row gap-4 items-start justify-between hover:border-primary/20 transition-all">
      <div className="flex gap-4 items-start">
        <div
          className={cn(
            "px-2 py-1 h-fit text-[10px] font-mono rounded uppercase border",
            task.status === "done"
              ? "bg-emerald-brand/10 text-emerald-brand border-emerald-brand/20"
              : task.status === "active"
                ? "bg-amber-brand/10 text-amber-brand border-amber-brand/20"
                : "bg-secondary/50 text-secondary-foreground border-transparent",
          )}
        >
          {task.status}
        </div>
        <div>
          <h3 className="font-semibold text-lg">{task.title}</h3>
          <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
          <div className="mt-3 flex flex-wrap gap-4 text-xs font-mono text-muted-foreground">
            <span>Assignee: {task.assignee}</span>
            <span>Priority: {task.priority}</span>
            <span>Date: {task.date}</span>
          </div>
        </div>
      </div>
      
      <div className="flex gap-2 shrink-0">
        {task.status !== "active" && task.status !== "done" && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setStatus("active")}
            disabled={isPending}
            className="h-8 gap-1 border-primary/20 hover:bg-primary/10 text-primary"
          >
            {isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
            Start
          </Button>
        )}
        {task.status !== "done" && (
          <Button
            variant="default"
            size="sm"
            onClick={() => setStatus("done")}
            disabled={isPending}
            className="h-8 gap-1 bg-emerald-brand hover:bg-emerald-brand/90 text-white shadow-sm shadow-emerald-brand/20"
          >
            {isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <CheckCircle2 className="h-3.5 w-3.5" />}
            Complete
          </Button>
        )}
      </div>
    </div>
  );
}
