"use client"

import { Square, RotateCcw, Clock } from "lucide-react"
import {
  LineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  ReferenceLine,
} from "recharts"
import { Button } from "@/components/ui/button"

/* Deterministic convergence curve: chi2/ndf over 60 iterations */
const SPARKLINE = [
  3.84,3.52,3.21,2.96,2.74,2.57,2.43,2.31,2.21,2.13,
  2.07,2.01,1.96,1.91,1.88,1.84,1.81,1.78,1.76,1.74,
  1.72,1.70,1.68,1.67,1.65,1.64,1.63,1.61,1.60,1.59,
  1.58,1.57,1.56,1.55,1.55,1.54,1.53,1.52,1.52,1.51,
  1.50,1.50,1.49,1.49,1.48,1.48,1.47,1.47,1.46,1.46,
  1.45,1.45,1.45,1.44,1.44,1.44,1.44,1.43,1.43,1.43,
].map((v, i) => ({ iter: i + 1, chi2: v }))

const CURRENT_CHI2 = 1.43
const TOTAL_ITERS = 60
const CURRENT_ITER = 60

interface Param {
  name: string
  unit: string
  value: number
  unc: number
  delta: number
  deltaSign: "pos" | "neg" | "zero"
}

const PARAMS: Param[] = [
  { name: "m_\u03c1",       unit: "MeV/c\u00b2", value: 775.26, unc: 0.04,   delta: -0.02,    deltaSign: "neg"  },
  { name: "\u0393_\u03c1",  unit: "MeV",          value: 149.1,  unc: 0.8,    delta: +0.30,    deltaSign: "pos"  },
  { name: "A_bg",            unit: "\u2014",        value: 0.2341, unc: 0.0012, delta: +0.0003,  deltaSign: "pos"  },
  { name: "\u03b1_P(0)",     unit: "\u2014",        value: 1.0814, unc: 0.0081, delta: -0.0006,  deltaSign: "neg"  },
  { name: "\u03b2_qqg",      unit: "GeV\u207b\u00b2", value: 2.156, unc: 0.034, delta: +0.012,  deltaSign: "pos"  },
]

function DeltaBadge({ delta, sign }: { delta: number; sign: Param["deltaSign"] }) {
  const color =
    Math.abs(delta) < 0.0001
      ? "var(--muted-foreground)"
      : sign === "neg"
      ? "var(--status-supported)"
      : "var(--amber)"

  const label =
    delta === 0 ? "\u00b10" : `${delta >= 0 ? "+" : ""}${delta}`

  return (
    <span
      className="font-mono text-[11px] px-1.5 py-0.5 rounded"
      style={{
        color,
        background: "var(--muted)",
      }}
    >
      {label}
    </span>
  )
}

