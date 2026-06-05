"use client"

import { useState } from "react"
import { CheckCircle2, XCircle, AlertCircle, RefreshCw, Cpu, ShieldAlert, Terminal, ChevronDown, ChevronUp } from "lucide-react"

/* ─── Mock data ─────────────────────────────────────────── */

type ServiceStatus = "healthy" | "degraded" | "down"

interface Service {
  id: string
  label: string
  version: string
  host: string
  uptime: string
  status: ServiceStatus
  lastCheck: string
  note: string | null
}

const SERVICES: Service[] = [
  {
    id: "onyx",
    label: "Onyx",
    version: "v0.4.12",
    host: "onyx.internal:8080",
    uptime: "14 d 3 h 22 m",
    status: "healthy",
    lastCheck: "14:32:01 UTC",
    note: null,
  },
  {
    id: "deerflow",
    label: "DeerFlow",
    version: "v1.2.1",
    host: "deerflow.internal:8765",
    uptime: "2 d 18 h 11 m",
    status: "degraded",
    lastCheck: "14:32:00 UTC",
    note: "High latency on /run_agent endpoint (P95 = 28.3 s). Embedding model swap pending.",
  },
  {
    id: "mcp_proxy",
    label: "MCP Proxy",
    version: "v0.2.4",
    host: "mcp.internal:3000",
    uptime: "30 d 0 h 51 m",
    status: "healthy",
    lastCheck: "14:31:59 UTC",
    note: null,
  },
]

interface DockerService {
  id: string
  name: string
  image: string
  replicas: string
  status: "running" | "stopped" | "restarting"
  cpu: string
  mem: string
}

const DOCKER_STACK: DockerService[] = [
  { id: "d1", name: "aisci_api",       image: "aisci/api:14.3",          replicas: "2/2", status: "running",    cpu: "12%", mem: "1.2 GB" },
  { id: "d2", name: "onyx_worker",     image: "onyx/worker:0.4.12",      replicas: "4/4", status: "running",    cpu: "34%", mem: "3.8 GB" },
  { id: "d3", name: "deerflow_agent",  image: "deerflow/agent:1.2.1",    replicas: "2/2", status: "restarting", cpu: "—",   mem: "—" },
  { id: "d4", name: "mcp_server",      image: "aisci/mcp-proxy:0.2.4",   replicas: "1/1", status: "running",    cpu: "2%",  mem: "0.3 GB" },
  { id: "d5", name: "postgres",        image: "postgres:16-alpine",       replicas: "1/1", status: "running",    cpu: "4%",  mem: "0.6 GB" },
  { id: "d6", name: "redis",           image: "redis:7-alpine",           replicas: "1/1", status: "running",    cpu: "1%",  mem: "0.1 GB" },
  { id: "d7", name: "gpu_inference",   image: "aisci/gpu-infer:cuda12.3", replicas: "0/1", status: "stopped",    cpu: "—",   mem: "—" },
  { id: "d8", name: "minio",           image: "minio/minio:latest",       replicas: "1/1", status: "running",    cpu: "3%",  mem: "0.4 GB" },
]

const GPU_ENABLED = false

type SecretStatus = "clean" | "warning" | "scanning"
const SECRET_STATUS: SecretStatus = "warning"
const SECRET_FINDINGS = [
  { file: "config/deerflow.yaml",      rule: "generic-api-key",    line: 14 },
  { file: ".env.local.example",        rule: "aws-secret-access-key", line: 3 },
]

