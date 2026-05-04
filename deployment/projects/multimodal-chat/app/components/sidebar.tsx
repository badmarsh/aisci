"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Clock,
  Compass,
  Grid3x3,
  TrendingUp,
  MoreHorizontal,
  Bell,
  ArrowUpFromDot,
  Plus,
  Pin,
  Target,
  Star,
  LayoutGrid,
  FolderClosed,
  BarChart3,
  Search,
  Users,
  Bitcoin,
  MoreVertical,
  Calendar,
  Mail,
  Menu,
  X,
} from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import Image from "next/image"
import { UpgradeModal } from "./upgrade-modal"
import { AccountMenu } from "./account-menu"

const historyItems = [
  "How to build a modern web app",
  "Best practices for React hooks",
  "Understanding TypeScript generics",
  "Next.js 15 new features",
  "Tailwind CSS design patterns",
  "API integration strategies",
  "Database optimization tips",
  "Authentication implementation guide",
  "State management solutions",
  "Performance optimization techniques",
  "Responsive design approaches",
  "SEO best practices 2026",
  "Component composition patterns",
  "Error handling in async code",
  "Testing strategies for frontend",
  "Deployment workflows explained",
  "Git branching strategies",
  "Code review best practices",
  "Documentation writing tips",
  "Debugging techniques advanced",
]

