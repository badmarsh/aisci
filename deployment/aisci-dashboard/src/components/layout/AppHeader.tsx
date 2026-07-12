import { useLocation, useParams, Link } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Bell,
  ChevronRight,
  FlaskConical,
  Loader2,
  Menu,
  Play,
  Search,
  Home,
  Atom,
  BookOpen,
  ShieldCheck,
  ListTodo,
  AlertTriangle,
  FileCode2,
  Bot,
  FolderTree,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import {
  triggerPipeline,
  fetchActivity,
  fetchPipelines,
  fetchProjects,
  materializeDecisions,
} from "@/lib/api";
import { LogDrawer } from "@/components/LogDrawer";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

const titles: Record<string, { title: string; crumb: string }> = {
  "/": { title: "Overview", crumb: "Portfolio" },
  "/fits": { title: "Physics Fits", crumb: "Physics Fits" },
  "/literature": { title: "Literature Intake", crumb: "Literature Intake" },
  "/evidence": { title: "Evidence Ledger", crumb: "Evidence Ledger" },
  "/tasks": { title: "Task Queue", crumb: "Tasks" },
  "/agents": { title: "Agents", crumb: "Agents" },
};

export function AppHeader() {
  const { pathname } = useLocation();
  // Find matching title based on end of pathname
  const pathKey = Object.keys(titles).find((k) => pathname?.endsWith(k)) || "/";
  const meta = titles[pathKey] || { title: "AiSci", crumb: "Overview" };

  const queryClient = useQueryClient();
  const [mobile, setMobile] = useState(false);
  const [logTarget, setLogTarget] = useState<string | null>(null);
  const [hasReadNotifications, setHasReadNotifications] = useState(false);

  const { projectId } = useParams({ strict: false }) as { projectId?: string };

  const { data: projects = [] } = useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
    staleTime: 60_000,
  });

  const project = projects.find((p: import("@/lib/api").Project) => p.id === projectId);
  const caps = project?.capabilities || [];

  const navItems = projectId
    ? [
        { title: "Overview", url: `/projects/${projectId}`, icon: Home, req: null },
        {
          title: "Physics Fits",
          url: `/projects/${projectId}/fits`,
          icon: Atom,
          req: ["fit_validation"],
        },
        {
          title: "Literature Intake",
          url: `/projects/${projectId}/literature`,
          icon: BookOpen,
          req: ["literature"],
        },
        {
          title: "Evidence Ledger",
          url: `/projects/${projectId}/evidence`,
          icon: ShieldCheck,
          req: ["evidence"],
        },
        {
          title: "Task Queue",
          url: `/projects/${projectId}/tasks`,
          icon: ListTodo,
          req: ["tasks"],
        },
        {
          title: "Anomalies",
          url: `/projects/${projectId}/anomalies`,
          icon: AlertTriangle,
          req: ["fit_validation"],
        },
        {
          title: "Jobs",
          url: `/projects/${projectId}/jobs`,
          icon: FileCode2,
          req: ["fit_validation", "symbolic_validation"],
        },
        { title: "Agents", url: `/projects/${projectId}/agents`, icon: Bot, req: null },
      ].filter((item) => !item.req || item.req.some((r: string) => caps.includes(r)))
    : [];

  const { data: activityFeed = [] } = useQuery({
    queryKey: ["activity", projectId],
    queryFn: () => (projectId ? fetchActivity(projectId) : Promise.resolve([])),
    staleTime: 10_000,
    enabled: !!projectId,
  });

  const recentCount = activityFeed.length;
  const recentActivities = activityFeed.slice(0, 10);

  const { data: pipelines = [] } = useQuery({
    queryKey: ["pipelines", projectId],
    queryFn: () => (projectId ? fetchPipelines(projectId) : Promise.resolve([])),
    staleTime: 10_000,
    enabled: !!projectId,
  });

  const pipelineMutation = useMutation({
    mutationFn: (pipelineId: string) => triggerPipeline(projectId!, pipelineId),
    onSuccess: (data) => {
      toast.success("Pipeline triggered.", { description: data.message });
      queryClient.invalidateQueries({ queryKey: ["literature", projectId] });
      queryClient.invalidateQueries({ queryKey: ["fits", projectId] });
      queryClient.invalidateQueries({ queryKey: ["anomalies", projectId] });
    },
    onError: (err: Error) => {
      toast.error(`Pipeline failed to start: ${err.message}`);
    },
  });

  function runPipeline(pipelineId: string, name: string) {
    if (!projectId) return;
    toast(`Pipeline ${name} started.`, { description: "Running in background..." });
    setLogTarget(pipelineId);
    pipelineMutation.mutate(pipelineId);
  }

  return (
    <>
      <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border bg-background/85 px-4 backdrop-blur-xl md:px-6">
        <button
          className="rounded-md p-2 text-muted-foreground lg:hidden"
          onClick={() => setMobile((v) => !v)}
          aria-label="Toggle navigation"
        >
          <Menu className="h-5 w-5" />
        </button>

        <nav aria-label="Breadcrumb" className="hidden items-center gap-2 text-xs sm:flex">
          <span className="text-muted-foreground">Control plane</span>
          <ChevronRight className="h-3 w-3 text-muted-foreground" />
          <strong>{meta.crumb}</strong>
        </nav>

        <div className="ml-auto flex items-center gap-2">
          {/* Global Search Input */}
          <label className="relative hidden md:block">
            <span className="sr-only">Search research graph</span>
            <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
            <input
              className="h-9 w-56 rounded-md border border-input bg-secondary/40 pl-9 pr-3 text-xs outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
              placeholder="Search claims, jobs, DOIs…"
            />
          </label>

          {/* Dynamic Pipeline Actions */}
          {projectId &&
            pipelines.map((p) => {
              const isPending = pipelineMutation.isPending && pipelineMutation.variables === p.id;
              const isUnavailable = p.status.startsWith("unavailable");
              return (
                <button
                  key={p.id}
                  onClick={() => runPipeline(p.id, p.name)}
                  disabled={isPending || isUnavailable}
                  title={isUnavailable ? p.status : `Run ${p.name}`}
                  className="pulse-glow inline-flex h-9 items-center gap-2 rounded-md bg-primary px-3 text-xs font-semibold text-primary-foreground transition hover:brightness-110 disabled:opacity-70 disabled:pointer-events-none"
                >
                  {isPending ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Play className="h-3.5 w-3.5" />
                  )}
                  <span className="hidden sm:inline">
                    {isPending ? "Running…" : `Run ${p.name}`}
                  </span>
                </button>
              );
            })}

          {/* Materialize Decisions Action */}
          {projectId && (
            <button
              onClick={() => {
                toast("Applying approved decisions...", {
                  description: "Updating canonical markdown ledgers...",
                });
                materializeDecisions(projectId)
                  .then((data) => {
                    toast.success("Decisions Materialized", { description: data.message });
                    queryClient.invalidateQueries({ queryKey: ["evidence"] });
                    queryClient.invalidateQueries({ queryKey: ["tasks"] });
                  })
                  .catch((err) =>
                    toast.error("Materialization failed", { description: err.message }),
                  );
              }}
              title="Apply Approved Decisions to Ledger"
              className="pulse-glow inline-flex h-9 items-center gap-2 rounded-md bg-indigo-brand px-3 text-xs font-semibold text-white transition hover:brightness-110"
            >
              <ShieldCheck className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Commit Ledger</span>
            </button>
          )}

          {/* Notifications Popover */}
          <Popover
            onOpenChange={(open) => {
              if (open) setHasReadNotifications(true);
            }}
          >
            <PopoverTrigger asChild>
              <button
                aria-label="Notifications"
                className="relative rounded-md p-2 text-muted-foreground hover:bg-secondary hover:text-foreground"
              >
                <Bell className="h-4 w-4" />
                {recentCount > 0 && !hasReadNotifications && (
                  <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-amber-brand" />
                )}
              </button>
            </PopoverTrigger>
            <PopoverContent className="w-80 p-0" align="end">
              <div className="flex items-center justify-between border-b border-border px-4 py-3">
                <h4 className="text-sm font-semibold">Notifications</h4>
                <Badge variant="secondary" className="text-[10px]">
                  {recentCount} New
                </Badge>
              </div>
              <ScrollArea className="h-72">
                {recentActivities.length > 0 ? (
                  <div className="flex flex-col">
                    {recentActivities.map((item: import("@/lib/api").ActivityModel, i: number) => (
                      <div
                        key={i}
                        className="flex flex-col gap-1 border-b border-border p-4 text-sm last:border-0 hover:bg-muted/50"
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-foreground">{item.action}</span>
                          <span className="text-[10px] text-muted-foreground">
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground">{item.details}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 text-center text-sm text-muted-foreground">
                    No new notifications.
                  </div>
                )}
              </ScrollArea>
            </PopoverContent>
          </Popover>
        </div>
      </header>

      {mobile && (
        <div className="fixed inset-x-3 top-19 z-40 rounded-xl border border-border bg-popover p-2 shadow-2xl lg:hidden flex flex-col max-h-[80vh] overflow-y-auto">
          <Link
            to="/"
            onClick={() => setMobile(false)}
            className="flex items-center gap-3 rounded-md px-3 py-3 text-sm hover:bg-secondary"
          >
            <FolderTree className="h-4 w-4 text-primary" />
            Portfolio
          </Link>
          {navItems.map((item) => (
            <Link
              key={item.title}
              to={item.url}
              onClick={() => setMobile(false)}
              className="flex items-center gap-3 rounded-md px-3 py-3 text-sm hover:bg-secondary"
            >
              <item.icon className="h-4 w-4 text-primary" />
              {item.title}
            </Link>
          ))}
        </div>
      )}

      <LogDrawer target={logTarget} onClose={() => setLogTarget(null)} />
    </>
  );
}
