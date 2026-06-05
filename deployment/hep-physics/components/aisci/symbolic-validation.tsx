import { CheckCircle2, XCircle, FileText } from "lucide-react"

interface Formula {
  id: string
  section: string
  description: string
  expression: string
  valid: boolean
  note: string
  dimensions: string
}

const FORMULAS: Formula[] = [
  {
    id: "F.01",
    section: "\u00a72.1",
    description: "Differential elastic cross-section",
    expression: "d\u03c3/dt = A\u00b7|F_N(t)|\u00b2\u00b7exp(Bt)",
    valid: true,
    note: "Dimensionally consistent",
    dimensions: "[mb\u00b7GeV\u207b\u00b2]",
  },
  {
    id: "F.02",
    section: "\u00a72.3",
    description: "Linear Regge trajectory",
    expression: "\u03b1(t) = \u03b1(0) + \u03b1\u2032t",
    valid: true,
    note: "Dimensionally consistent",
    dimensions: "[1]",
  },
  {
    id: "F.03",
    section: "\u00a73.1",
    description: "Total cross-section from optical theorem",
    expression: "\u03c3_tot = Im\u202fA(s,0) / s",
    valid: false,
    note: "Missing factor 16\u03c0 in denominator",
    dimensions: "[GeV\u207b\u00b2 \u2260 mb] — mismatch",
  },
  {
    id: "F.04",
    section: "\u00a73.2",
    description: "Ratio of real to imaginary forward amplitude",
    expression: "\u03c1(s) = Re\u202fA(s,0) / Im\u202fA(s,0)",
    valid: true,
    note: "Dimensionless ratio — consistent",
    dimensions: "[1]",
  },
  {
    id: "F.05",
    section: "\u00a74.1",
    description: "Logarithmic growth of elastic slope",
    expression: "B(s) = B\u2080 + 2\u03b1\u2032 ln(s/s\u2080)",
    valid: true,
    note: "Dimensionally consistent",
    dimensions: "[GeV\u207b\u00b2]",
  },
  {
    id: "F.06",
    section: "\u00a74.3",
    description: "Saturation of elastic-to-total ratio",
    expression: "\u03c3_el/\u03c3_tot \u2192 1/(16\u03c0B) as s \u2192 \u221e",
    valid: false,
    note: "LHS dimensionless [1]; RHS has units [GeV\u00b2] — mismatch",
    dimensions: "[1 \u2260 GeV\u00b2]",
  },
  {
    id: "F.07",
    section: "\u00a75.1",
    description: "Impact-parameter profile function",
    expression: "W(b,s) = (1/4\u03c0) \u222b d\u00b2q e^{iq\u00b7b} A(s,t)",
    valid: true,
    note: "Impact-parameter representation — consistent",
    dimensions: "[GeV\u207b\u00b2]",
  },
  {
    id: "F.08",
    section: "\u00a75.4",
    description: "Eikonal unitarisation",
    expression: "S(b,s) = exp[i\u03c7(b,s)]",
    valid: true,
    note: "S-matrix unitarity preserved — consistent",
    dimensions: "[1]",
  },
  {
    id: "F.09",
    section: "\u00a76.2",
    description: "Double-pomeron exchange amplitude",
    expression: "A_DPE(s,t) = g_1 g_2 \u03b2(t) (s/s\u2080)^{\u03b1(t)}",
    valid: true,
    note: "Dimensionally consistent with coupling convention",
    dimensions: "[mb\u00b7GeV\u207b\u00b2]",
  },
  {
    id: "F.10",
    section: "\u00a76.5",
    description: "Froissart-Martin bound",
    expression: "\u03c3_tot \u2264 (\u03c0/m_\u03c0\u00b2) ln\u00b2(s/s\u2080)",
    valid: false,
    note: "Prefactor \u03c0/m_\u03c0\u00b2 correct but s\u2080 definition inconsistent with \u00a72.1",
    dimensions: "[mb] — units OK but definition conflict",
  },
]

