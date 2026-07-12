import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { fetchProjectHealth, fetchJobs, fetchAnomalies } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageShell } from "@/components/PageShell";
import { Activity, BookOpen, AlertTriangle, Network, ShieldCheck, ListTodo, Copy, FileCode2 } from "lucide-react";

export const Route = createFileRoute("/projects/$projectId/")({
  head: () => ({
    meta: [
      { title: "Project Monitoring — AiSci" },
    ],
  }),
  component: ThinProjectOverview,
});

function ThinProjectOverview() {
  const { projectId } = Route.useParams();
  const navigate = useNavigate();

  const { data: health } = useQuery({
    queryKey: ["health", projectId],
    queryFn: () => fetchProjectHealth(projectId),
  });

  const { data: jobs = [] } = useQuery({
    queryKey: ["jobs", projectId],
    queryFn: () => fetchJobs(projectId),
  });

  const { data: anomalies = [] } = useQuery({
    queryKey: ["anomalies", projectId],
    queryFn: () => fetchAnomalies(projectId),
  });

  const recentJobs = jobs.slice(0, 5);
  const openAnomaliesCount = anomalies.filter((a: any) => a.status === "open").length;

  return (
    <PageShell>
      <div className="mb-6 flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h2 className="text-2xl font-bold tracking-tight">Project Status</h2>
            <div className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground flex items-center gap-1.5 border border-border/50 bg-secondary/30 px-2 py-0.5 rounded-sm">
              <span>{projectId}</span>
              <button className="hover:text-primary transition-colors" title="Copy ID">
                <Copy className="h-3 w-3" />
              </button>
            </div>
          </div>
          <p className="text-muted-foreground text-sm">
            High-level monitoring for legacy workflows. For active analysis, use the Paper Studio or Pipeline Catalog.
          </p>
        </div>
      </div>

      {/* Main KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card className="bg-sidebar">
          <CardHeader className="pb-2">
            <CardDescription>System Health</CardDescription>
            <CardTitle className="text-xl flex items-center gap-2 text-emerald-500">
              <Activity className="w-4 h-4" />
              {health?.status === "healthy" ? "Healthy" : "Degraded"}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card className="bg-sidebar">
          <CardHeader className="pb-2">
            <CardDescription>Recent Pipelines</CardDescription>
            <CardTitle className="text-xl font-mono">{recentJobs.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="bg-sidebar">
          <CardHeader className="pb-2">
            <CardDescription>Open Anomalies</CardDescription>
            <CardTitle className="text-xl font-mono text-amber-500">{openAnomaliesCount}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="bg-sidebar flex items-center justify-center p-4">
          <Button onClick={() => navigate({ to: "/" })} className="w-full h-full flex flex-col gap-2">
            <BookOpen className="w-5 h-5" />
            Go to Paper Triage
          </Button>
        </Card>
      </div>

      {/* Legacy Navigation Hub */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <h3 className="lg:col-span-3 text-lg font-semibold mt-4 border-b pb-2">Legacy Expert Views</h3>
        
        <Link to={`/projects/${projectId}/literature`} className="block">
          <Card className="hover:border-primary/50 transition">
            <CardHeader className="p-4">
              <CardTitle className="text-sm flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-primary" /> Literature Database
              </CardTitle>
            </CardHeader>
          </Card>
        </Link>
        <Link to={`/projects/${projectId}/evidence`} className="block">
          <Card className="hover:border-primary/50 transition">
            <CardHeader className="p-4">
              <CardTitle className="text-sm flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-primary" /> Evidence Ledger
              </CardTitle>
            </CardHeader>
          </Card>
        </Link>
        <Link to={`/projects/${projectId}/anomalies`} className="block">
          <Card className="hover:border-primary/50 transition">
            <CardHeader className="p-4">
              <CardTitle className="text-sm flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-primary" /> Anomaly Reports
              </CardTitle>
            </CardHeader>
          </Card>
        </Link>
        <Link to={`/projects/${projectId}/tasks`} className="block">
          <Card className="hover:border-primary/50 transition">
            <CardHeader className="p-4">
              <CardTitle className="text-sm flex items-center gap-2">
                <ListTodo className="w-4 h-4 text-primary" /> Task Queue
              </CardTitle>
            </CardHeader>
          </Card>
        </Link>
        <Link to={`/projects/${projectId}/jobs`} className="block">
          <Card className="hover:border-primary/50 transition">
            <CardHeader className="p-4">
              <CardTitle className="text-sm flex items-center gap-2">
                <FileCode2 className="w-4 h-4 text-primary" /> System Jobs
              </CardTitle>
            </CardHeader>
          </Card>
        </Link>
      </div>
    </PageShell>
  );
}
