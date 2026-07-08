"use client"

import { useState } from "react"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"
import { ChevronDown } from "lucide-react"

/* Mock pT spectra datasets */
const DATASETS = {
  alice_13: {
    label: "ALICE 13 TeV pp — charged hadrons",
    ref: "arXiv:2204.10210",
    color: "var(--chart-1)",
    data: [
      { pt: "0.15", dN: 22.4 }, { pt: "0.50", dN: 15.1 }, { pt: "1.00", dN: 8.73 },
      { pt: "1.50", dN: 4.91 }, { pt: "2.00", dN: 2.64 }, { pt: "2.50", dN: 1.38 },
      { pt: "3.00", dN: 0.712 }, { pt: "3.50", dN: 0.362 }, { pt: "4.00", dN: 0.183 },
      { pt: "4.50", dN: 0.0921 }, { pt: "5.00", dN: 0.0461 }, { pt: "6.00", dN: 0.0115 },
      { pt: "7.00", dN: 0.00283 }, { pt: "8.00", dN: 0.000693 }, { pt: "10.0", dN: 0.0000413 },
    ],
  },
  cms_7: {
    label: "CMS 7 TeV pp — charged tracks",
    ref: "arXiv:1005.3299",
    color: "var(--amber)",
    data: [
      { pt: "0.15", dN: 18.2 }, { pt: "0.50", dN: 12.4 }, { pt: "1.00", dN: 7.11 },
      { pt: "1.50", dN: 3.98 }, { pt: "2.00", dN: 2.12 }, { pt: "2.50", dN: 1.10 },
      { pt: "3.00", dN: 0.564 }, { pt: "3.50", dN: 0.285 }, { pt: "4.00", dN: 0.143 },
      { pt: "4.50", dN: 0.0714 }, { pt: "5.00", dN: 0.0355 }, { pt: "6.00", dN: 0.00873 },
      { pt: "7.00", dN: 0.00212 }, { pt: "8.00", dN: 0.000514 }, { pt: "10.0", dN: 0.0000301 },
    ],
  },
  atlas_5: {
    label: "ATLAS 5.02 TeV pp — inclusive charged",
    ref: "arXiv:1603.01500",
    color: "var(--chart-2)",
    data: [
      { pt: "0.15", dN: 14.3 }, { pt: "0.50", dN: 9.72 }, { pt: "1.00", dN: 5.59 },
      { pt: "1.50", dN: 3.14 }, { pt: "2.00", dN: 1.68 }, { pt: "2.50", dN: 0.873 },
      { pt: "3.00", dN: 0.449 }, { pt: "3.50", dN: 0.228 }, { pt: "4.00", dN: 0.114 },
      { pt: "4.50", dN: 0.0572 }, { pt: "5.00", dN: 0.0284 }, { pt: "6.00", dN: 0.00697 },
      { pt: "7.00", dN: 0.00170 }, { pt: "8.00", dN: 0.000410 }, { pt: "10.0", dN: 0.0000241 },
    ],
  },
} as const

type DatasetKey = keyof typeof DATASETS

