import { Link, useRouterState, useParams } from "@tanstack/react-router";
import {
  Home,
  Atom,
  BookOpen,
  ShieldCheck,
  ListTodo,
  Bot,
  Moon,
  Sun,
  AlertTriangle,
  FolderTree,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const pathname = useRouterState({ select: (r) => r.location.pathname });
  
  const { projectId } = useParams({ strict: false }) as { projectId?: string };
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    if (dark) root.classList.add("dark");
    else root.classList.remove("dark");
  }, [dark]);

  const items = projectId ? [
    { title: "Overview", url: `/projects/${projectId}`, icon: Home },
    { title: "Physics Fits", url: `/projects/${projectId}/fits`, icon: Atom },
    { title: "Literature Intake", url: `/projects/${projectId}/literature`, icon: BookOpen },
    { title: "Evidence Ledger", url: `/projects/${projectId}/evidence`, icon: ShieldCheck },
    { title: "Task Queue", url: `/projects/${projectId}/tasks`, icon: ListTodo },
    { title: "Anomalies", url: `/projects/${projectId}/anomalies`, icon: AlertTriangle },
    { title: "Agents", url: `/projects/${projectId}/agents`, icon: Bot },
  ] : [];

  return (
    <Sidebar collapsible="icon" className="border-r border-sidebar-border">
      <SidebarHeader className="border-b border-sidebar-border">
        <div className="flex items-center gap-2.5 px-2 py-2">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 ring-1 ring-primary/30">
            <AtomLogo />
          </div>
          {!collapsed && (
            <div className="flex flex-col leading-tight">
              <span className="text-base font-bold tracking-tight">AiSci</span>
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                Autonomous Research System
              </span>
            </div>
          )}
        </div>
        {!collapsed && (
          <div className="px-2 pb-2">
            <Badge className="w-full justify-center bg-emerald-brand/15 text-emerald-brand ring-1 ring-emerald-brand/40 hover:bg-emerald-brand/15">
              <span className="mr-1.5 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-brand" />
              NOMINAL
            </Badge>
          </div>
        )}
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={pathname === "/"} tooltip="Portfolio">
                  <Link to="/" className="flex flex-1 items-center gap-2">
                    <FolderTree className="h-4 w-4" />
                    <span>Portfolio</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              {items.map((item) => {
                // Ensure exact match for overview, or prefix match?
                // Just use simple logic or exact match
                const active = pathname === item.url || pathname === `${item.url}/`;
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton asChild isActive={active} tooltip={item.title}>
                      <div className="flex w-full items-center justify-between group">
                        {/* We use standard a href because Link to dynamic route string might be unhappy with TS unless type is ignored */}
                        <Link to={item.url as any} className="flex flex-1 items-center gap-2">
                          <item.icon className="h-4 w-4" />
                          <span>{item.title}</span>
                        </Link>
                      </div>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setDark(!dark)}
          className="h-8 w-8 text-muted-foreground hover:text-foreground"
        >
          {dark ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
        </Button>
      </SidebarFooter>
    </Sidebar>
  );
}

function AtomLogo() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-5 w-5 text-primary"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
    >
      <circle cx="12" cy="12" r="1.6" fill="currentColor" />
      <ellipse cx="12" cy="12" rx="9" ry="3.5" />
      <ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(60 12 12)" />
      <ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(-60 12 12)" />
    </svg>
  );
}
