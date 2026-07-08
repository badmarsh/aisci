"use client"

import {
  Inbox,
  CircleUserRound,
  ListTodo,
  FolderKanban,
  Zap,
  Bot,
  Users,
  BarChart3,
  Monitor,
  BookOpen,
  Settings,
  Atom,
} from "lucide-react"
import { cn } from "@/lib/utils"
import type { ReactNode } from "react"

type Item = {
  id: string
  label: string
  icon: typeof Inbox
}

type Group = {
  header?: string
  items: Item[]
}

const GROUPS: Group[] = [
  {
    items: [
      { id: "inbox",     label: "Inbox",     icon: Inbox },
      { id: "my-issues", label: "My Issues", icon: CircleUserRound },
    ],
  },
  {
    header: "Workspace",
    items: [
      { id: "issues",      label: "Issues",      icon: ListTodo },
      { id: "projects",    label: "Projects",    icon: FolderKanban },
      { id: "autopilot",   label: "Autopilot",   icon: Zap },
      { id: "agents",      label: "Agents",      icon: Bot },
      { id: "squads",      label: "Squads",      icon: Users },
      { id: "usage",       label: "Usage",       icon: BarChart3 },
      { id: "hep-physics", label: "HEP Physics", icon: Atom },
    ],
  },
  {
    header: "Configure",
    items: [
      { id: "runtimes", label: "Runtimes", icon: Monitor },
      { id: "skills",   label: "Skills",   icon: BookOpen },
      { id: "settings", label: "Settings", icon: Settings },
    ],
  },
]

const ACTIVE_ID = "hep-physics"

interface MulticaShellProps {
  children: ReactNode
}

/**
 * Outer shell that mounts the HEP Physics console inside Multica's chrome.
 * The left nav mirrors Multica's primary menu so the console reads as a
 * first-class entry rather than an external tool.
 */
export function MulticaShell({ children }: MulticaShellProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground font-sans">
      <aside
        className="flex flex-col w-60 shrink-0 border-r h-full"
        style={{
          background: "var(--sidebar)",
          borderColor: "var(--sidebar-border)",
        }}
        aria-label="Multica navigation"
      >
        {/* Workspace header */}
        <div
          className="flex items-center gap-2.5 h-14 px-5 shrink-0 border-b"
          style={{ borderColor: "var(--sidebar-border)" }}
        >
          <div
            className="w-7 h-7 rounded-md flex items-center justify-center text-[11px] font-semibold"
            style={{
              background: "var(--foreground)",
              color: "var(--background)",
            }}
            aria-hidden
          >
            M
          </div>
          <span className="text-sm font-medium tracking-tight text-foreground">
            Multica
          </span>
        </div>

        {/* Nav groups */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          {GROUPS.map((group, gi) => (
            <div key={gi} className={cn(gi > 0 && "mt-6")}>
              {group.header && (
                <p
                  className="px-2.5 mb-2 text-[11px] font-semibold tracking-wide"
                  style={{ color: "var(--foreground)" }}
                >
                  {group.header}
                </p>
              )}
              <ul className="flex flex-col gap-0.5">
                {group.items.map(({ id, label, icon: Icon }) => {
                  const active = id === ACTIVE_ID
                  return (
                    <li key={id}>
                      <button
                        type="button"
                        aria-current={active ? "page" : undefined}
                        className={cn(
                          "flex items-center gap-2.5 w-full px-2.5 py-1.5 rounded-md text-sm text-left transition-colors",
                          active
                            ? "font-medium"
                            : "text-muted-foreground hover:text-foreground"
                        )}
                        style={
                          active
                            ? {
                                background: "var(--sidebar-accent)",
                                color: "var(--sidebar-accent-foreground)",
                              }
                            : undefined
                        }
                      >
                        <Icon
                          className="w-[18px] h-[18px] shrink-0"
                          strokeWidth={1.75}
                          aria-hidden
                        />
                        <span>{label}</span>
                      </button>
                    </li>
                  )
                })}
              </ul>
            </div>
          ))}
        </nav>
      </aside>

      <div className="flex flex-1 min-w-0 flex-col">{children}</div>
    </div>
  )
}
