import { createFileRoute } from "@tanstack/react-router";
import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, TrendingUp, HelpCircle, Activity, Settings2 } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

import { PageShell } from "@/components/PageShell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Slider } from "@/components/ui/slider";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { fetchFitRuns, fetchAnomalies } from "@/lib/api";
import type { Anomaly } from "@/lib/types";

export const Route = createFileRoute("/projects/$projectId/anomalies")({
  head: () => ({
    meta: [
      { title: "Physics Anomalies — AiSci" },
      {
        name: "description",
        content: "Specialized view for monitoring and discovering fit anomalies.",
      },
    ],
  }),
  component: AnomaliesPage,
});

const ARCHETYPES = [
  {
    type: "chi2",
    title: "High χ²/ndf",
    description: "Model rejection due to extremely high χ²/ndf.",
    Icon: AlertTriangle,
    color: "text-rose-brand",
    bg: "bg-rose-brand/10",
  },
  {
    type: "correlation",
    title: "Parameter Correlation",
    description: "Highly correlated parameters (|ρ| > threshold).",
    Icon: Activity,
    color: "text-amber-brand",
    bg: "bg-amber-brand/10",
  },
  {
    type: "boundary",
    title: "Boundary Conditions",
    description: "Fit parameters hitting physical limits.",
    Icon: HelpCircle,
    color: "text-cyan-brand",
    bg: "bg-cyan-brand/10",
  },
];

function AnomaliesPage() {
  const { data: runsData } = useQuery({
    queryKey: ["fitRuns"],
    queryFn: fetchFitRuns,
  });
  const runs = runsData?.runs || [];

  const [selectedRun, setSelectedRun] = useState<string | undefined>();
  const activeRun = selectedRun || (runs.length > 0 ? runs[0] : undefined);

  const {
    data: anomalies,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["anomalies", activeRun],
    queryFn: () => fetchAnomalies(activeRun),
    enabled: !!activeRun,
  });

  const { criticalCount, warningCount, typeCounts, chartData } = useMemo(() => {
    if (!anomalies) return { criticalCount: 0, warningCount: 0, typeCounts: {}, chartData: [] };
    let cCount = 0;
    let wCount = 0;
    const tCounts: Record<string, number> = {};
    const modelCounts: Record<string, any> = {};

    for (const a of anomalies) {
      if (a.severity === "critical") cCount++;
      else if (a.severity === "warning") wCount++;

      tCounts[a.type] = (tCounts[a.type] || 0) + 1;

      if (!modelCounts[a.model]) {
        modelCounts[a.model] = { name: a.model, Critical: 0, Warning: 0 };
      }

      if (a.severity === "critical") modelCounts[a.model].Critical++;
      if (a.severity === "warning") modelCounts[a.model].Warning++;
    }

    return {
      criticalCount: cCount,
      warningCount: wCount,
      typeCounts: tCounts,
      chartData: Object.values(modelCounts),
    };
  }, [anomalies]);

  return (
    <PageShell>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Physics Anomalies</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Monitor, discover, and adjust specialized physics failure archetypes.
          </p>
        </div>
        {runs.length > 0 && (
          <Select value={activeRun} onValueChange={(val) => setSelectedRun(val)}>
            <SelectTrigger className="w-[280px] font-mono text-xs glass-card">
              <SelectValue placeholder="Select run..." />
            </SelectTrigger>
            <SelectContent>
              {runs.map((r: string) => (
                <SelectItem key={r} value={r} className="font-mono text-xs">
                  {r}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 mb-6">
        <div className="xl:col-span-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          {ARCHETYPES.map((arch) => {
            const count = typeCounts[arch.type] || 0;
            return (
              <Card
                key={arch.type}
                className={`glass-card overflow-hidden border-l-4 transition-all hover:translate-y-[-2px] ${count > 0 ? "border-l-" + arch.color.split("-")[1] + "-brand" : "border-l-border"}`}
              >
                <CardHeader className="pb-2 flex flex-row items-start justify-between">
                  <div>
                    <CardTitle className="text-sm font-semibold">{arch.title}</CardTitle>
                    <CardDescription className="text-xs mt-1">{arch.description}</CardDescription>
                  </div>
                  <div className={`p-2 rounded-full ${arch.bg}`}>
                    <arch.Icon className={`h-4 w-4 ${arch.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {count}
                    <span className="text-sm font-normal text-muted-foreground ml-2">detected</span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {isLoading && (
        <div className="space-y-4">
          <Skeleton className="h-[300px] w-full" />
          <Skeleton className="h-[400px] w-full" />
        </div>
      )}

      {isError && (
        <Alert variant="destructive">
          <AlertTitle>Error loading anomalies</AlertTitle>
          <AlertDescription>Failed to fetch the anomaly data from the backend.</AlertDescription>
        </Alert>
      )}

      {anomalies && (
        <>
          <Card className="glass-card mb-6 fade-in-up" style={{ animationDelay: "0.1s" }}>
            <CardHeader>
              <CardTitle className="text-base">Archetype Scatter Plot</CardTitle>
              <CardDescription>
                Visualizing anomaly severity across multiplicity bins
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <RechartsTooltip
                      contentStyle={{
                        backgroundColor: "#000",
                        borderColor: "#333",
                        borderRadius: "6px",
                      }}
                      itemStyle={{ color: "#fff" }}
                    />
                    <Legend />
                    <Bar dataKey="Critical" fill="#f43f5e" />
                    <Bar dataKey="Warning" fill="#f59e0b" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card fade-in-up" style={{ animationDelay: "0.2s" }}>
            <CardHeader className="pb-3 border-b border-border/50">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  Anomaly Ledger
                </CardTitle>
                <div className="flex gap-2">
                  <Badge variant="outline" className="border-rose-brand/30 text-rose-brand">
                    {criticalCount} Critical
                  </Badge>
                  <Badge variant="outline" className="border-amber-brand/30 text-amber-brand">
                    {warningCount} Warning
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead className="w-[100px]">Severity</TableHead>
                    <TableHead>Multiplicity Bin</TableHead>
                    <TableHead>Model</TableHead>
                    <TableHead>Archetype</TableHead>
                    <TableHead>Value</TableHead>
                    <TableHead className="w-[40%]">Context & Message</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {anomalies.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                        No anomalies detected in this run with the current thresholds.
                      </TableCell>
                    </TableRow>
                  )}
                  {anomalies.map((anomaly: Anomaly, i: number) => (
                    <TableRow key={i} className="border-border hover:bg-muted/50 transition-colors">
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={
                            anomaly.severity === "critical"
                              ? "border-rose-brand/40 text-rose-brand bg-rose-brand/5"
                              : "border-amber-brand/40 text-amber-brand bg-amber-brand/5"
                          }
                        >
                          {anomaly.severity.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{anomaly.bin}</TableCell>
                      <TableCell>{anomaly.model}</TableCell>
                      <TableCell>
                        <span className="inline-flex items-center gap-1.5 text-sm capitalize">
                          {anomaly.type === "chi2" && (
                            <AlertTriangle className="h-3 w-3 text-rose-brand" />
                          )}
                          {anomaly.type === "correlation" && (
                            <Activity className="h-3 w-3 text-amber-brand" />
                          )}
                          {anomaly.type === "boundary" && (
                            <HelpCircle className="h-3 w-3 text-cyan-brand" />
                          )}
                          {anomaly.type}
                        </span>
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {anomaly.value.toFixed(2)}
                      </TableCell>
                      <TableCell className="font-mono text-xs leading-relaxed text-muted-foreground">
                        {anomaly.message}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      )}
    </PageShell>
  );
}

export default AnomaliesPage;