export function FittingPipeline() {
  return (
    <section className="px-10 py-8 space-y-8 max-w-[900px]">
      {/* Header */}
      <div className="flex items-baseline gap-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          Fitting Pipeline Monitor
        </h1>
        <span
          className="font-mono text-xs"
          style={{ color: "var(--muted-foreground)" }}
        >
          fitting_pipeline.py
        </span>
      </div>

      {/* Run summary card */}
      <div
        className="rounded border p-6 space-y-6"
        style={{ background: "var(--card)", borderColor: "var(--border)" }}
      >
        {/* Run meta */}
        <div className="flex items-start justify-between gap-6">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span
                className="w-2 h-2 rounded-full live-dot"
                style={{ background: "var(--status-supported)" }}
              />
              <span className="font-mono text-xs font-semibold" style={{ color: "var(--status-supported)" }}>
                RUNNING
              </span>
              <span className="font-mono text-xs text-muted-foreground">
                v2.3.1 · run-20240115-0803
              </span>
            </div>

            <div className="flex items-center gap-6">
              <div>
                <p className="text-[11px] font-mono text-muted-foreground mb-0.5">Iteration</p>
                <p className="font-mono text-lg font-semibold tabular-nums text-foreground">
                  {CURRENT_ITER}/{TOTAL_ITERS}
                </p>
              </div>
              <div>
                <p className="text-[11px] font-mono text-muted-foreground mb-0.5">
                  Current {"\u03c7\u00b2/ndf"}
                </p>
                <p
                  className="font-mono text-lg font-semibold tabular-nums"
                  style={{ color: "var(--amber)" }}
                >
                  {CURRENT_CHI2.toFixed(3)}
                </p>
              </div>
              <div>
                <p className="text-[11px] font-mono text-muted-foreground mb-0.5">Elapsed</p>
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-muted-foreground" />
                  <p className="font-mono text-lg font-semibold text-foreground">4h 32m</p>
                </div>
              </div>
              <div>
                <p className="text-[11px] font-mono text-muted-foreground mb-0.5">Dataset</p>
                <p className="font-mono text-sm font-medium text-foreground">ALICE 13 TeV pp</p>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-2 shrink-0">
            <Button
              size="sm"
              variant="outline"
              className="h-8 gap-1.5 font-mono text-xs"
              style={{ borderColor: "var(--border)", color: "var(--muted-foreground)" }}
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Restart
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="h-8 gap-1.5 font-mono text-xs"
              style={{
                borderColor: "var(--status-refuted-bg)",
                color: "var(--status-refuted)",
              }}
            >
              <Square className="w-3.5 h-3.5" />
              Stop run
            </Button>
          </div>
        </div>

        {/* Chi2/ndf sparkline */}
        <div>
          <div className="flex items-baseline justify-between mb-2">
            <p className="text-[11px] font-mono text-muted-foreground tracking-widest uppercase">
              {"\u03c7\u00b2/ndf"} convergence
            </p>
            <p className="text-[11px] font-mono text-muted-foreground">
              target \u2264 1.2
            </p>
          </div>
          <div
            className="rounded border"
            style={{ borderColor: "var(--border)", background: "var(--background)" }}
          >
            <ResponsiveContainer width="100%" height={80}>
              <LineChart
                data={SPARKLINE}
                margin={{ top: 10, right: 12, bottom: 6, left: 12 }}
              >
                <ReferenceLine
                  y={1.2}
                  stroke="var(--status-supported)"
                  strokeDasharray="3 3"
                  strokeWidth={1}
                  strokeOpacity={0.5}
                />
                <Line
                  type="monotone"
                  dataKey="chi2"
                  stroke="var(--amber)"
                  strokeWidth={1.5}
                  dot={false}
                  isAnimationActive={false}
                />
                <Tooltip
                  contentStyle={{
                    background: "var(--popover)",
                    border: "1px solid var(--border)",
                    borderRadius: "4px",
                    fontSize: "11px",
                    fontFamily: "var(--font-mono)",
                    color: "var(--foreground)",
                    padding: "4px 8px",
                  }}
                  formatter={(v: number) => [v.toFixed(3), "\u03c7\u00b2/ndf"]}
                  labelFormatter={(l: number) => `Iter ${l}`}
                  cursor={{ stroke: "var(--border)", strokeWidth: 1 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Parameter convergence */}
        <div>
          <p className="text-[11px] font-mono text-muted-foreground tracking-widest uppercase mb-3">
            Parameter convergence
          </p>
          <div className="space-y-1">
            <div
              className="grid font-mono text-[11px] text-muted-foreground pb-1 border-b"
              style={{
                borderColor: "var(--border)",
                gridTemplateColumns: "7rem 1fr 7rem 6rem",
              }}
            >
              <span>Parameter</span>
              <span>Value \u00b1 \u03c3</span>
              <span className="text-right">Unit</span>
              <span className="text-right">\u0394 last iter</span>
            </div>
            {PARAMS.map((p) => (
              <div
                key={p.name}
                className="grid items-center py-1.5 hover:bg-muted/20 rounded transition-colors"
                style={{
                  gridTemplateColumns: "7rem 1fr 7rem 6rem",
                }}
              >
                <span className="font-mono text-sm font-medium text-foreground">
                  {p.name}
                </span>
                <span className="font-mono text-xs text-foreground tabular-nums">
                  {p.value}&thinsp;\u00b1&thinsp;{p.unc}
                </span>
                <span className="font-mono text-xs text-right text-muted-foreground">
                  {p.unit}
                </span>
                <span className="text-right">
                  <DeltaBadge delta={p.delta} sign={p.deltaSign} />
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Log tail */}
      <div>
        <p className="text-[11px] font-mono text-muted-foreground tracking-widest uppercase mb-2">
          Stdout tail (last 5 lines)
        </p>
        <pre
          className="rounded border p-4 font-mono text-xs leading-relaxed overflow-x-auto"
          style={{
            background: "var(--background)",
            borderColor: "var(--border)",
            color: "var(--muted-foreground)",
          }}
        >
{`[14:31:52] iter=60  chi2/ndf=1.4302  dchi2=-0.0007
[14:31:51] iter=59  chi2/ndf=1.4309  dchi2=-0.0006
[14:31:50] iter=58  chi2/ndf=1.4315  dchi2=-0.0008
[14:31:48] iter=57  chi2/ndf=1.4323  dchi2=-0.0011
[14:31:46] iter=56  chi2/ndf=1.4334  dchi2=-0.0009`}
        </pre>
      </div>
    </section>
  )
}