const LOG_LINES = [
  { ts: "14:32:01.412", level: "INFO",  svc: "onyx",       msg: "Health check OK — 200 /healthz" },
  { ts: "14:32:00.889", level: "WARN",  svc: "deerflow",   msg: "P95 latency 28318 ms on /run_agent (threshold: 10000 ms)" },
  { ts: "14:31:59.990", level: "INFO",  svc: "mcp_proxy",  msg: "Tool call: search_hepdata — 241 ms" },
  { ts: "14:31:58.774", level: "ERROR", svc: "deerflow",   msg: "TimeoutError: tool call to 'read_file' exceeded 30 s" },
  { ts: "14:31:57.333", level: "INFO",  svc: "aisci_api",  msg: "POST /api/claims 201 Created — 34 ms" },
  { ts: "14:31:56.121", level: "WARN",  svc: "gpu_infer",  msg: "Container exited: OOMKilled (VRAM 24 GB exceeded)" },
  { ts: "14:31:54.901", level: "INFO",  svc: "onyx",       msg: "Embedding batch 128/512 complete" },
  { ts: "14:31:53.502", level: "ERROR", svc: "deerflow",   msg: "ValidationError: arxiv payload missing 'doi' — skipping" },
  { ts: "14:31:52.200", level: "INFO",  svc: "mcp_proxy",  msg: "Tool call: get_formula_list — 88 ms" },
  { ts: "14:31:51.019", level: "INFO",  svc: "aisci_api",  msg: "GET /api/evidence 200 OK — 12 ms" },
  { ts: "14:31:49.677", level: "WARN",  svc: "postgres",   msg: "Slow query: 1840 ms on SELECT * FROM runs WHERE status='running'" },
  { ts: "14:31:48.503", level: "INFO",  svc: "redis",      msg: "SETEX evidence:live:14 TTL=30s" },
]

/* ─── Helpers ───────────────────────────────────────────── */

const STATUS_ICON: Record<ServiceStatus, React.ReactNode> = {
  healthy:  <CheckCircle2 className="w-4 h-4 shrink-0" style={{ color: "var(--status-supported)" }} />,
  degraded: <AlertCircle  className="w-4 h-4 shrink-0" style={{ color: "var(--amber)" }} />,
  down:     <XCircle      className="w-4 h-4 shrink-0" style={{ color: "var(--status-refuted)" }} />,
}

const STATUS_TEXT: Record<ServiceStatus, string> = {
  healthy:  "var(--status-supported)",
  degraded: "var(--amber)",
  down:     "var(--status-refuted)",
}

const STATUS_BG: Record<ServiceStatus, string> = {
  healthy:  "var(--status-supported-bg)",
  degraded: "var(--amber-bg)",
  down:     "var(--status-refuted-bg)",
}

const DOCKER_STATUS_COLOR: Record<DockerService["status"], string> = {
  running:    "var(--status-supported)",
  stopped:    "var(--status-refuted)",
  restarting: "var(--amber)",
}

const LOG_LEVEL_COLOR: Record<string, string> = {
  INFO:  "var(--muted-foreground)",
  WARN:  "var(--amber)",
  ERROR: "var(--status-refuted)",
  DEBUG: "var(--muted-foreground)",
}