export function Sidebar() {
  const [openPanel, setOpenPanel] = useState<string | null>(null)
  const [pinnedPanel, setPinnedPanel] = useState<string | null>(null)
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)
  const [showAccountMenu, setShowAccountMenu] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  const handlePanelChange = (panel: string) => {
    setOpenPanel(panel)
  }

  const handlePinToggle = (panel: string) => {
    if (pinnedPanel === panel) {
      setPinnedPanel(null)
      setOpenPanel(null)
    } else {
      setPinnedPanel(panel)
      setOpenPanel(panel)
    }
  }

  const sidebarContent = (
    <div
      className={`relative flex border-r border-border bg-background py-4 transition-all duration-300 ease-in-out z-50 h-full ${
        openPanel ? "w-[280px]" : "w-16"
      }`}
      onMouseLeave={() => {
        if (!pinnedPanel) {
          setOpenPanel(null)
        }
      }}
    >
      <div className="flex flex-col h-full w-16 shrink-0 items-center">
        {/* Logo */}
        <Button variant="ghost" size="icon" className="mb-6 h-10 w-10 shrink-0">
          <div className="flex h-8 w-8 items-center justify-center">
            <Image src="/images/perplexity-logo.png" alt="Logo" width={32} height={32} className="object-contain" />
          </div>
        </Button>

        <Button
          variant="ghost"
          className="mb-8 h-10 w-10 shrink-0 text-muted-foreground hover:text-foreground hover:bg-accent rounded-full bg-muted/50"
        >
          <Plus className="h-5 w-5 shrink-0" />
        </Button>

        <nav className="flex flex-1 flex-col gap-1">
          <div className="relative mb-2">
            <Button
              variant="ghost"
              onMouseEnter={() => handlePanelChange("history")}
              className={`h-10 w-10 shrink-0 mx-auto transition-colors ${
                openPanel === "history"
                  ? "text-foreground bg-accent"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              <Clock className="h-5 w-5" />
            </Button>
            <div className="text-[9px] text-muted-foreground text-center mt-1 font-medium">History</div>
          </div>

          <div className="relative mb-2">
            <Button
              variant="ghost"
              onMouseEnter={() => handlePanelChange("discover")}
              className={`h-10 w-10 shrink-0 mx-auto transition-colors ${
                openPanel === "discover"
                  ? "text-foreground bg-accent"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              <Compass className="h-5 w-5" />
            </Button>
            <div className="text-[9px] text-muted-foreground text-center mt-1 font-medium">Discover</div>
          </div>

          <div className="relative mb-2">
            <Button
              variant="ghost"
              onMouseEnter={() => handlePanelChange("spaces")}
              className={`h-10 w-10 shrink-0 mx-auto transition-colors ${
                openPanel === "spaces"
                  ? "text-foreground bg-accent"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              <Grid3x3 className="h-5 w-5" />
            </Button>
            <div className="text-[9px] text-muted-foreground text-center mt-1 font-medium">Spaces</div>
          </div>

          <div className="relative mb-2">
            <Button
              variant="ghost"
              onMouseEnter={() => handlePanelChange("finance")}
              className={`h-10 w-10 shrink-0 mx-auto transition-colors ${
                openPanel === "finance"
                  ? "text-foreground bg-accent"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              <TrendingUp className="h-5 w-5" />
            </Button>
            <div className="text-[9px] text-muted-foreground text-center mt-1 font-medium">Finance</div>
          </div>

          <div className="relative mb-2">
            <Button
              variant="ghost"
              onMouseEnter={() => handlePanelChange("more")}
              className={`h-10 w-10 shrink-0 mx-auto transition-colors ${
                openPanel === "more"
                  ? "text-foreground bg-accent"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              <MoreHorizontal className="h-5 w-5" />
            </Button>
            <div className="text-[9px] text-muted-foreground text-center mt-1 font-medium">More</div>
          </div>

          <div className="relative mb-2">
            <Button
              variant="ghost"
              onMouseEnter={() => handlePanelChange("notifications")}
              className={`h-10 w-10 shrink-0 transition-colors ${
                openPanel === "notifications"
                  ? "text-foreground bg-accent"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              <Bell className="h-5 w-5 shrink-0" />
            </Button>
          </div>
        </nav>

        <div className="flex flex-col gap-1 pt-4 items-center">
          <Button
            variant="ghost"
            onClick={() => setShowAccountMenu(!showAccountMenu)}
            className="h-10 w-10 shrink-0 text-muted-foreground hover:text-foreground hover:bg-accent p-0"
          >
            <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-full overflow-visible ring-2 ring-primary/60">
              <div className="h-9 w-9 rounded-full overflow-hidden">
                <Image
                  src="/images/user-avatar.jpg"
                  alt="Profile"
                  width={36}
                  height={36}
                  className="object-cover"
                />
              </div>
              <span className="absolute -bottom-1 -right-1 text-[7px] font-bold bg-primary text-primary-foreground px-1 py-0.5 rounded">
                pro
              </span>
            </div>
          </Button>
          <div className="text-[9px] text-muted-foreground text-center font-medium">Account</div>

          <Button
            variant="ghost"
            onClick={() => setShowUpgradeModal(true)}
            className="h-10 w-10 shrink-0 text-muted-foreground hover:text-foreground hover:bg-accent"
          >
            <ArrowUpFromDot className="h-5 w-5 shrink-0" />
          </Button>
          <div className="text-[9px] text-muted-foreground text-center font-medium">Upgrade</div>
        </div>
      </div>

      {openPanel && (
        <div key={openPanel} className="w-[216px] bg-background border-r border-border">
          {openPanel === "history" && (
            <div className="flex flex-col h-full animate-in fade-in duration-300">
              <div className="flex items-center justify-between px-3 py-2.5">
                <h2 className="text-sm font-semibold">History</h2>
                <Button
                  variant="ghost"
                  size="icon"
                  className={`h-6 w-6 transition-colors ${pinnedPanel === "history" ? "text-primary" : ""}`}
                  onClick={() => handlePinToggle("history")}
                >
                  <Pin
                    className={`h-3.5 w-3.5 transition-transform ${pinnedPanel === "history" ? "rotate-45" : ""}`}
                  />
                </Button>
              </div>
              <div className="px-3 py-1.5">
                <h3 className="text-[11px] font-medium text-muted-foreground">Recent</h3>
              </div>
              <ScrollArea className="flex-1 px-1.5">
                <div className="space-y-0 pb-2">
                  {historyItems.map((item, index) => (
                    <button
                      key={index}
                      className="group w-full text-left px-2 py-1.5 text-[13px] leading-tight text-foreground hover:bg-accent rounded transition-all duration-200 relative"
                    >
                      <span className="block truncate pr-4">{item}</span>
                      <span className="absolute right-2 top-1.5 bottom-1.5 w-8 bg-gradient-to-l from-background via-background to-transparent group-hover:from-accent group-hover:via-accent pointer-events-none transition-colors duration-200" />
                    </button>
                  ))}
                </div>
              </ScrollArea>
              <div className="px-3 py-2">
                <button className="text-xs text-primary hover:underline">View All</button>
              </div>
            </div>
          )}

          {openPanel === "discover" && (
            <div className="flex flex-col h-full animate-in fade-in duration-300">
              <div className="flex items-center justify-between px-3 py-2.5">
                <h2 className="text-sm font-semibold">Discover</h2>
                <Button
                  variant="ghost"
                  size="icon"
                  className={`h-6 w-6 transition-colors ${pinnedPanel === "discover" ? "text-primary" : ""}`}
                  onClick={() => handlePinToggle("discover")}
                >
                  <Pin
                    className={`h-3.5 w-3.5 transition-transform ${pinnedPanel === "discover" ? "rotate-45" : ""}`}
                  />
                </Button>
              </div>
              <div className="p-1.5">
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Target className="h-4 w-4 shrink-0" />
                  <span className="font-normal">For You</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Star className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Top</span>
                </button>
              </div>
            </div>
          )}

          {openPanel === "spaces" && (
            <div className="flex flex-col h-full animate-in fade-in duration-300">
              <div className="flex items-center justify-between px-3 py-2.5">
                <h2 className="text-sm font-semibold">Spaces</h2>
                <Button
                  variant="ghost"
                  size="icon"
                  className={`h-6 w-6 transition-colors ${pinnedPanel === "spaces" ? "text-primary" : ""}`}
                  onClick={() => handlePinToggle("spaces")}
                >
                  <Pin
                    className={`h-3.5 w-3.5 transition-transform ${pinnedPanel === "spaces" ? "rotate-45" : ""}`}
                  />
                </Button>
              </div>
              <div className="p-1.5">
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <LayoutGrid className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Templates</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Plus className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Create new Space</span>
                </button>
              </div>
              <div className="px-1.5 pb-1.5">
                <div className="flex items-center justify-between px-2.5 py-1.5">
                  <h3 className="text-[11px] font-medium text-muted-foreground">Private</h3>
                  <Button variant="ghost" size="icon" className="h-5 w-5">
                    <Plus className="h-3 w-3" />
                  </Button>
                </div>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <FolderClosed className="h-4 w-4 shrink-0" />
                  <span className="font-normal">My Space</span>
                </button>
              </div>
            </div>
          )}

          {openPanel === "finance" && (
            <div className="flex flex-col h-full animate-in fade-in duration-300">
              <div className="flex items-center justify-between px-3 py-2.5">
                <h2 className="text-sm font-semibold">Finance</h2>
                <Button
                  variant="ghost"
                  size="icon"
                  className={`h-6 w-6 transition-colors ${pinnedPanel === "finance" ? "text-primary" : ""}`}
                  onClick={() => handlePinToggle("finance")}
                >
                  <Pin
                    className={`h-3.5 w-3.5 transition-transform ${pinnedPanel === "finance" ? "rotate-45" : ""}`}
                  />
                </Button>
              </div>
              <div className="p-1.5">
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <span className="text-base shrink-0">🇺🇸</span>
                  <span className="font-normal">US Markets</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Bitcoin className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Crypto</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <BarChart3 className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Earnings</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <TrendingUp className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Predictions</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Search className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Screener</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Users className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Politicians</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Star className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Watchlist</span>
                </button>
              </div>
              <div className="px-3 py-1.5">
                <h3 className="text-[11px] font-medium text-muted-foreground">Get started</h3>
              </div>
              <div className="p-1.5">
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Search className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Stock analysis</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Search className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Stock comparison</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Search className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Crypto price</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Search className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Currency conversion</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Search className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Market news</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Search className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Explainer</span>
                </button>
              </div>
            </div>
          )}

          {openPanel === "more" && (
            <div className="flex flex-col h-full animate-in fade-in duration-300">
              <div className="p-1.5 pt-3">
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Compass className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Discover</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <Grid3x3 className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Spaces</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <TrendingUp className="h-4 w-4 shrink-0" />
                  <span className="font-normal">Finance</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <span className="text-base shrink-0">✈️</span>
                  <span className="font-normal">Travel</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <span className="text-base shrink-0">📚</span>
                  <span className="font-normal">Academic</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <span className="text-base shrink-0">🏆</span>
                  <span className="font-normal">Sports</span>
                </button>
                <button className="w-full flex items-center gap-2.5 px-2.5 py-2 text-[13px] hover:bg-accent rounded transition-colors">
                  <span className="text-base shrink-0">🎯</span>
                  <span className="font-normal">Patents</span>
                </button>
              </div>
              <div className="mt-auto px-1.5 pb-3 pt-2">
                <button className="w-full flex items-center justify-between px-2.5 py-2 text-[13px] text-muted-foreground hover:text-foreground hover:bg-accent rounded transition-colors group">
                  <span className="font-normal">Customize Sidebar</span>
                  <span className="text-base transition-transform group-hover:translate-x-0.5">→</span>
                </button>
              </div>
            </div>
          )}

          {openPanel === "notifications" && (
            <div className="flex flex-col h-full animate-in fade-in duration-300">
              <div className="flex items-center justify-between px-3 py-2.5">
                <h2 className="text-sm font-semibold">Notifications</h2>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="icon" className="h-6 w-6">
                    <MoreVertical className="h-3.5 w-3.5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-6 w-6">
                    <Calendar className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
              <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
                <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-muted/50 mb-4">
                  <Mail className="h-7 w-7 text-muted-foreground" />
                </div>
                <p className="text-sm text-muted-foreground text-center">Your notifications will appear here</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )

  return (
    <>
      {sidebarContent}
      <AccountMenu isOpen={showAccountMenu} onClose={() => setShowAccountMenu(false)} />
      <UpgradeModal isOpen={showUpgradeModal} onClose={() => setShowUpgradeModal(false)} />
    </>
  )
}
