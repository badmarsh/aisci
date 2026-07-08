import { ExternalLink } from "lucide-react"

type ClaimStatus = "open" | "sanity" | "supported" | "refuted"

interface Claim {
  id: string
  claim: string
  status: ClaimStatus
  updated: string
  source: string
  chi2ndf: number | null
}

const STATUS_CFG: Record<
  ClaimStatus,
  { label: string; text: string; bg: string }
> = {
  open:      { label: "Open",          text: "var(--status-open)",      bg: "var(--status-open-bg)" },
  sanity:    { label: "Sanity checked",text: "var(--status-sanity)",    bg: "var(--status-sanity-bg)" },
  supported: { label: "Supported",     text: "var(--status-supported)", bg: "var(--status-supported-bg)" },
  refuted:   { label: "Refuted",       text: "var(--status-refuted)",   bg: "var(--status-refuted-bg)" },
}

const CLAIMS: Claim[] = [
  {
    id: "CLM-001",
    claim: "\u03c1(770)\u2070 mass m\u209a = 775.11 \u00b1 0.34 MeV/c\u00b2 consistent with PDG 2022",
    status: "supported",
    updated: "2024-01-15 14:32 UTC",
    source: "arXiv:2401.09876",
    chi2ndf: 1.12,
  },
  {
    id: "CLM-002",
    claim: "Charged kaon pT slope \u03ba = 0.312 \u00b1 0.021 GeV\u207b\u00b9 at \u221as = 13 TeV",
    status: "sanity",
    updated: "2024-01-15 11:20 UTC",
    source: "HEPData:ins2345678",
    chi2ndf: 1.41,
  },
  {
    id: "CLM-003",
    claim: "Bjorken sum rule saturates at Q\u00b2 = 5.0 GeV\u00b2 within systematic uncertainties",
    status: "open",
    updated: "2024-01-14 09:15 UTC",
    source: "Manuscript \u00a73.2",
    chi2ndf: null,
  },
  {
    id: "CLM-004",
    claim: "Pomeron intercept \u03b1_P(0) = 1.081 \u00b1 0.008 at \u221as = 13 TeV",
    status: "refuted",
    updated: "2024-01-13 16:45 UTC",
    source: "arXiv:2312.11111",
    chi2ndf: 3.87,
  },
  {
    id: "CLM-005",
    claim: "\u03c3_tot(pp) energy dependence follows s^0.0808 power law above ISR energies",
    status: "supported",
    updated: "2024-01-12 08:00 UTC",
    source: "PDG 2023 \u00a751",
    chi2ndf: 0.98,
  },
  {
    id: "CLM-006",
    claim: "\u03c9(782)\u2013\u03c1(770) mixing angle \u03b8_\u03c9\u03c1 = 3.4 \u00b1 0.6 mrad",
    status: "sanity",
    updated: "2024-01-11 17:30 UTC",
    source: "Manuscript \u00a74.1",
    chi2ndf: 1.55,
  },
  {
    id: "CLM-007",
    claim: "R(Q) = \u03c3(e\u207ae\u207b\u2192hadrons)/\u03c3(e\u207ae\u207b\u2192\u03bc\u207a\u03bc\u207b) > 3.8 above charm threshold",
    status: "supported",
    updated: "2024-01-10 12:45 UTC",
    source: "PDG 2023 \u00a79",
    chi2ndf: 1.03,
  },
  {
    id: "CLM-008",
    claim: "Regge slope \u03b1' = 0.887 \u00b1 0.025 GeV\u207b\u00b2 from \u03c0\u207ap elastic data",
    status: "open",
    updated: "2024-01-09 10:15 UTC",
    source: "HEPData:ins1234567",
    chi2ndf: null,
  },
  {
    id: "CLM-009",
    claim: "Quark counting rules hold for large-angle scattering at pT > 6 GeV/c",
    status: "refuted",
    updated: "2024-01-08 09:30 UTC",
    source: "Manuscript \u00a75.3",
    chi2ndf: 4.21,
  },
  {
    id: "CLM-010",
    claim: "Elastic slope B(s) \u2248 B\u2080 + 2\u03b1\u2032 ln(s/s\u2080) increases logarithmically with energy",
    status: "supported",
    updated: "2024-01-07 14:20 UTC",
    source: "arXiv:2401.00123",
    chi2ndf: 1.08,
  },
  {
    id: "CLM-011",
    claim: "\u03c3_el/\u03c3_tot ratio approaches unitarity limit: \u03c3_el/\u03c3_tot \u2192 0.5 at LHC energies",
    status: "sanity",
    updated: "2024-01-06 16:00 UTC",
    source: "Manuscript \u00a76.1",
    chi2ndf: 1.29,
  },
  {
    id: "CLM-012",
    claim: "Dip-bump structure in |t| \u2248 0.5 GeV\u00b2 reproduced by double pomeron exchange",
    status: "supported",
    updated: "2024-01-05 11:10 UTC",
    source: "arXiv:2309.12345",
    chi2ndf: 1.17,
  },
]

