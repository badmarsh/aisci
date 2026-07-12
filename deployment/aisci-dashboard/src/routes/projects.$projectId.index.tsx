import type { ReactNode } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  ReferenceLine,
} from "recharts";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  Bot,
  CheckCircle2,
  Database,
  Radio,
  Sigma,
  BookOpen,
  Atom,
  ShieldCheck,
  ListTodo,
  Copy,
} from "lucide-react";
import {
  fetchActivity,
  fetchAnomalies,
  fetchFits,
  fetchProjectOverview,
  fetchProjectHealth,
  fetchExportSummary,
} from "@/lib/api";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { PageShell } from "@/components/PageShell";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/projects/$projectId/")({
  head: () => ({
    meta: [
      { title: "Overview — AiSci" },
      { name: "description", content: "AiSci autonomous physics research control plane" },
    ],
  }),
  component: Overview,
});

function Overview() {
  const { projectId } = Route.useParams();

  const { data: fitsData = { fitRows: [], chi2Series: [] } as any } = useQuery({
    queryKey: ["fits", projectId],
    queryFn: () => fetchFits(projectId),
  });
  const { data: activityFeed = [] } = useQuery({
    queryKey: ["activity", projectId],
    queryFn: () => fetchActivity(projectId),
  });
  const { data: anomalies = [] } = useQuery({
    queryKey: ["anomalies", projectId],
    queryFn: () => fetchAnomalies(projectId),
    staleTime: 60_000,
  });
  const {
    data: overview = { literature_count: 0, active_fits: 0, claims_count: 0, open_tasks: 0 } as any,
  } = useQuery({
    queryKey: ["overview", projectId],
    queryFn: () => fetchProjectOverview(projectId),
  });
  const { data: health } = useQuery({
    queryKey: ["health", projectId],
    queryFn: () => fetchProjectHealth(projectId),
  });

  const metrics: import("@/lib/api").Metric[] = [
    {
      label: "Papers Ingested",
      value: String(overview.literature_count),
      delta: 0,
      accent: "emerald",
      spark: [2, 4, 3, 5, 4, 6],
    },
    {
      label: "Active Fits",
      value: String(overview.active_fits),
      delta: 0,
      accent: "cyan",
      spark: [10, 15, 12, 18, 20],
    },
    {
      label: "Claims Tracked",
      value: String(overview.claims_count),
      delta: 0,
      accent: "amber",
      spark: [1, 2, 2, 3, 4],
    },
    {
      label: "Open Tasks",
      value: String(overview.open_tasks),
      delta: 0,
      accent: "violet",
      spark: [10, 8, 9, 6, 5],
    },
  ];

  async function handleExport() {
    try {
      const { markdown } = await fetchExportSummary(projectId);
      await navigator.clipboard.writeText(markdown);
      toast.success("Summary copied to clipboard!");
    } catch {
      toast.error("Failed to export summary.");
    }
  }

  return (
    <PageShell>
      <section className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-primary">
            <Radio className="h-3.5 w-3.5" /> Live research fabric
          </div>
          <h1 className="text-balance text-3xl font-semibold tracking-tight md:text-4xl">
            Scientific operations overview
          </h1>
          <p className="max-w-2xl text-pretty text-sm leading-6 text-muted-foreground">
            Autonomous agents are ingesting evidence, fitting collision spectra, and validating
            physical claims across the active research graph.
          </p>
        </div>
        <div className="flex items-center gap-3 border-l border-primary/40 pl-4">
          <Button variant="outline" size="sm" className="gap-1.5" onClick={handleExport}>
            <Copy className="h-3.5 w-3.5" /> Export
          </Button>
          <div className="h-8 w-px bg-border" />
          <div>
            <div className="font-mono text-xl font-semibold text-emerald-brand">99.98%</div>
            <div className="text-xs text-muted-foreground">pipeline uptime</div>
          </div>
        </div>
      </section>

      <section aria-label="Research metrics" className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => (
          <MetricCard key={metric.label} metric={metric} />
        ))}
      </section>

      <section className="mt-4 grid gap-4 xl:grid-cols-12">
        <Panel
          className="xl:col-span-7"
          title="Model χ²/ndf vs Multiplicity"
          label="Tsallis & Jüttner fits"
          icon={Sigma}
          action="Latest"
        >
          <div className="mt-4 h-72" aria-label="Chart showing chi2 over bins">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={fitsData.chi2Series || []}
                margin={{ top: 8, right: 8, left: -24, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="fit-fill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--cyan-brand)" stopOpacity={0.28} />
                    <stop offset="100%" stopColor="var(--cyan-brand)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 5" vertical={false} />
                <XAxis
                  dataKey="bin"
                  tick={{ fill: "var(--muted-foreground)", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  scale="log"
                  domain={[0.5, 500]}
                  ticks={[1, 5, 10, 50, 100, 500]}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    background: "var(--popover)",
                    border: "1px solid var(--border)",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
                <ReferenceLine y={5} stroke="var(--rose-brand)" strokeDasharray="4 4" />
                <Area
                  type="monotone"
                  dataKey="Tsallis 2c"
                  stroke="var(--emerald-brand)"
                  fill="url(#fit-fill)"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="Jüttner 1c"
                  stroke="var(--rose-brand)"
                  strokeWidth={1.5}
                  dot={true}
                />
                <Line
                  type="monotone"
                  dataKey="Bose-Einstein 1c"
                  stroke="var(--primary)"
                  strokeWidth={1.5}
                  dot={true}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="flex gap-5 border-t border-border pt-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-2">
              <i className="h-1.5 w-4 bg-emerald-brand" />
              Tsallis
            </span>
            <span className="flex items-center gap-2">
              <i className="h-1.5 w-4 bg-rose-brand" />
              Jüttner
            </span>
            <span className="flex items-center gap-2">
              <i className="h-1.5 w-4 bg-primary" />
              Bose-Einstein
            </span>
          </div>
        </Panel>

        <Panel
          className="xl:col-span-5"
          title="Agent workload"
          label="Distributed cognition mesh"
          icon={Bot}
          action={`Active`}
        >
          <div className="mt-3 flex flex-col divide-y divide-border">
            {[
              {
                id: 1,
                status: "active",
                name: "Literature Ingest",
                load: 85,
                role: "extraction",
                throughput: "12 papers/h",
              },
              {
                id: 2,
                status: "active",
                name: "Minuit Fitter",
                load: 92,
                role: "compute",
                throughput: "244 fits/m",
              },
              {
                id: 3,
                status: "blocked",
                name: "Peer Reviewer",
                load: 15,
                role: "validation",
                throughput: "idle",
              },
            ].map((agent) => (
              <div key={agent.id} className="flex items-center gap-3 py-3">
                <span
                  className={cn(
                    "h-2 w-2 rounded-full",
                    agent.status === "active"
                      ? "bg-emerald-brand"
                      : agent.status === "blocked"
                        ? "bg-amber-brand"
                        : "bg-muted-foreground",
                  )}
                />
                <div className="min-w-0 flex-1">
                  <div className="flex justify-between gap-3">
                    <span className="text-sm font-medium">{agent.name}</span>
                    <span className="font-mono text-[11px] text-muted-foreground">
                      {agent.load}%
                    </span>
                  </div>
                  <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full bg-primary transition-all"
                      style={{ width: `${agent.load}%` }}
                    />
                  </div>
                  <div className="mt-1 flex justify-between text-[10px] text-muted-foreground">
                    <span>{agent.role}</span>
                    <span>{agent.throughput}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel
          className="xl:col-span-4"
          title="Database sync"
          label="Primary ledger"
          icon={Database}
          action="synced"
        >
          <div className="mt-5 flex items-end justify-between">
            <strong className="font-mono text-4xl font-medium">100%</strong>
            <span className="text-xs text-muted-foreground">Local records</span>
          </div>
          <div className="mt-4 h-2 overflow-hidden rounded-full bg-secondary">
            <div
              className="h-full bg-primary shadow-[0_0_12px_var(--cyan-brand)]"
              style={{ width: `100%` }}
            />
          </div>
          <dl className="mt-5 grid grid-cols-2 gap-3 border-t border-border pt-4 text-xs">
            <div>
              <dt className="text-muted-foreground">Read latency</dt>
              <dd className="mt-1 font-mono text-foreground">12 ms</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Replica state</dt>
              <dd className="mt-1 flex items-center gap-1.5 text-emerald-brand">
                <CheckCircle2 className="h-3 w-3" />
                Consistent
              </dd>
            </div>
          </dl>
        </Panel>

        <Panel
          className="xl:col-span-4"
          title="Anomaly queue"
          label="Residual scan deviations"
          icon={AlertTriangle}
          action={`${anomalies?.length ?? 0} open`}
        >
          <div className="mt-3 flex flex-col divide-y divide-border">
            {anomalies?.slice(0, 4).map((a: any, i: number) => (
              <div key={`${a.bin}-${a.model}-${i}`} className="group flex items-center gap-3 py-3">
                <div
                  className={cn(
                    "flex h-8 w-8 items-center justify-center rounded-md font-mono text-xs",
                    a.severity === "high" || a.severity === "critical"
                      ? "bg-amber-brand/15 text-amber-brand"
                      : "bg-secondary text-muted-foreground",
                  )}
                >
                  !
                </div>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-medium">
                    [{a.bin}] {a.model}
                  </div>
                  <div className="truncate font-mono text-[10px] text-muted-foreground">
                    {a.message}
                  </div>
                </div>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground transition group-hover:text-primary" />
              </div>
            ))}
          </div>
        </Panel>

        <Panel
          className="xl:col-span-4"
          title="Activity stream"
          label="Latest agent events"
          icon={Activity}
          action="Live"
        >
          <div className="mt-3 flex max-h-64 flex-col overflow-auto scroll-slim">
            {activityFeed?.slice(0, 5).map((item: any, index: number) => (
              <div key={item.id} className="relative flex gap-3 pb-4 last:pb-0">
                <div className="flex flex-col items-center">
                  <span className="mt-1 h-2 w-2 rounded-full bg-primary" />
                  {index < 4 && <span className="mt-1 w-px flex-1 bg-border" />}
                </div>
                <div>
                  <div className="text-xs font-semibold">{item.action}</div>
                  <p className="mt-1 text-[11px] leading-5 text-muted-foreground">{item.details}</p>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </section>
    </PageShell>
  );
}

function Panel({
  title,
  label,
  icon: Icon,
  action,
  className,
  children,
}: {
  title: string;
  label: string;
  icon: typeof Activity;
  action: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <article
      className={cn(
        "glass-card rounded-xl p-4 transition-colors hover:border-primary/25",
        className,
      )}
    >
      <header className="flex items-start justify-between gap-3">
        <div className="flex gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <Icon className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold">{title}</h2>
            <p className="mt-0.5 text-[11px] text-muted-foreground">{label}</p>
          </div>
        </div>
        <span className="rounded-md border border-border bg-secondary/60 px-2 py-1 font-mono text-[10px] uppercase text-muted-foreground">
          {action}
        </span>
      </header>
      {children}
    </article>
  );
}
