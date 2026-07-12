import { Link, useRouterState, useParams } from "@tanstack/react-router";
import {
  Atom,
  ChevronLeft,
  FlaskConical,
  Home,
  BookOpen,
  ShieldCheck,
  ListTodo,
  Bot,
  AlertTriangle,
  FileCode2,
  FolderTree,
} from "lucide-react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "@/lib/api";
import { cn } from "@/lib/utils";

export function AppSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  const { projectId } = useParams({ strict: false }) as { projectId?: string };

  const { data: projects = [] } = useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
    staleTime: 60_000,
  });

  const project = projects.find((p: import("@/lib/api").Project) => p.id === projectId);
  const caps = project?.capabilities || [];

  const items = projectId
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

  return (
    <aside
      className={cn(
        "sticky top-0 hidden h-screen shrink-0 flex-col border-r border-sidebar-border bg-sidebar/95 transition-[width] duration-300 lg:flex",
        collapsed ? "w-[72px]" : "w-60",
      )}
    >
      <div className="flex h-16 items-center gap-3 border-b border-sidebar-border px-4">
        <Link
          to="/"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-primary/40 bg-primary/10 text-primary shadow-[0_0_18px_-6px_var(--cyan-brand)]"
        >
          <FlaskConical className="h-5 w-5" />
        </Link>
        {!collapsed && (
          <div className="min-w-0">
            <div className="font-semibold tracking-tight">AiSci</div>
            <div className="truncate text-[9px] uppercase tracking-[0.18em] text-muted-foreground">
              Research control plane
            </div>
          </div>
        )}
      </div>

      <div className="px-3 py-4 flex-1 overflow-y-auto scroll-slim">
        {!collapsed && (
          <div className="mb-3 text-[9px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Navigation
          </div>
        )}
        <nav className="flex flex-col gap-1">
          <Link
            to="/"
            title="Portfolio"
            className={cn(
              "relative flex h-10 items-center gap-3 rounded-md px-3 text-sm transition-colors",
              pathname === "/"
                ? "bg-sidebar-accent text-foreground before:absolute before:-left-3 before:h-5 before:w-0.5 before:bg-primary"
                : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-foreground",
            )}
          >
            <FolderTree className={cn("h-4 w-4 shrink-0", pathname === "/" && "text-primary")} />
            {!collapsed && <span className="flex-1">Portfolio</span>}
          </Link>

          {items.map((item) => {
            const active = pathname === item.url || pathname === `${item.url}/`;
            return (
              <Link
                key={item.title}
                to={item.url}
                title={item.title}
                className={cn(
                  "relative flex h-10 items-center gap-3 rounded-md px-3 text-sm transition-colors",
                  active
                    ? "bg-sidebar-accent text-foreground before:absolute before:-left-3 before:h-5 before:w-0.5 before:bg-primary"
                    : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-foreground",
                )}
              >
                <item.icon className={cn("h-4 w-4 shrink-0", active && "text-primary")} />
                {!collapsed && <span className="flex-1">{item.title}</span>}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="mt-auto border-t border-sidebar-border p-3">
        <div className={cn("flex items-center gap-2", collapsed && "justify-center")}>
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-violet-brand/15 text-[10px] font-semibold text-violet-brand">
            RB
          </div>
          {!collapsed && (
            <div className="min-w-0 flex-1">
              <div className="truncate text-xs font-medium">R. Boltzmann</div>
              <div className="truncate text-[9px] text-muted-foreground">
                Principal investigator
              </div>
            </div>
          )}
          <button
            onClick={() => setCollapsed((v) => !v)}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="rounded-md p-2 text-muted-foreground hover:bg-secondary hover:text-foreground"
          >
            <ChevronLeft className={cn("h-4 w-4 transition", collapsed && "rotate-180")} />
          </button>
        </div>
      </div>
    </aside>
  );
}