const PASS_COUNT = FORMULAS.filter((f) => f.valid).length
const FAIL_COUNT = FORMULAS.filter((f) => !f.valid).length

export function SymbolicValidation() {
  return (
    <section className="px-10 py-8 space-y-8 max-w-[900px]">
      {/* Header */}
      <div className="flex items-baseline gap-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          Symbolic Validation
        </h1>
        <span className="font-mono text-xs text-muted-foreground">
          Dimensional analysis · manuscript extraction
        </span>
      </div>

      {/* Summary row */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" style={{ color: "var(--status-supported)" }} />
          <span className="font-mono text-sm" style={{ color: "var(--status-supported)" }}>
            {PASS_COUNT} consistent
          </span>
        </div>
        <div className="flex items-center gap-2">
          <XCircle className="w-4 h-4" style={{ color: "var(--status-refuted)" }} />
          <span className="font-mono text-sm" style={{ color: "var(--status-refuted)" }}>
            {FAIL_COUNT} inconsistent
          </span>
        </div>
        <span className="text-xs font-mono text-muted-foreground ml-auto">
          {FORMULAS.length} formulas extracted · manuscript v14
        </span>
      </div>

      {/* Formula table */}
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
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-16">
                  ID
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-16">
                  Sect.
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground">
                  Description
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground">
                  Expression
                </th>
                <th className="text-left px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-24">
                  Dims
                </th>
                <th className="text-center px-4 py-2.5 font-mono text-[11px] font-semibold tracking-widest uppercase text-muted-foreground w-24">
                  Check
                </th>
              </tr>
            </thead>
            <tbody>
              {FORMULAS.map((f, i) => (
                <tr
                  key={f.id}
                  className="border-b transition-colors hover:bg-muted/20 group"
                  style={{
                    borderColor: "var(--border)",
                    background: i % 2 === 0 ? "transparent" : "var(--card)",
                  }}
                >
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground align-top">
                    {f.id}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground align-top whitespace-nowrap">
                    {f.section}
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground align-top leading-relaxed">
                    {f.description}
                  </td>
                  <td className="px-4 py-3 align-top">
                    <div
                      className="font-mono text-xs rounded px-2 py-1 inline-block"
                      style={{
                        background: "var(--muted)",
                        color: "var(--foreground)",
                      }}
                    >
                      {f.expression}
                    </div>
                    {/* Note on hover / always-visible on narrow */}
                    <p className="text-[11px] font-mono mt-1.5 leading-relaxed"
                       style={{ color: f.valid ? "var(--muted-foreground)" : "var(--status-refuted)" }}>
                      {f.note}
                    </p>
                  </td>
                  <td className="px-4 py-3 font-mono text-[11px] text-muted-foreground align-top whitespace-nowrap">
                    {f.dimensions}
                  </td>
                  <td className="px-4 py-3 align-top">
                    <div className="flex justify-center">
                      {f.valid ? (
                        <span
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-medium"
                          style={{
                            color: "var(--status-supported)",
                            background: "var(--status-supported-bg)",
                          }}
                        >
                          <CheckCircle2 className="w-3 h-3" />
                          pass
                        </span>
                      ) : (
                        <span
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-medium"
                          style={{
                            color: "var(--status-refuted)",
                            background: "var(--status-refuted-bg)",
                          }}
                        >
                          <XCircle className="w-3 h-3" />
                          fail
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Note */}
      <div
        className="flex items-start gap-3 rounded border p-4"
        style={{ borderColor: "var(--border)", background: "var(--card)" }}
      >
        <FileText
          className="w-4 h-4 shrink-0 mt-0.5"
          style={{ color: "var(--muted-foreground)" }}
        />
        <p className="text-xs font-mono leading-relaxed text-muted-foreground">
          Formulas extracted via LaTeX AST parser from manuscript v14.
          Dimensional analysis uses SI base units with GeV/c conventions.
          Inconsistent formulas (F.03, F.06, F.10) require author correction before submission.
        </p>
      </div>
    </section>
  )
}
