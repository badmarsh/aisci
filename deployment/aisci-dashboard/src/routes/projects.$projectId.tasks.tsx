import { createFileRoute } from "@tanstack/react-router";
import { toast } from "sonner";
import { BookMarked } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { PageShell } from "@/components/PageShell";
import { type Task } from "@/lib/types";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchTasks, updateTask, syncFromFiles } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/projects/$projectId/tasks")({
  head: () => ({
    meta: [
      { title: "Task Queue — AiSci" },
      {
        name: "description",
        content:
          "Active, blocked, and agent-proposed tasks in the AiSci autonomous research pipeline.",
      },
    ],
  }),
  component: TasksPage,
});

const priorityStyles: Record<Task["priority"], string> = {
  HIGH: "bg-rose-brand/15 text-rose-brand ring-1 ring-rose-brand/40",
  MEDIUM: "bg-amber-brand/15 text-amber-brand ring-1 ring-amber-brand/40",
  LOW: "bg-muted text-muted-foreground ring-1 ring-border",
};

function TasksPage() {
  const queryClient = useQueryClient();
  const { projectId } = Route.useParams();

  const {
    data: tasks = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["tasks", projectId],
    queryFn: () => fetchTasks(projectId),
  });

  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => updateTask(projectId, id, status),
    onSuccess: (_, { status }) => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["activity"] });
      toast.success(`Task marked as ${status}`, {
        description: "next-actions.md updated.",
      });
    },
    onError: () => {
      toast.error("Failed to update task status.");
    },
  });

  const syncMutation = useMutation({
    mutationFn: () => syncFromFiles(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Synced from canonical files.");
    },
    onError: () => {
      toast.error("Sync failed. Check the API logs.");
    },
  });

  const active = tasks.filter((t: Task) => t.status === "active");
  const blocked = tasks.filter((t: Task) => t.status === "blocked");
  const proposed = tasks.filter((t: Task) => t.status === "proposed");

  if (isLoading) {
    return (
      <PageShell>
        <Skeleton className="h-[200px] w-full" />
      </PageShell>
    );
  }

  if (isError) {
    return (
      <PageShell>
        <div className="text-rose-brand">Error loading tasks.</div>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <Tabs defaultValue="active">
        <div className="mb-4 flex items-center justify-between">
          <TabsList className="bg-muted/40">
            <TabsTrigger value="active">🟢 Active ({active.length})</TabsTrigger>
            <TabsTrigger value="blocked">⏸ Blocked ({blocked.length})</TabsTrigger>
            <TabsTrigger value="proposed">🤖 Agent-Proposed ({proposed.length})</TabsTrigger>
          </TabsList>
          <Button
            variant="outline"
            size="sm"
            disabled={syncMutation.isPending}
            onClick={() => syncMutation.mutate()}
          >
            Sync from Files
          </Button>
        </div>

        <TabsContent value="active">
          {active.length === 0 && (
            <div className="rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
              No active tasks.
            </div>
          )}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {active.map((t: Task) => (
              <TaskCard key={t.id} t={t} mutation={mutation} />
            ))}
          </div>
        </TabsContent>
        <TabsContent value="blocked">
          {blocked.length === 0 && (
            <div className="rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
              No blocked tasks.
            </div>
          )}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {blocked.map((t: Task) => (
              <TaskCard key={t.id} t={t} mutation={mutation} />
            ))}
          </div>
        </TabsContent>
        <TabsContent value="proposed">
          {proposed.length === 0 && (
            <div className="rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
              No proposed tasks.
            </div>
          )}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {proposed.map((t: Task) => (
              <TaskCard key={t.id} t={t} proposed mutation={mutation} />
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}

function TaskCard({ t, proposed, mutation }: { t: Task; proposed?: boolean; mutation?: any }) {
  return (
    <Card
      className={`glass-card fade-in-up transition hover:border-primary/40 ${
        proposed ? "border-amber-brand/50 ring-1 ring-amber-brand/20" : ""
      }`}
    >
      {proposed && (
        <div className="border-b border-amber-brand/40 bg-amber-brand/10 px-4 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-amber-brand">
          🤖 Pending Approval
        </div>
      )}
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-sm font-semibold leading-snug">{t.title}</CardTitle>
          <Badge className={priorityStyles[t.priority]}>{t.priority}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="line-clamp-3 text-xs leading-relaxed text-muted-foreground">
          {t.description}
        </p>
        {t.citation && (
          <div className="mt-3 flex items-center gap-1.5 rounded-md border border-border bg-muted/40 px-2 py-1 text-[11px] text-muted-foreground">
            <BookMarked className="h-3 w-3 text-primary" /> {t.citation}
          </div>
        )}
        <div className="mt-4 flex items-center justify-between text-[11px] text-muted-foreground">
          <div className="flex items-center gap-2">
            <Avatar className="h-6 w-6 ring-1 ring-border">
              <AvatarFallback
                className={`text-[10px] font-semibold ${
                  t.assignee === "AI"
                    ? "bg-primary/15 text-primary"
                    : "bg-emerald-brand/15 text-emerald-brand"
                }`}
              >
                {t.assignee}
              </AvatarFallback>
            </Avatar>
            <span>{t.assignee === "AI" ? "Agent" : "Robert"}</span>
          </div>
          <span className="font-mono">{t.date}</span>
        </div>
        {proposed && (
          <div className="mt-3">
            <Button
              variant="outline"
              size="sm"
              disabled={mutation?.isPending}
              onClick={() => mutation?.mutate({ id: t.id, status: "active" })}
            >
              Approve to Active
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
