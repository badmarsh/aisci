"use client"

import { useState } from "react"
import { CheckCircle2, XCircle, AlertCircle, Clock, ChevronRight, RefreshCw } from "lucide-react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts"

/* ─── Mock data ─────────────────────────────────────────── */

interface SubsystemResult {
  id: string
  label: string
  passed: number
  failed: number
  skipped: number
  coverage: number
  duration: string
  lastRun: string
}

const SUBSYSTEMS: SubsystemResult[] = [
  {
    id: "physics",
    label: "Physics",
    passed: 142,
    failed: 3,
    skipped: 4,
    coverage: 87,
    duration: "12.4 s",
    lastRun: "2024-01-15 14:31 UTC",
  },
  {
    id: "onyx",
    label: "Onyx",
    passed: 88,
    failed: 0,
    skipped: 1,
    coverage: 94,
    duration: "6.7 s",
    lastRun: "2024-01-15 14:30 UTC",
  },
  {
    id: "deerflow",
    label: "DeerFlow",
    passed: 61,
    failed: 7,
    skipped: 2,
    coverage: 71,
    duration: "9.2 s",
    lastRun: "2024-01-15 14:29 UTC",
  },
  {
    id: "mcp_proxy",
    label: "MCP Proxy",
    passed: 35,
    failed: 0,
    skipped: 0,
    coverage: 96,
    duration: "2.1 s",
    lastRun: "2024-01-15 14:28 UTC",
  },
  {
    id: "pipeline",
    label: "Fit Pipeline",
    passed: 52,
    failed: 1,
    skipped: 3,
    coverage: 78,
    duration: "18.6 s",
    lastRun: "2024-01-15 14:25 UTC",
  },
]

interface Failure {
  id: string
  subsystem: string
  test: string
  message: string
  duration: string
  time: string
}

const RECENT_FAILURES: Failure[] = [
  {
    id: "F-001",
    subsystem: "Physics",
    test: "test_chi2_convergence_rho770",
    message: "AssertionError: χ²/ndf = 3.21 > threshold 2.50",
    duration: "0.83 s",
    time: "14:31:08",
  },
  {
    id: "F-002",
    subsystem: "Physics",
    test: "test_pomeron_intercept_bound",
    message: "ValueError: intercept 1.095 outside allowed range [1.065, 1.090]",
    duration: "0.11 s",
    time: "14:31:07",
  },
  {
    id: "F-003",
    subsystem: "DeerFlow",
    test: "test_agent_tool_retry_limit",
    message: "TimeoutError: tool call exceeded 30.0 s limit (actual: 31.4 s)",
    duration: "31.4 s",
    time: "14:29:44",
  },
  {
    id: "F-004",
    subsystem: "DeerFlow",
    test: "test_schema_validation_arxiv_payload",
    message: "ValidationError: 'doi' field missing in response fixture v3",
    duration: "0.04 s",
    time: "14:29:41",
  },
  {
    id: "F-005",
    subsystem: "Physics",
    test: "test_froissart_bound_consistency",
    message: "AssertionError: s₀ definition mismatch vs §2.1 (see F.10 symbolic)",
    duration: "0.22 s",
    time: "14:29:39",
  },
  {
    id: "F-006",
    subsystem: "DeerFlow",
    test: "test_rag_chunk_overlap_boundary",
    message: "IndexError: chunk boundary -1 out of range for document with 0 pages",
    duration: "0.07 s",
    time: "14:29:37",
  },
  {
    id: "F-007",
    subsystem: "DeerFlow",
    test: "test_embedding_vector_dimension",
    message: "AssertionError: expected dim=1536, got dim=3072 (model changed)",
    duration: "0.16 s",
    time: "14:29:35",
  },
  {
    id: "F-008",
    subsystem: "Fit Pipeline",
    test: "test_minuit_gradient_tolerance",
    message: "ConvergenceWarning: MIGRAD did not converge after 500 iterations",
    duration: "4.80 s",
    time: "14:25:12",
  },
]

/* ─── Bar chart data ────────────────────────────────────── */

const CHART_DATA = SUBSYSTEMS.map((s) => ({
  name: s.label,
  passed: s.passed,
  failed: s.failed,
  skipped: s.skipped,
}))

/* ─── Helpers ───────────────────────────────────────────── */

function totalPassed() { return SUBSYSTEMS.reduce((a, s) => a + s.passed, 0) }
function totalFailed() { return SUBSYSTEMS.reduce((a, s) => a + s.failed, 0) }
function totalSkipped() { return SUBSYSTEMS.reduce((a, s) => a + s.skipped, 0) }

