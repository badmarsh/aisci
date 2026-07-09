import { createFileRoute } from "@tanstack/react-router";
import { BookMarked } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { PageShell } from "@/components/PageShell";
import { tasks, type Task } from "@/lib/mock-data";

export const Route = createFileRoute("/tasks")({
  head: () => ({
    meta: [
      { title: "Task Queue — AiSci" },
      {
        name: "description",
        content: "Active, blocked, and agent-proposed tasks in the AiSci autonomous research pipeline.",
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
  const active = tasks.filter((t) => t.status === "active");
  const blocked = tasks.filter((t) => t.status === "blocked");
  const proposed = tasks.filter((t) => t.status === "proposed");

  return (
    <PageShell>
      <Tabs defaultValue="active">
        <TabsList className="bg-muted/40">
          <TabsTrigger value="active">🟢 Active ({active.length})</TabsTrigger>
          <TabsTrigger value="blocked">⏸ Blocked ({blocked.length})</TabsTrigger>
          <TabsTrigger value="proposed">🤖 Agent-Proposed ({proposed.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="active">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {active.map((t) => (
              <TaskCard key={t.id} t={t} />
            ))}
          </div>
        </TabsContent>
        <TabsContent value="blocked">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {blocked.map((t) => (
              <TaskCard key={t.id} t={t} />
            ))}
          </div>
        </TabsContent>
        <TabsContent value="proposed">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {proposed.map((t) => (
              <TaskCard key={t.id} t={t} proposed />
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}

function TaskCard({ t, proposed }: { t: Task; proposed?: boolean }) {
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
      </CardContent>
    </Card>
  );
}
