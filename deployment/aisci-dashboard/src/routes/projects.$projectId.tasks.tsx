import { createFileRoute } from "@tanstack/react-router";
import { toast } from "sonner";
import { ChevronDown, Database, FileCode2, Filter, Search, Terminal, Workflow } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { fetchTasks, updateTask, syncFromFiles, fetchProjects } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { StatusBadge } from "@/components/dashboard/StatusBadge";
import { cn } from "@/lib/utils";
import { type Task } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/projects/$projectId/tasks")({
  beforeLoad: async ({ params }) => {
    const projects = await fetchProjects();
    const p = projects.find((p) => p.id === params.projectId);
    if (!p || !p.capabilities.includes("tasks")) {
      throw redirect({ to: `/projects/${params.projectId}` as any });
    }
  },
  head: () => ({
    meta: [
      { title: "Task Queue — AiSci" },
      { name: "description", content: "Queue of analysis requests and blocked decisions." },
    ],
  }),
  component: TasksPage,
});

const statuses = ["all", "active", "blocked", "proposed", "closed"];

function TasksPage() {
  const queryClient = useQueryClient();
  const { projectId } = Route.useParams();

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ["tasks", projectId],
    queryFn: () => fetchTasks(projectId),
  });
  const [status, setStatus] = useState("all");
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  const syncMutation = useMutation({
    mutationFn: () => syncFromFiles(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Synced from canonical files.");
    },
  });

  const mutation = useMutation({
    mutationFn: ({ id, newStatus }: { id: string; newStatus: string }) =>
      updateTask(projectId, id, newStatus),
    onSuccess: (_, { newStatus }) => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success(`Task marked as ${newStatus}`);
    },
  });

  const filtered = useMemo(
    () =>
      tasks.filter(
        (t: Task) =>
          (status === "all" || t.status === status) &&
          `${t?.id || ""} ${t?.title || ""} ${t?.description || ""} ${t?.assignee || ""}`
            .toLowerCase()
            .includes(query.toLowerCase()),
      ),
    [tasks, status, query],
  );

  return (
    <PageShell>
      <section className="mb-6 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-primary">
            <Workflow className="h-3.5 w-3.5" /> Orchestration layer
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">Task control plane</h1>
          <p className="max-w-2xl text-sm leading-6 text-muted-foreground">
            Monitor ingestion, parameter extraction, symbolic validation, and provenance sealing
            across the research pipeline.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            disabled={syncMutation.isPending}
            onClick={() => syncMutation.mutate()}
          >
            Sync from Files
          </Button>
          <div className="grid grid-cols-3 overflow-hidden rounded-lg border border-border bg-card/70">
            {["active", "blocked", "proposed"].map((s) => (
              <div key={s} className="border-r border-border px-4 py-2 last:border-0">
                <div className="font-mono text-xl font-semibold">
                  {tasks.filter((t: Task) => t.status === s).length}
                </div>
                <div className="text-[10px] uppercase tracking-wide text-muted-foreground">{s}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="glass-card overflow-hidden rounded-xl">
        <div className="flex flex-col justify-between gap-3 border-b border-border p-3 md:flex-row md:items-center">
          <div className="relative flex-1 md:max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search task, description, or agent"
              aria-label="Search tasks"
              className="h-9 w-full rounded-md border border-input bg-background/60 pl-9 pr-3 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
            />
          </div>
          <div className="flex items-center gap-1 overflow-auto">
            <Filter className="mr-1 h-4 w-4 text-muted-foreground" />
            {statuses.map((s) => (
              <button
                key={s}
                onClick={() => setStatus(s)}
                className={cn(
                  "rounded-md px-3 py-1.5 text-xs font-medium capitalize transition",
                  status === s
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                )}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="hidden grid-cols-[100px_minmax(240px,1fr)_130px_110px_160px_36px] gap-4 border-b border-border bg-secondary/30 px-4 py-2 text-[10px] font-medium uppercase tracking-[0.12em] text-muted-foreground md:grid">
          <span>Task</span>
          <span>Work unit</span>
          <span>Status</span>
          <span>Agent</span>
          <span>Progress</span>
          <span />
        </div>

        {isLoading ? (
          <div className="h-64 animate-pulse bg-secondary/20" />
        ) : filtered.length === 0 ? (
          <div className="flex h-64 flex-col items-center justify-center gap-2 text-muted-foreground">
            <Search className="h-7 w-7" />
            <p className="text-sm">No tasks match this view.</p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {filtered.map((task: Task) => {
              const open = expanded === task.id;
              const progress = task.status === "closed" ? 100 : task.status === "active" ? 50 : 0;
              return (
                <article key={task.id}>
                  <button
                    aria-expanded={open}
                    onClick={() => setExpanded(open ? null : task.id)}
                    className="grid w-full gap-3 px-4 py-4 text-left transition hover:bg-secondary/25 md:grid-cols-[100px_minmax(240px,1fr)_130px_110px_160px_36px] md:items-center md:gap-4"
                  >
                    <span className="font-mono text-xs text-primary">
                      {String(task?.id || "").slice(0, 8)}...
                    </span>
                    <span className="min-w-0">
                      <strong className="block truncate text-sm font-medium">{task.title}</strong>
                      <span className="mt-1 block truncate text-[11px] text-muted-foreground">
                        {task.citation || "Unknown Source"} ·{" "}
                        <b className="font-mono text-amber-brand">{task.priority}</b>
                      </span>
                    </span>
                    <StatusBadge
                      status={
                        task.status === "proposed"
                          ? "pending"
                          : task.status === "active"
                            ? "running"
                            : task.status === "blocked"
                              ? "anomaly"
                              : "success"
                      }
                    />
                    <span className="text-xs text-muted-foreground">{task.assignee}</span>
                    <span>
                      <span className="flex justify-between font-mono text-[10px] text-muted-foreground">
                        <span>{progress}%</span>
                        <span>{task.date}</span>
                      </span>
                      <span className="mt-1.5 block h-1.5 overflow-hidden rounded-full bg-secondary">
                        <span
                          className={cn(
                            "block h-full",
                            task.status === "blocked"
                              ? "bg-amber-brand"
                              : task.status === "closed"
                                ? "bg-emerald-brand"
                                : "bg-primary",
                          )}
                          style={{ width: `${progress}%` }}
                        />
                      </span>
                    </span>
                    <ChevronDown
                      className={cn(
                        "hidden h-4 w-4 text-muted-foreground transition md:block",
                        open && "rotate-180 text-primary",
                      )}
                    />
                  </button>
                  {open && (
                    <div className="grid gap-4 border-t border-border bg-background/50 p-4 lg:grid-cols-2">
                      <div className="rounded-lg border border-border bg-card/60 p-4 flex flex-col justify-between">
                        <div>
                          <h3 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide">
                            <Database className="h-4 w-4 text-primary" />
                            Task details
                          </h3>
                          <dl className="mt-4 grid grid-cols-[110px_1fr] gap-x-3 gap-y-2 text-xs">
                            <dt className="text-muted-foreground">Description</dt>
                            <dd className="text-muted-foreground">{task.description}</dd>
                            <dt className="text-muted-foreground">Citation</dt>
                            <dd className="font-mono text-primary truncate">
                              {task.citation || "N/A"}
                            </dd>
                            <dt className="text-muted-foreground">Date</dt>
                            <dd className="font-mono">{task.date}</dd>
                          </dl>
                        </div>
                        {task.status === "proposed" && (
                          <div className="mt-4 pt-4 border-t border-border">
                            <Button
                              size="sm"
                              onClick={() => mutation.mutate({ id: task.id, newStatus: "active" })}
                            >
                              Approve to Active
                            </Button>
                          </div>
                        )}
                      </div>
                      <div className="rounded-lg border border-border bg-[#080b10] p-4 text-[#d8e4ec]">
                        <h3 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                          <Terminal className="h-4 w-4 text-primary" />
                          Execution log
                        </h3>
                        <div className="mt-4 flex flex-col gap-2 font-mono text-[11px]">
                          <div className="grid grid-cols-[64px_42px_1fr] gap-2">
                            <span className="text-muted-foreground">{task.date}</span>
                            <span className="text-primary">info</span>
                            <span>Task initialized by {task.assignee}</span>
                          </div>
                          {task.status === "proposed" && (
                            <div className="grid grid-cols-[64px_42px_1fr] gap-2">
                              <span className="text-muted-foreground">now</span>
                              <span className="text-amber-brand">warn</span>
                              <span>Waiting for user approval</span>
                            </div>
                          )}
                          {task.status === "active" && (
                            <div className="grid grid-cols-[64px_42px_1fr] gap-2">
                              <span className="text-muted-foreground">now</span>
                              <span className="text-primary">info</span>
                              <span>Executing runbook steps...</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}
      </section>
    </PageShell>
  );
}
