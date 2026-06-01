import {
  ScrollText,
  GitMerge,
  Activity,
  BadgeCheck,
  FlaskConical,
  Server,
} from "lucide-react"
import { cn } from "@/lib/utils"
import type { Role, Section } from "@/app/page"

const NAV_ITEMS: {
  id: Section
  label: string
  icon: typeof ScrollText
  hint: string
}[] = [
  { id: "evidence",   label: "Evidence",   icon: ScrollText,   hint: "Scientific claims ledger" },
  { id: "pipeline",   label: "Pipeline",   icon: GitMerge,     hint: "Fitting pipeline monitor" },
  { id: "spectra",    label: "Spectra",    icon: Activity,     hint: "Interactive spectra plotter" },
  { id: "validation", label: "Validation", icon: BadgeCheck,   hint: "Symbolic validation" },
  { id: "tests",      label: "Tests",      icon: FlaskConical, hint: "pytest test results" },
  { id: "ops",        label: "Ops",        icon: Server,       hint: "Infrastructure & deployments" },
]

interface LeftRailProps {
  role: Role
  section: Section
  onSection: (s: Section) => void
}

export function LeftRail({ role, section, onSection }: LeftRailProps) {
  return (
    <nav
      className="flex flex-col w-52 shrink-0 border-r h-full py-5"
      style={{
        background: "var(--sidebar)",
        borderColor: "var(--sidebar-border)",
      }}
      aria-label="Primary navigation"
    >
      <p
        className="px-4 mb-3 text-[10px] font-mono font-semibold tracking-[0.16em] uppercase"
        style={{ color: "var(--muted-foreground)" }}
      >
        Navigation
      </p>

      <ul className="flex flex-col gap-0.5 px-2">
        {NAV_ITEMS.map(({ id, label, icon: Icon, hint }) => {
          const active = section === id
          const isOpsForScientist = id === "ops" && role === "scientist"
          const isEvidenceForDevops = id === "evidence" && role === "devops"
          const dimmed = isOpsForScientist || isEvidenceForDevops

          return (
            <li key={id}>
              <button
                onClick={() => onSection(id)}
                title={hint}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "relative flex items-center gap-3 w-full px-3 py-2 text-sm rounded transition-colors text-left",
                  active
                    ? "text-foreground font-medium"
                    : dimmed
                    ? "text-muted-foreground/40 hover:text-muted-foreground/60"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/30"
                )}
              >
                {/* Active indicator */}
                {active && (
                  <span
                    className="absolute left-0 top-1/2 -translate-y-1/2 h-4 w-0.5 rounded-r"
                    style={{ background: "var(--amber)" }}
                  />
                )}

                <Icon
                  className="w-4 h-4 shrink-0"
                  style={active ? { color: "var(--amber)" } : undefined}
                />
                <span className="font-mono text-xs tracking-wide">{label}</span>

                {/* Role badge for landing sections */}
                {((id === "evidence" && role === "scientist") ||
                  (id === "ops" && role === "devops")) && (
                  <span
                    className="ml-auto text-[9px] font-mono px-1 py-0.5 rounded"
                    style={{
                      background: "var(--amber-bg)",
                      color: "var(--amber)",
                    }}
                  >
                    home
                  </span>
                )}
              </button>
            </li>
          )
        })}
      </ul>

      {/* Footer meta */}
      <div className="mt-auto px-4 pt-6">
        <div
          className="border rounded p-3 space-y-1"
          style={{ borderColor: "var(--border)" }}
        >
          <p className="text-[10px] font-mono" style={{ color: "var(--muted-foreground)" }}>
            Session
          </p>
          <p className="text-xs font-mono text-foreground">
            {role === "scientist" ? "Scientist Robert" : "DevOps Marek"}
          </p>
          <p className="text-[10px] font-mono" style={{ color: "var(--muted-foreground)" }}>
            Run 2024-01 · Rev 14
          </p>
        </div>
      </div>
    </nav>
  )
}
