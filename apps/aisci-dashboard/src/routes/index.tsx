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
import { BookOpen, Atom, ShieldCheck, ListTodo, ArrowUpRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { PageShell } from "@/components/PageShell";
import { chi2Series, activityFeed } from "@/lib/mock-data";

export const Route = createFileRoute("/")({
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

const kpis: Kpi[] = [
  {
    label: "Papers Ingested",
    value: "312",
    sub: "+8 today",
    Icon: BookOpen,
    accent: "text-emerald-brand",
  },
  {
    label: "Active Fits",
    value: "10",
    sub: "bins across 3 models",
    Icon: Atom,
    accent: "text-primary",
    badge: {
      text: "RUNNING",
      className: "bg-primary/15 text-primary ring-1 ring-primary/40",
    },
  },
  {
    label: "Claims Tracked",
    value: "47",
    sub: "12 pending review",
    Icon: ShieldCheck,
    accent: "text-amber-brand",
  },
  {
    label: "Open Tasks",
    value: "6",
    sub: "2 agent-proposed",
    Icon: ListTodo,
    accent: "text-primary",
  },
];

function Overview() {
  return (
    <PageShell>
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
                {k.badge && (
                  <Badge className={k.badge.className}>{k.badge.text}</Badge>
                )}
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
            <CardTitle className="text-base">
              Model χ²/ndf Across Multiplicity Bins
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Rejection threshold at χ²/ndf = 5 (dashed). Jüttner 1c fails the Boltzmann
              approximation across all bins.
            </p>
          </CardHeader>
          <CardContent>
            <div className="h-[360px] w-full">
              <ResponsiveContainer>
                <LineChart data={chi2Series} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
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
                {activityFeed.map((e, i) => {
                  const dot: Record<string, string> = {
                    emerald: "bg-emerald-brand",
                    cyan: "bg-primary",
                    amber: "bg-amber-brand",
                    rose: "bg-rose-brand",
                  };
                  return (
                    <li
                      key={i}
                      className="group flex gap-3 rounded-md border border-transparent p-2 transition hover:border-border hover:bg-muted/40"
                    >
                      <span
                        className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${dot[e.color]} ring-2 ring-background`}
                      />
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[11px] text-muted-foreground">
                            {e.time}
                          </span>
                        </div>
                        <p className="text-sm leading-snug text-foreground/90">{e.text}</p>
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
