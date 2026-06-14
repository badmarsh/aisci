"use client"

import { Search, ChevronDown, UserRound, Terminal } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ThemeToggle } from "@/components/theme-toggle"
import type { Role } from "@/app/page"

const ROLES: { id: Role; label: string; initials: string; icon: typeof UserRound }[] = [
  { id: "scientist", label: "Scientist Robert", initials: "RB", icon: UserRound },
  { id: "devops",    label: "DevOps Marek",     initials: "MK", icon: Terminal },
]

interface TopBarProps {
  role: Role
  onRoleChange: (r: Role) => void
}

export function TopBar({ role, onRoleChange }: TopBarProps) {
  const current = ROLES.find((r) => r.id === role)!

  return (
    <header
      className="flex items-center h-12 shrink-0 px-4 gap-6 border-b"
      style={{ background: "var(--sidebar)", borderColor: "var(--sidebar-border)" }}
    >


      {/* Role switcher */}
      <DropdownMenu>
        <DropdownMenuTrigger
          render={
            <Button
              variant="ghost"
              size="sm"
              className="h-8 gap-2 text-xs font-mono text-foreground/80 hover:text-foreground px-2"
            />
          }
        >
          <current.icon className="w-3.5 h-3.5 shrink-0" />
          <span>{current.label}</span>
          <ChevronDown className="w-3 h-3 text-muted-foreground" />
        </DropdownMenuTrigger>
        <DropdownMenuContent
          align="start"
          className="w-48 font-mono text-xs"
          style={{ background: "var(--popover)", borderColor: "var(--border)" }}
        >
          {ROLES.map((r, i) => (
            <DropdownMenuItem
              key={r.id}
              onClick={() => onRoleChange(r.id)}
              className="gap-2 text-xs cursor-pointer"
            >
              <r.icon className="w-3.5 h-3.5 shrink-0" />
              <div className="flex flex-col">
                <span>{r.label}</span>
                <span className="text-muted-foreground font-normal">
                  {r.id === "scientist" ? "Evidence · Pipeline · Spectra" : "Ops · Tests · Infra"}
                </span>
              </div>
              {role === r.id && (
                <div
                  className="ml-auto w-1.5 h-1.5 rounded-full"
                  style={{ background: "var(--amber)" }}
                />
              )}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Global search */}
      <div className="flex-1 max-w-sm">
        <div className="relative">
          <Search
            className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 pointer-events-none"
            style={{ color: "var(--muted-foreground)" }}
          />
          <input
            type="search"
            placeholder="Search claims, runs, formulas…"
            className="w-full h-8 pl-8 pr-3 rounded text-xs font-mono bg-transparent border outline-none transition-colors placeholder:text-muted-foreground focus:ring-1 ring-ring"
            style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
          />
          <kbd
            className="absolute right-2 top-1/2 -translate-y-1/2 font-mono text-[10px] px-1 rounded border"
            style={{
              color: "var(--muted-foreground)",
              borderColor: "var(--border)",
              background: "var(--muted)",
            }}
          >
            ⌘K
          </kbd>
        </div>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Theme toggle */}
      <ThemeToggle />

      {/* Session avatar */}
      <Avatar className="w-7 h-7 cursor-pointer">
        <AvatarFallback
          className="text-[10px] font-mono font-semibold"
          style={{ background: "var(--muted)", color: "var(--foreground)" }}
        >
          {current.initials}
        </AvatarFallback>
      </Avatar>
    </header>
  )
}