const STAT_COUNTS = {
  open:      CLAIMS.filter((c) => c.status === "open").length,
  sanity:    CLAIMS.filter((c) => c.status === "sanity").length,
  supported: CLAIMS.filter((c) => c.status === "supported").length,
  refuted:   CLAIMS.filter((c) => c.status === "refuted").length,
}

function Chi2Cell({ value }: { value: number | null }) {
  if (value === null)
    return <span style={{ color: "var(--muted-foreground)" }}>—</span>

  const color =
    value > 2.5
      ? "var(--status-refuted)"
      : value > 1.5
      ? "var(--amber)"
      : "var(--foreground)"

  return (
    <span className="font-mono text-xs" style={{ color }}>
      {value.toFixed(2)}
    </span>
  )
}

function StatusPill({ status }: { status: ClaimStatus }) {
  const cfg = STATUS_CFG[status]
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium whitespace-nowrap"
      style={{ color: cfg.text, background: cfg.bg }}
    >
      {cfg.label}
    </span>
  )
}

export function EvidenceLedger() {
  return (
    <section className="px-10 py-8 space-y-8 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-baseline gap-4">
        <h1 className="text-2xl font-semibold tracking-tight text-balance">
          Evidence Ledger
        </h1>
        <div className="flex items-center gap-1.5">
          <span
            className="w-2 h-2 rounded-full live-dot"
            style={{ background: "var(--status-supported)" }}
          />
          <span
            className="text-[10px] font-mono tracking-widest uppercase"
            style={{ color: "var(--muted-foreground)" }}
          >
            Live
          </span>
        </div>
        <span className="ml-auto text-xs font-mono" style={{ color: "var(--muted-foreground)" }}>
          {CLAIMS.length} claims · last sync 14:32 UTC
        </span>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {(
          [
            { key: "open",      label: "Open" },
            { key: "sanity",    label: "Sanity checked" },
            { key: "supported", label: "Supported" },
            { key: "refuted",   label: "Refuted" },
          ] as { key: ClaimStatus; label: string }[]
        ).map(({ key, label }) => {
          const cfg = STATUS_CFG[key]
          return (
            <div
              key={key}
              className="rounded border p-5 space-y-2"
              style={{ background: "var(--card)", borderColor: "var(--border)" }}
            >
              <div className="flex items-center gap-2">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ background: cfg.text }}
                />
                <span
                  className="text-xs font-mono"
                  style={{ color: "var(--muted-foreground)" }}
                >
                  {label}
                </span>
              </div>
              <p
                className="text-4xl font-semibold tracking-tight tabular-nums"
                style={{ color: cfg.text }}
              >
                {STAT_COUNTS[key]}
              </p>
              <p className="text-xs font-mono" style={{ color: "var(--muted-foreground)" }}>
                claims
              </p>
            </div>
          )
        })}
      </div>

      {/* Claims table */}
      <div
        className="rounded border overflow-hidden"
        style={{ borderColor: "var(--border)" }}
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr
                className="border-b"
                style={{
                  background: "var(--muted)",
                  borderColor: "var(--border)",
                }}
              >
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-20">
                  ID
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground">
                  Claim
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-36">
                  Status
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-40">
                  Last update
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-44">
                  Source
                </th>
                <th className="text-right px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-24">
                  {"\u03c7\u00b2/ndf"}
                </th>
              </tr>
            </thead>
            <tbody>
              {CLAIMS.map((c, i) => (
                <tr
                  key={c.id}
                  className="border-b transition-colors hover:bg-muted/20"
                  style={{
                    borderColor: "var(--border)",
                    background: i % 2 === 0 ? "transparent" : "var(--card)",
                  }}
                >
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                    {c.id}
                  </td>
                  <td className="px-4 py-3 text-sm leading-relaxed text-foreground max-w-md">
                    {c.claim}
                  </td>
                  <td className="px-4 py-3">
                    <StatusPill status={c.status} />
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground whitespace-nowrap">
                    {c.updated}
                  </td>
                  <td className="px-4 py-3">
                    <a
                      href="#"
                      className="inline-flex items-center gap-1 font-mono text-xs hover:underline underline-offset-2 transition-colors"
                      style={{ color: "var(--status-open)" }}
                    >
                      {c.source}
                      <ExternalLink className="w-3 h-3 shrink-0" />
                    </a>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Chi2Cell value={c.chi2ndf} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-6 pb-2">
        {(Object.entries(STATUS_CFG) as [ClaimStatus, (typeof STATUS_CFG)[ClaimStatus]][]).map(
          ([key, cfg]) => (
            <div key={key} className="flex items-center gap-1.5">
              <span
                className="w-2 h-2 rounded-full"
                style={{ background: cfg.text }}
              />
              <span
                className="text-[11px] font-mono"
                style={{ color: "var(--muted-foreground)" }}
              >
                {cfg.label}
              </span>
            </div>
          )
        )}
        <span
          className="ml-auto text-[11px] font-mono"
          style={{ color: "var(--muted-foreground)" }}
        >
          {"\u03c7\u00b2/ndf"}&nbsp;
          <span style={{ color: "var(--amber)" }}>amber &gt;1.5</span>
          {" · "}
          <span style={{ color: "var(--status-refuted)" }}>red &gt;2.5</span>
        </span>
      </div>
    </section>
  )
}
