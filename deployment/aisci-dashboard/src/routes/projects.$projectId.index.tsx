import { createFileRoute } from "@tanstack/react-router";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import {
  BookOpen,
  Atom,
  ShieldCheck,
  ListTodo,
  ArrowUpRight,
  AlertTriangle,
  Copy,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Link } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { PageShell } from "@/components/PageShell";
import { type Activity, type Anomaly } from "@/lib/types";
import { useQuery } from "@tanstack/react-query";
import {
  fetchLiterature,
  fetchFits,
  fetchEvidence,
  fetchTasks,
  fetchActivity,
  fetchAnomalies,
  fetchExportSummary,
} from "@/lib/api";
import { useState } from "react";
import { toast } from "sonner";

export const Route = createFileRoute("/projects/$projectId/")({
  head: () => ({
    meta: [
      { title: "Overview — AiSci" },
      {
        name: "description",
        content:
          "High-level status of the AiSci autonomous research pipeline: papers ingested, active fits, claims tracked, and open tasks.",
      },
    ],
  }),
  component: Overview,
});

type Kpi = {
  label: string;
  value: string;
  sub: string;
  Icon: typeof BookOpen;
  accent: string;
  badge?: { text: string; className: string };
};

function Overview() {
  const { projectId } = Route.useParams();
  const [showAnomalies, setShowAnomalies] = useState(false);
  
  const { data: literature = [] } = useQuery({
    queryKey: ["literature", projectId],
    queryFn: () => fetchLiterature(projectId),
  });
  const { data: fitsData = { fitRows: [], chi2Series: [] } as any } = useQuery({
    queryKey: ["fits", projectId],
    queryFn: () => fetchFits(projectId),
  });
  const { data: evidence = [] } = useQuery({ 
    queryKey: ["evidence", projectId], 
    queryFn: () => fetchEvidence(projectId) 
  });
  const { data: tasks = [] } = useQuery({ 
    queryKey: ["tasks", projectId], 
    queryFn: () => fetchTasks(projectId) 
  });
  const { data: activityFeed = [] } = useQuery({ 
    queryKey: ["activity"], 
    queryFn: fetchActivity 
  });

  const { data: anomalies = [] } = useQuery({
    queryKey: ["anomalies", projectId],
    queryFn: () => fetchAnomalies(projectId),
    staleTime: 60_000,
  });

  const criticalCount = anomalies.filter((a: Anomaly) => a.severity === "critical").length;
  const warningCount = anomalies.filter((a: Anomaly) => a.severity === "warning").length;

  async function handleExport() {
    try {
      const { markdown } = await fetchExportSummary(projectId);
      await navigator.clipboard.writeText(markdown);
      toast.success("Summary copied to clipboard!", {
        description: "Paste it into a GitHub Issue or research log.",
      });
    } catch {
      toast.error("Failed to export summary.");
    }
  }

  const kpis: Kpi[] = [
    {
      label: "Papers Ingested",
      value: String(literature.length),
      sub: "+0 today",
      Icon: BookOpen,
      accent: "text-emerald-brand",
    },
    {
      label: "Active Fits",
      value: String(fitsData.fitRows?.length || 0),
      sub: "bins across models",
      Icon: Atom,
      accent: "text-primary",
      badge: {
        text: "RUNNING",
        className: "bg-primary/15 text-primary ring-1 ring-primary/40",
      },
    },
    {
      label: "Claims Tracked",
      value: String(evidence.length),
      sub: `${evidence.filter((e: any) => e.status === "Proposed").length} pending review`,
      Icon: ShieldCheck,
      accent: "text-amber-brand",
    },
    {
      label: "Open Tasks",
      value: String(tasks.filter((t: any) => t.status !== "closed").length),
      sub: `${tasks.filter((t: any) => t.status === "proposed").length} agent-proposed`,
      Icon: ListTodo,
      accent: "text-primary",
    },
  ];

  return (
    <PageShell>
      <div className="mb-4 flex justify-end">
        <Button variant="outline" size="sm" className="gap-1.5" onClick={handleExport}>
          <Copy className="h-3.5 w-3.5" />
          Export Summary
        </Button>
      </div>

      {anomalies.length > 0 && (
        <Alert className="mb-4 glass-card border-rose-brand/40">
          <AlertTriangle className="h-4 w-4 text-rose-brand" />
          <AlertTitle className="flex items-center justify-between">
            <span className="text-rose-brand">
              {criticalCount > 0 ? `${criticalCount} critical` : ""}
              {criticalCount > 0 && warningCount > 0 ? " · " : ""}
              {warningCount > 0 ? `${warningCount} warnings` : ""} — physics anomalies in latest run
            </span>
            <button
              className="ml-4 text-xs underline text-muted-foreground hover:text-foreground"
              onClick={() => setShowAnomalies((s) => !s)}
            >
              {showAnomalies ? "Hide" : "Show details"}
            </button>
          </AlertTitle>
          {showAnomalies && (
            <AlertDescription className="mt-2">
              <ul className="space-y-0.5 text-xs font-mono">
                {anomalies.slice(0, 8).map((a: Anomaly, i: number) => (
                  <li
                    key={i}
                    className={a.severity === "critical" ? "text-rose-brand" : "text-amber-brand"}
                  >
                    [{a.bin}] {a.model}: {a.message}
                  </li>
                ))}
                {anomalies.length > 8 && (
                  <li className="text-muted-foreground">
                    …and {anomalies.length - 8} more.{" "}
                    <Link to="/projects/$projectId/fits" params={{ projectId }} className="underline">
                      Go to Fits page.
                    </Link>
                  </li>
                )}
              </ul>
            </AlertDescription>
          )}
        </Alert>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((k) => (
          <Card key={k.label} className="glass-card fade-in-up transition hover:border-primary/40">
            <CardHeader className="flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                {k.label}
              </CardTitle>
              <k.Icon className={`h-4 w-4 ${k.accent}`} />
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold tracking-tight">{k.value}</span>
                {k.badge && <Badge className={k.badge.className}>{k.badge.text}</Badge>}
              </div>
              <div className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
                {k.label === "Papers Ingested" && (
                  <ArrowUpRight className="h-3 w-3 text-emerald-brand" />
                )}
                {k.sub}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="glass-card fade-in-up lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Model χ²/ndf Across Multiplicity Bins</CardTitle>
            <p className="text-xs text-muted-foreground">
              Rejection threshold at χ²/ndf = 5 (dashed). Jüttner 1c fails the Boltzmann
              approximation across all bins.
            </p>
          </CardHeader>
          <CardContent>
            <div className="h-[360px] w-full">
              <ResponsiveContainer>
                <LineChart
                  data={fitsData.chi2Series || []}
                  margin={{ top: 10, right: 20, left: 0, bottom: 5 }}
                >
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                  <XAxis
                    dataKey="bin"
                    tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                    stroke="var(--border)"
                  />
                  <YAxis
                    tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                    stroke="var(--border)"
                    scale="log"
                    domain={[0.5, 500]}
                    ticks={[1, 5, 10, 50, 100, 500]}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "var(--popover)",
                      border: "1px solid var(--border)",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                    labelStyle={{ color: "var(--foreground)", fontWeight: 600 }}
                  />
                  <Legend
                    verticalAlign="top"
                    align="right"
                    wrapperStyle={{ fontSize: 12, paddingBottom: 8 }}
                  />
                  <ReferenceLine
                    y={5}
                    stroke="var(--rose-brand)"
                    strokeDasharray="4 4"
                    label={{
                      value: "Rejection Threshold",
                      position: "insideTopRight",
                      fill: "var(--rose-brand)",
                      fontSize: 11,
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="Jüttner 1c"
                    stroke="var(--rose-brand)"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="Tsallis 2c"
                    stroke="var(--emerald-brand)"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="Bose-Einstein 1c"
                    stroke="var(--primary)"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card fade-in-up">
          <CardHeader>
            <CardTitle className="text-base">Recent Activity</CardTitle>
            <p className="text-xs text-muted-foreground">Agent events, most recent first.</p>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[360px] pr-3">
              <ul className="space-y-2">
                {activityFeed.map((e: Activity) => {
                  let colorClass = "bg-primary";
                  if (
                    e.action.toLowerCase().includes("flagged") ||
                    e.action.toLowerCase().includes("error")
                  ) {
                    colorClass = "bg-rose-brand";
                  } else if (e.action.toLowerCase().includes("proposed")) {
                    colorClass = "bg-amber-brand";
                  } else if (
                    e.action.toLowerCase().includes("complete") ||
                    e.action.toLowerCase().includes("updated")
                  ) {
                    colorClass = "bg-emerald-brand";
                  }

                  // format timestamp to time only if today
                  const t = new Date(e.timestamp);
                  const timeStr = t.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

                  return (
                    <li
                      key={e.id}
                      className="group flex gap-3 rounded-md border border-transparent p-2 transition hover:border-border hover:bg-muted/40"
                    >
                      <span
                        className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${colorClass} ring-2 ring-background`}
                      />
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[11px] text-muted-foreground">
                            {timeStr}
                          </span>
                        </div>
                        <p className="text-sm leading-snug text-foreground/90">
                          <strong>{e.action}</strong>: {e.details}
                        </p>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </PageShell>
  );
}