function CoverageBar({ pct }: { pct: number }) {
  const color =
    pct >= 90 ? "var(--status-supported)" :
    pct >= 75 ? "var(--amber)" :
    "var(--status-refuted)"

  return (
    <div className="flex items-center gap-2.5">
      <div
        className="relative h-1.5 flex-1 rounded-full overflow-hidden"
        style={{ background: "var(--muted)" }}
      >
        <div
          className="absolute left-0 top-0 h-full rounded-full transition-all"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span
        className="font-mono text-xs tabular-nums w-8 text-right"
        style={{ color }}
      >
        {pct}%
      </span>
    </div>
  )
}

function SubsystemBadge({ result }: { result: SubsystemResult }) {
  const hasFailed = result.failed > 0
  const icon = hasFailed
    ? <XCircle className="w-3.5 h-3.5 shrink-0" style={{ color: "var(--status-refuted)" }} />
    : <CheckCircle2 className="w-3.5 h-3.5 shrink-0" style={{ color: "var(--status-supported)" }} />

  return (
    <div
      className="rounded border p-4 space-y-3"
      style={{ background: "var(--card)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium text-foreground">{result.label}</span>
        </div>
        <span className="font-mono text-[10px] text-muted-foreground">{result.lastRun}</span>
      </div>

      <div className="flex items-center gap-4 font-mono text-xs">
        <span style={{ color: "var(--status-supported)" }}>
          {result.passed} passed
        </span>
        {result.failed > 0 && (
          <span style={{ color: "var(--status-refuted)" }}>
            {result.failed} failed
          </span>
        )}
        {result.skipped > 0 && (
          <span style={{ color: "var(--muted-foreground)" }}>
            {result.skipped} skipped
          </span>
        )}
        <span className="ml-auto flex items-center gap-1 text-muted-foreground">
          <Clock className="w-3 h-3" />
          {result.duration}
        </span>
      </div>

      <div className="space-y-1">
        <p className="text-[10px] font-mono tracking-widest uppercase text-muted-foreground">
          Coverage
        </p>
        <CoverageBar pct={result.coverage} />
      </div>
    </div>
  )
}

/* ─── Component ─────────────────────────────────────────── */

export function TestsDashboard() {
  const [showAll, setShowAll] = useState(false)
  const displayed = showAll ? RECENT_FAILURES : RECENT_FAILURES.slice(0, 5)
  const totalTests = totalPassed() + totalFailed() + totalSkipped()
  const passRate = ((totalPassed() / totalTests) * 100).toFixed(1)

  return (
    <section className="px-10 py-8 space-y-8 max-w-[960px]">
      {/* Header */}
      <div className="flex items-baseline gap-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          Test Results
        </h1>
        <span className="font-mono text-xs text-muted-foreground">
          pytest · CI run 2024-01-15 14:31 UTC
        </span>
        <button
          className="ml-auto flex items-center gap-1.5 font-mono text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Re-run all
        </button>
      </div>

      {/* Global summary strip */}
      <div
        className="flex items-center gap-6 rounded border px-5 py-3.5"
        style={{ background: "var(--card)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" style={{ color: "var(--status-supported)" }} />
          <span className="font-mono text-sm" style={{ color: "var(--status-supported)" }}>
            {totalPassed()} passed
          </span>
        </div>
        <div className="flex items-center gap-2">
          <XCircle className="w-4 h-4" style={{ color: "var(--status-refuted)" }} />
          <span className="font-mono text-sm" style={{ color: "var(--status-refuted)" }}>
            {totalFailed()} failed
          </span>
        </div>
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-muted-foreground" />
          <span className="font-mono text-sm text-muted-foreground">
            {totalSkipped()} skipped
          </span>
        </div>

        <div
          className="h-5 w-px mx-2"
          style={{ background: "var(--border)" }}
        />

        <span className="font-mono text-sm text-foreground">
          {totalTests} total
        </span>

        <div
          className="h-5 w-px mx-2"
          style={{ background: "var(--border)" }}
        />

        <span
          className="font-mono text-sm"
          style={{
            color: parseFloat(passRate) >= 97
              ? "var(--status-supported)"
              : parseFloat(passRate) >= 90
              ? "var(--amber)"
              : "var(--status-refuted)",
          }}
        >
          {passRate}% pass rate
        </span>

        <div className="ml-auto flex items-center gap-1.5 text-muted-foreground font-mono text-xs">
          <Clock className="w-3.5 h-3.5" />
          49.0 s total
        </div>
      </div>

      {/* Per-subsystem cards */}
      <div>
        <p className="text-[11px] font-mono font-semibold tracking-widest uppercase text-muted-foreground mb-3">
          Subsystems
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {SUBSYSTEMS.map((s) => (
            <SubsystemBadge key={s.id} result={s} />
          ))}
        </div>
      </div>

      {/* Pass/fail chart */}
      <div
        className="rounded border p-5 space-y-3"
        style={{ background: "var(--card)", borderColor: "var(--border)" }}
      >
        <p className="text-[11px] font-mono font-semibold tracking-widest uppercase text-muted-foreground">
          Pass / Fail Distribution
        </p>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart
            data={CHART_DATA}
            margin={{ top: 4, right: 8, left: -20, bottom: 4 }}
            barSize={18}
          >
            <CartesianGrid
              strokeDasharray="2 4"
              stroke="var(--border)"
              strokeOpacity={0.6}
              vertical={false}
            />
            <XAxis
              dataKey="name"
              stroke="var(--border)"
              tick={{
                fontSize: 11,
                fontFamily: "var(--font-mono)",
                fill: "var(--muted-foreground)",
              }}
            />
            <YAxis
              stroke="var(--border)"
              tick={{
                fontSize: 10,
                fontFamily: "var(--font-mono)",
                fill: "var(--muted-foreground)",
              }}
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
              cursor={{ fill: "var(--muted)", fillOpacity: 0.4 }}
            />
            <Bar dataKey="passed" name="Passed" radius={[2, 2, 0, 0]}>
              {CHART_DATA.map((_, i) => (
                <Cell key={i} fill="var(--status-supported)" fillOpacity={0.7} />
              ))}
            </Bar>
            <Bar dataKey="failed" name="Failed" radius={[2, 2, 0, 0]}>
              {CHART_DATA.map((entry, i) => (
                <Cell
                  key={i}
                  fill="var(--status-refuted)"
                  fillOpacity={entry.failed > 0 ? 0.85 : 0.2}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        {/* Chart legend */}
        <div className="flex items-center gap-4 pt-1">
          <div className="flex items-center gap-1.5">
            <span
              className="w-2.5 h-2.5 rounded-sm"
              style={{ background: "var(--status-supported)", opacity: 0.7 }}
            />
            <span className="font-mono text-[11px] text-muted-foreground">Passed</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className="w-2.5 h-2.5 rounded-sm"
              style={{ background: "var(--status-refuted)", opacity: 0.85 }}
            />
            <span className="font-mono text-[11px] text-muted-foreground">Failed</span>
          </div>
        </div>
      </div>

      {/* Recent failures */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <p className="text-[11px] font-mono font-semibold tracking-widest uppercase text-muted-foreground">
            Recent Failures
          </p>
          <span className="font-mono text-xs text-muted-foreground">
            {RECENT_FAILURES.length} total
          </span>
        </div>

        <div
          className="rounded border overflow-hidden"
          style={{ borderColor: "var(--border)" }}
        >
          <table className="w-full text-sm">
            <thead>
              <tr
                className="border-b"
                style={{ background: "var(--muted)", borderColor: "var(--border)" }}
              >
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-24">
                  Subsystem
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground">
                  Test
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground">
                  Message
                </th>
                <th className="text-right px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-16">
                  dur.
                </th>
                <th className="text-right px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-20">
                  Time
                </th>
              </tr>
            </thead>
            <tbody>
              {displayed.map((f, i) => (
                <tr
                  key={f.id}
                  className="border-b transition-colors hover:bg-muted/20"
                  style={{
                    borderColor: "var(--border)",
                    background: i % 2 === 0 ? "transparent" : "var(--card)",
                  }}
                >
                  <td className="px-4 py-3 align-top">
                    <span
                      className="inline-block font-mono text-[11px] px-2 py-0.5 rounded"
                      style={{
                        background: "var(--muted)",
                        color: "var(--muted-foreground)",
                      }}
                    >
                      {f.subsystem}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-foreground align-top whitespace-nowrap">
                    {f.test}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs align-top leading-relaxed"
                    style={{ color: "var(--status-refuted)" }}
                  >
                    {f.message}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground text-right align-top whitespace-nowrap">
                    {f.duration}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground text-right align-top whitespace-nowrap">
                    {f.time}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {RECENT_FAILURES.length > 5 && (
          <button
            onClick={() => setShowAll((v) => !v)}
            className="mt-3 flex items-center gap-1 font-mono text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            <ChevronRight
              className="w-3.5 h-3.5 transition-transform"
              style={{ transform: showAll ? "rotate(90deg)" : "rotate(0deg)" }}
            />
            {showAll
              ? "Show fewer"
              : `Show ${RECENT_FAILURES.length - 5} more failures`}
          </button>
        )}
      </div>
    </section>
  )
}