export function SpectraPlotter() {
  const [selected, setSelected] = useState<DatasetKey>("alice_13")
  const ds = DATASETS[selected]

  return (
    <section className="px-10 py-8 space-y-8 max-w-[900px]">
      {/* Header */}
      <div className="flex items-baseline gap-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          Interactive Spectra Plotter
        </h1>
        <span className="font-mono text-xs text-muted-foreground">HEPData pT spectra</span>
      </div>

      {/* Dataset picker */}
      <div
        className="rounded border p-5 space-y-4"
        style={{ background: "var(--card)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="space-y-0.5">
            <p className="text-[11px] font-mono text-muted-foreground tracking-widest uppercase">
              Dataset
            </p>
            <p className="text-sm font-medium text-foreground">{ds.label}</p>
            <p className="font-mono text-xs text-muted-foreground">{ds.ref}</p>
          </div>

          {/* Custom select */}
          <div className="relative">
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value as DatasetKey)}
              className="appearance-none font-mono text-xs h-8 pl-3 pr-8 rounded border outline-none cursor-pointer transition-colors hover:border-foreground/30 focus:ring-1 ring-ring"
              style={{
                background: "var(--secondary)",
                borderColor: "var(--border)",
                color: "var(--foreground)",
              }}
            >
              {(Object.entries(DATASETS) as [DatasetKey, (typeof DATASETS)[DatasetKey]][]).map(
                ([k, v]) => (
                  <option key={k} value={k}>
                    {v.label}
                  </option>
                )
              )}
            </select>
            <ChevronDown
              className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 pointer-events-none"
              style={{ color: "var(--muted-foreground)" }}
            />
          </div>
        </div>

        {/* Axis labels */}
        <div className="flex items-center justify-between text-[11px] font-mono text-muted-foreground">
          <span>d²N / (dp_T dy) [GeV/c]\u207b\u00b9</span>
          <span>p_T [GeV/c]</span>
        </div>

        {/* Chart */}
        <div
          className="rounded border"
          style={{ borderColor: "var(--border)", background: "var(--background)" }}
        >
          <ResponsiveContainer width="100%" height={340}>
            <AreaChart
              data={[...ds.data]}
              margin={{ top: 16, right: 20, bottom: 10, left: 16 }}
            >
              <CartesianGrid
                strokeDasharray="2 4"
                stroke="var(--border)"
                strokeOpacity={0.6}
              />
              <XAxis
                dataKey="pt"
                stroke="var(--border)"
                tick={{ fontSize: 11, fontFamily: "var(--font-mono)", fill: "var(--muted-foreground)" }}
                label={{
                  value: "p_T [GeV/c]",
                  position: "insideBottom",
                  offset: -4,
                  fontSize: 11,
                  fontFamily: "var(--font-mono)",
                  fill: "var(--muted-foreground)",
                }}
              />
              <YAxis
                stroke="var(--border)"
                tick={{ fontSize: 10, fontFamily: "var(--font-mono)", fill: "var(--muted-foreground)" }}
                tickFormatter={(v: number) =>
                  v >= 1 ? v.toFixed(0) : v >= 0.01 ? v.toFixed(3) : v.toExponential(1)
                }
                width={62}
              />
              <Tooltip
                contentStyle={{
                  background: "var(--popover)",
                  border: "1px solid var(--border)",
                  borderRadius: "4px",
                  fontSize: "11px",
                  fontFamily: "var(--font-mono)",
                  color: "var(--foreground)",
                  padding: "6px 10px",
                }}
                formatter={(v: number) => [v.toPrecision(4), "d\u00b2N/dp_T dy"]}
                labelFormatter={(l: string) => `p_T = ${l} GeV/c`}
                cursor={{ stroke: "var(--border)", strokeWidth: 1 }}
              />
              <Area
                type="monotone"
                dataKey="dN"
                stroke={ds.color}
                fill={ds.color}
                fillOpacity={0.08}
                strokeWidth={1.5}
                dot={{ r: 3, fill: ds.color, strokeWidth: 0 }}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Footer note */}
        <p className="text-[11px] font-mono text-muted-foreground">
          Placeholder — connect HEPData API to load live spectra tables.
          Y-axis linear; log scale available on request.
        </p>
      </div>

      {/* Dataset switcher pills */}
      <div className="flex gap-2 flex-wrap">
        {(Object.entries(DATASETS) as [DatasetKey, (typeof DATASETS)[DatasetKey]][]).map(
          ([k, v]) => (
            <button
              key={k}
              onClick={() => setSelected(k)}
              className="font-mono text-xs px-3 py-1.5 rounded border transition-colors"
              style={{
                borderColor: selected === k ? v.color : "var(--border)",
                color: selected === k ? v.color : "var(--muted-foreground)",
                background: selected === k ? "var(--muted)" : "transparent",
              }}
            >
              {k === "alice_13" ? "ALICE 13 TeV" : k === "cms_7" ? "CMS 7 TeV" : "ATLAS 5 TeV"}
            </button>
          )
        )}
      </div>
    </section>
  )
}