function ServiceCard({ svc }: { svc: Service }) {
  return (
    <div
      className="rounded border p-5 space-y-3"
      style={{ background: "var(--card)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          {STATUS_ICON[svc.status]}
          <span className="text-sm font-medium text-foreground">{svc.label}</span>
          <span
            className="font-mono text-[10px] px-1.5 py-0.5 rounded"
            style={{ background: "var(--muted)", color: "var(--muted-foreground)" }}
          >
            {svc.version}
          </span>
        </div>
        <span
          className="font-mono text-[11px] px-2 py-0.5 rounded capitalize"
          style={{ color: STATUS_TEXT[svc.status], background: STATUS_BG[svc.status] }}
        >
          {svc.status}
        </span>
      </div>

      <div className="space-y-1 font-mono text-xs text-muted-foreground">
        <div className="flex items-center justify-between">
          <span>{svc.host}</span>
          <span>up {svc.uptime}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>last check</span>
          <span>{svc.lastCheck}</span>
        </div>
      </div>

      {svc.note && (
        <p
          className="font-mono text-[11px] leading-relaxed rounded px-2.5 py-2 border"
          style={{
            color: "var(--amber)",
            background: "var(--amber-bg)",
            borderColor: "var(--amber)",
          }}
        >
          {svc.note}
        </p>
      )}
    </div>
  )
}

/* ─── Component ─────────────────────────────────────────── */

export function OpsSurface() {
  const [logExpanded, setLogExpanded] = useState(false)
  const logLines = logExpanded ? LOG_LINES : LOG_LINES.slice(0, 6)

  return (
    <section className="px-10 py-8 space-y-8 max-w-[960px]">
      {/* Header */}
      <div className="flex items-baseline gap-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          Infrastructure
        </h1>
        <span className="font-mono text-xs text-muted-foreground">
          DevOps surface · 2024-01-15 14:32 UTC
        </span>
        <button className="ml-auto flex items-center gap-1.5 font-mono text-xs text-muted-foreground hover:text-foreground transition-colors">
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* Deployment status cards */}
      <div>
        <p className="text-[11px] font-mono font-semibold tracking-widest uppercase text-muted-foreground mb-3">
          Deployment Status
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {SERVICES.map((svc) => (
            <ServiceCard key={svc.id} svc={svc} />
          ))}
        </div>
      </div>

      {/* Docker stack health + GPU strip */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <p className="text-[11px] font-mono font-semibold tracking-widest uppercase text-muted-foreground">
            Docker Stack
          </p>
          {/* GPU pill */}
          <div
            className="flex items-center gap-1.5 font-mono text-[11px] px-2.5 py-1 rounded border"
            style={{
              background: GPU_ENABLED ? "var(--status-supported-bg)" : "var(--status-refuted-bg)",
              borderColor: GPU_ENABLED ? "var(--status-supported)" : "var(--status-refuted)",
              color: GPU_ENABLED ? "var(--status-supported)" : "var(--status-refuted)",
            }}
          >
            <Cpu className="w-3 h-3" />
            GPU accel — {GPU_ENABLED ? "on" : "off"}
          </div>
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
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground">
                  Service
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground hidden md:table-cell">
                  Image
                </th>
                <th className="text-center px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-24">
                  Replicas
                </th>
                <th className="text-center px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-28">
                  Status
                </th>
                <th className="text-right px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-16 hidden sm:table-cell">
                  CPU
                </th>
                <th className="text-right px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-20 hidden sm:table-cell">
                  Mem
                </th>
              </tr>
            </thead>
            <tbody>
              {DOCKER_STACK.map((row, i) => (
                <tr
                  key={row.id}
                  className="border-b transition-colors hover:bg-muted/20"
                  style={{
                    borderColor: "var(--border)",
                    background: i % 2 === 0 ? "transparent" : "var(--card)",
                  }}
                >
                  <td className="px-4 py-2.5 font-mono text-xs text-foreground">
                    {row.name}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-xs text-muted-foreground hidden md:table-cell">
                    {row.image}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-xs text-center">
                    <span
                      style={{
                        color: row.replicas.startsWith("0")
                          ? "var(--status-refuted)"
                          : row.replicas.split("/")[0] !== row.replicas.split("/")[1]
                          ? "var(--amber)"
                          : "var(--status-supported)",
                      }}
                    >
                      {row.replicas}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    <span
                      className="inline-block font-mono text-[11px] px-2 py-0.5 rounded capitalize"
                      style={{
                        color: DOCKER_STATUS_COLOR[row.status],
                        background:
                          row.status === "running"
                            ? "var(--status-supported-bg)"
                            : row.status === "restarting"
                            ? "var(--amber-bg)"
                            : "var(--status-refuted-bg)",
                      }}
                    >
                      {row.status}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 font-mono text-xs text-muted-foreground text-right hidden sm:table-cell">
                    {row.cpu}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-xs text-muted-foreground text-right hidden sm:table-cell">
                    {row.mem}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Secret leak scanner */}
      <div>
        <p className="text-[11px] font-mono font-semibold tracking-widest uppercase text-muted-foreground mb-3">
          Secret-Leak Scanner
        </p>
        <div
          className="rounded border p-5 space-y-4"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <ShieldAlert
                className="w-4 h-4 shrink-0"
                style={{
                  color:
                    SECRET_STATUS === "clean"
                      ? "var(--status-supported)"
                      : SECRET_STATUS === "warning"
                      ? "var(--amber)"
                      : "var(--muted-foreground)",
                }}
              />
              <span className="text-sm font-medium text-foreground">
                gitleaks · trivy secret scan
              </span>
            </div>
            <span
              className="font-mono text-[11px] px-2.5 py-0.5 rounded capitalize"
              style={{
                color:
                  SECRET_STATUS === "clean"
                    ? "var(--status-supported)"
                    : SECRET_STATUS === "warning"
                    ? "var(--amber)"
                    : "var(--muted-foreground)",
                background:
                  SECRET_STATUS === "clean"
                    ? "var(--status-supported-bg)"
                    : SECRET_STATUS === "warning"
                    ? "var(--amber-bg)"
                    : "var(--muted)",
              }}
            >
              {SECRET_STATUS === "warning"
                ? `${SECRET_FINDINGS.length} findings`
                : SECRET_STATUS}
            </span>
          </div>

          {SECRET_STATUS === "warning" && (
            <div
              className="rounded border overflow-hidden"
              style={{ borderColor: "var(--border)" }}
            >
              <table className="w-full">
                <thead>
                  <tr
                    className="border-b"
                    style={{ background: "var(--muted)", borderColor: "var(--border)" }}
                  >
                    <th className="text-left px-3 py-2 font-mono text-[10px] font-semibold tracking-widest uppercase text-muted-foreground">
                      File
                    </th>
                    <th className="text-left px-3 py-2 font-mono text-[10px] font-semibold tracking-widest uppercase text-muted-foreground">
                      Rule
                    </th>
                    <th className="text-right px-3 py-2 font-mono text-[10px] font-semibold tracking-widest uppercase text-muted-foreground w-16">
                      Line
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {SECRET_FINDINGS.map((f, i) => (
                    <tr
                      key={i}
                      className="border-b last:border-0"
                      style={{ borderColor: "var(--border)" }}
                    >
                      <td className="px-3 py-2.5 font-mono text-xs text-foreground">
                        {f.file}
                      </td>
                      <td className="px-3 py-2.5">
                        <span
                          className="font-mono text-[11px] px-1.5 py-0.5 rounded"
                          style={{ background: "var(--amber-bg)", color: "var(--amber)" }}
                        >
                          {f.rule}
                        </span>
                      </td>
                      <td className="px-3 py-2.5 font-mono text-xs text-muted-foreground text-right">
                        {f.line}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <p className="font-mono text-[11px] text-muted-foreground">
            Last scan: 2024-01-15 14:15 UTC · 2 findings require remediation before merge.
          </p>
        </div>
      </div>

      {/* Log tail */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <p className="text-[11px] font-mono font-semibold tracking-widest uppercase text-muted-foreground">
            Log Tail
          </p>
          <div className="flex items-center gap-2">
            <span
              className="w-1.5 h-1.5 rounded-full live-dot"
              style={{ background: "var(--status-supported)" }}
            />
            <span className="font-mono text-[10px] tracking-widest uppercase text-muted-foreground">
              live
            </span>
          </div>
        </div>

        <div
          className="rounded border overflow-hidden"
          style={{ background: "var(--background)", borderColor: "var(--border)" }}
        >
          <div className="flex items-center gap-2 px-4 py-2 border-b"
            style={{ background: "var(--muted)", borderColor: "var(--border)" }}
          >
            <Terminal className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="font-mono text-[11px] text-muted-foreground">
              docker compose logs --follow --tail 50
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <tbody>
                {logLines.map((l, i) => (
                  <tr
                    key={i}
                    className="border-b last:border-0 hover:bg-muted/10 transition-colors"
                    style={{ borderColor: "var(--border)" }}
                  >
                    <td className="pl-4 pr-3 py-1.5 font-mono text-[11px] text-muted-foreground whitespace-nowrap align-top w-28">
                      {l.ts}
                    </td>
                    <td className="px-3 py-1.5 align-top w-16">
                      <span
                        className="font-mono text-[10px] font-semibold tracking-widest"
                        style={{ color: LOG_LEVEL_COLOR[l.level] ?? "var(--muted-foreground)" }}
                      >
                        {l.level}
                      </span>
                    </td>
                    <td className="px-3 py-1.5 align-top w-24">
                      <span
                        className="font-mono text-[11px] px-1.5 py-0.5 rounded"
                        style={{ background: "var(--muted)", color: "var(--muted-foreground)" }}
                      >
                        {l.svc}
                      </span>
                    </td>
                    <td className="px-3 pr-4 py-1.5 font-mono text-[11px] text-foreground leading-relaxed">
                      {l.msg}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button
            onClick={() => setLogExpanded((v) => !v)}
            className="w-full flex items-center justify-center gap-1.5 py-2 border-t font-mono text-[11px] text-muted-foreground hover:text-foreground hover:bg-muted/20 transition-colors"
            style={{ borderColor: "var(--border)" }}
          >
            {logExpanded ? (
              <>
                <ChevronUp className="w-3.5 h-3.5" />
                Collapse
              </>
            ) : (
              <>
                <ChevronDown className="w-3.5 h-3.5" />
                Show all {LOG_LINES.length} lines
              </>
            )}
          </button>
        </div>
      </div>
    </section>
  )
}
