import { Area, AreaChart, ResponsiveContainer } from "recharts";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import type { Metric } from "@/lib/api";
import { cn } from "@/lib/utils";

const accentVar: Record<Metric["accent"], string> = {
  cyan: "var(--cyan-brand)",
  amber: "var(--amber-brand)",
  emerald: "var(--emerald-brand)",
  violet: "var(--violet-brand)",
};

export function MetricCard({ metric }: { metric: Metric }) {
  const color = accentVar[metric.accent];
  const up = metric.delta >= 0;
  const data = metric.spark.map((v: number, i: number) => ({ i, v }));

  return (
    <div className="glass-card group relative overflow-hidden rounded-xl p-4 transition-all hover:-translate-y-0.5 hover:shadow-lg">
      <div
        className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full opacity-20 blur-2xl transition-opacity group-hover:opacity-40"
        style={{ background: color }}
        aria-hidden="true"
      />
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {metric.label}
        </span>
        <span
          className={cn(
            "flex items-center gap-0.5 rounded-full px-1.5 py-0.5 text-[10px] font-semibold",
            up ? "bg-emerald-brand/10 text-emerald-brand" : "bg-rose-brand/10 text-rose-brand",
          )}
        >
          {up ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
          {Math.abs(metric.delta)}%
        </span>
      </div>
      <div className="mt-2 flex items-end justify-between gap-2">
        <span className="font-mono text-3xl font-semibold tracking-tight text-foreground">
          {metric.value}
        </span>
        <div className="h-10 w-24">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 4, bottom: 0, left: 0, right: 0 }}>
              <defs>
                <linearGradient id={`spark-${metric.label}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.5} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="v"
                stroke={color}
                strokeWidth={1.75}
                fill={`url(#spark-${metric.label})`}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
