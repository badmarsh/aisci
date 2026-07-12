import { useRouterState, useParams } from "@tanstack/react-router";
import { Bell, Loader2, Play, Keyboard } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { triggerPipeline, fetchActivity } from "@/lib/api";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { LogDrawer } from "@/components/LogDrawer";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";

const titles: Record<string, { title: string; crumb: string }> = {
  "/": { title: "Overview", crumb: "Dashboard / Overview" },
  "/fits": { title: "Physics Fits", crumb: "Dashboard / Physics Fits" },
  "/literature": { title: "Literature Intake", crumb: "Dashboard / Literature Intake" },
  "/evidence": { title: "Evidence Ledger", crumb: "Dashboard / Evidence Ledger" },
  "/tasks": { title: "Task Queue", crumb: "Dashboard / Task Queue" },
  "/agents": { title: "Agents", crumb: "Dashboard / Agents" },
};

export function AppHeader() {
  const pathname = useRouterState({ select: (r) => r.location.pathname });
  const meta = titles[pathname] ?? { title: "AiSci", crumb: "Dashboard" };
  const queryClient = useQueryClient();
  const [logTarget, setLogTarget] = useState<"ingest" | "fits" | null>(null);
  const [hasReadNotifications, setHasReadNotifications] = useState(false);
  
  // Extract projectId if available in the route
  const { projectId } = useParams({ strict: false }) as { projectId?: string };

  const { data: activityFeed = [] } = useQuery({
    queryKey: ["activity", projectId],
    queryFn: () => projectId ? fetchActivity(projectId) : Promise.resolve([]),
    staleTime: 10_000,
    enabled: !!projectId,
  });

  const recentCount = activityFeed.length;
  const recentActivities = activityFeed.slice(0, 10);

  const ingestMutation = useMutation({
    mutationFn: () => triggerPipeline(projectId!, "ingest-validation"), // Note: need to register ingest pipeline in pipelines.py if used
    onSuccess: (data) => {
      toast.success("Ingest complete.", { description: data.message });
      queryClient.invalidateQueries({ queryKey: ["literature", projectId] });
    },
    onError: () => {
      toast.error("Ingest failed.");
    },
  });

  const fitsMutation = useMutation({
    mutationFn: () => triggerPipeline(projectId!, "fit-validation"),
    onSuccess: (data) => {
      toast.success("Fits complete.", { description: data.message });
      queryClient.invalidateQueries({ queryKey: ["fits", projectId] });
      queryClient.invalidateQueries({ queryKey: ["anomalies", projectId] });
    },
    onError: () => {
      toast.error("Fits failed.");
    },
  });

  function runIngest() {
    if (!projectId) return;
    toast("Ingest pipeline started.", {
      description: "Fetching from arXiv + OpenAlex...",
    });
    setLogTarget("ingest");
    ingestMutation.mutate();
  }

  function runFits() {
    if (!projectId) return;
    toast("Fits pipeline started.", {
      description: "Running fit_quality script...",
    });
    setLogTarget("fits");
    fitsMutation.mutate();
  }

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur-md">
      <SidebarTrigger />
      <Separator orientation="vertical" className="h-6" />
      <div className="flex flex-col leading-tight">
        <h1 className="text-sm font-semibold tracking-tight">{meta.title}</h1>
        <span className="text-[11px] text-muted-foreground">{meta.crumb}</span>
      </div>

      <div className="ml-auto flex items-center gap-2">
        {projectId && (
          <>
            <Button
              onClick={runIngest}
              disabled={ingestMutation.isPending}
              size="sm"
              className="gap-1.5 bg-primary text-primary-foreground hover:bg-primary/90"
            >
              {ingestMutation.isPending ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Play className="h-3.5 w-3.5" />
              )}
              {ingestMutation.isPending ? "Running Ingest…" : "Run Ingest"}
            </Button>
            <Button
              onClick={runFits}
              disabled={fitsMutation.isPending}
              size="sm"
              variant="outline"
              className="gap-1.5"
            >
              {fitsMutation.isPending ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Play className="h-3.5 w-3.5" />
              )}
              {fitsMutation.isPending ? "Running Fits…" : "Run Fits"}
            </Button>
          </>
        )}
        <Popover
          onOpenChange={(open) => {
            if (open) setHasReadNotifications(true);
          }}
        >
          <PopoverTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-4 w-4" />
              {recentCount > 0 && !hasReadNotifications && (
                <Badge className="absolute -right-0.5 -top-0.5 h-4 min-w-4 justify-center rounded-full bg-rose-brand p-0 px-1 text-[10px] text-white">
                  {recentCount > 99 ? "99+" : recentCount}
                </Badge>
              )}
            </Button>
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
                  {recentActivities.map((item: any, i: number) => (
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
        <Avatar className="h-8 w-8 ring-1 ring-border">
          <AvatarFallback className="bg-primary/15 text-xs font-semibold text-primary">
            RB
          </AvatarFallback>
        </Avatar>
      </div>

      <LogDrawer target={logTarget} onClose={() => setLogTarget(null)} />
    </header>
  );
}
