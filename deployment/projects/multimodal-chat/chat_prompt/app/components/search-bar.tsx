"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Search, Focus, Grid3x3, Globe, Cpu, Paperclip, Mic } from "lucide-react"

const suggestions = ["test", "test internet speed", "test my speed", "testament", "test my internet speed"]

type Mode = "search" | "deep-research" | "create"

const modeTooltips = {
  search: {
    title: "Search",
    description: "Get fast answers to everyday questions",
    proEnabled: true,
    proDescription: "Advanced search with 10x the sources; powered by top models",
    footer: "Unlimited access for subscribers",
  },
  "deep-research": {
    title: "Deep research",
    description: "Create in-depth reports with more sources, charts, and advanced reasoning",
    proEnabled: true,
    proDescription: "In-depth reports with more sources, charts, and advanced reasoning",
    footer: "Extended access for subscribers",
  },
  create: {
    title: "Create files and apps",
    description: "Turn your ideas into docs, slides, dashboards, and more",
    badge: "New",
    proEnabled: true,
    proDescription: "Turn your ideas into completed docs, slides, dashboards, and more",
    footer: "48 queries remaining this month",
  },
}

export function SearchBar({ onSearch }: { onSearch?: () => void }) {
  const [query, setQuery] = useState("")
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [isFocused, setIsFocused] = useState(false)
  const [activeMode, setActiveMode] = useState<Mode>("search")
  const [hoveredMode, setHoveredMode] = useState<Mode | null>(null)
  const [tooltipOffset, setTooltipOffset] = useState(0)

  const buttonRefs = useRef<{ [key in Mode]?: HTMLButtonElement }>({})

  const handleMouseEnter = (mode: Mode) => {
    setHoveredMode(mode)
    const button = buttonRefs.current[mode]
    if (button) {
      const buttonRect = button.getBoundingClientRect()
      const containerRect = button.closest(".relative")?.getBoundingClientRect()
      if (containerRect) {
        const buttonCenter = buttonRect.left + buttonRect.width / 2 - containerRect.left
        setTooltipOffset(buttonCenter)
      }
    }
  }

  return (
    <div className="relative">
      <div
        className={`animate-in fade-in slide-in-from-bottom-4 duration-500 rounded-2xl border-2 bg-card shadow-[0_4px_20px_rgb(0,0,0,0.03)] transition-all hover:shadow-[0_4px_30px_rgb(0,0,0,0.06)] ${
          isFocused ? "border-teal-500/50 ring-1 ring-teal-500/20" : "border-teal-500/20 hover:border-teal-500/30"
        }`}
      >
        {/* Input */}
        <div className="px-4 md:px-5 py-3 md:py-3.5">
          <input
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setShowSuggestions(e.target.value.length > 0)
            }}
            onFocus={() => {
              setIsFocused(true)
              if (query.length > 0) setShowSuggestions(true)
            }}
            onBlur={() => {
              setIsFocused(false)
              setTimeout(() => setShowSuggestions(false), 150)
            }}
            placeholder="Ask anything..."
            className="w-full border-0 bg-transparent text-[14px] md:text-[15px] text-foreground placeholder:text-muted-foreground/60 focus:outline-none"
          />
        </div>

        <div className="flex items-center justify-between px-2 md:px-2.5 py-2 gap-2">
          <div className="relative flex items-center gap-0.5 rounded-lg bg-accent/30 p-0.5">
            <Button
              ref={(el) => {
                if (el) buttonRefs.current.search = el
              }}
              variant="ghost"
              size="icon"
              onMouseEnter={() => handleMouseEnter("search")}
              onMouseLeave={() => setHoveredMode(null)}
              onClick={() => setActiveMode("search")}
              className={`h-8 w-8 md:h-9 md:w-9 rounded-md transition-all duration-300 ${
                activeMode === "search"
                  ? "border-2 border-teal-500/60 bg-background text-teal-600 shadow-sm hover:border-teal-500/70 hover:text-teal-700 dark:text-teal-500"
                  : "border-2 border-transparent text-muted-foreground hover:bg-accent/60 hover:text-foreground"
              }`}
            >
              <Search className="h-4 w-4 md:h-[17px] md:w-[17px]" />
            </Button>
            <Button
              ref={(el) => {
                if (el) buttonRefs.current["deep-research"] = el
              }}
              variant="ghost"
              size="icon"
              onMouseEnter={() => handleMouseEnter("deep-research")}
              onMouseLeave={() => setHoveredMode(null)}
              onClick={() => setActiveMode("deep-research")}
              className={`h-8 w-8 md:h-9 md:w-9 rounded-md transition-all duration-300 ${
                activeMode === "deep-research"
                  ? "border-2 border-teal-500/60 bg-background text-teal-600 shadow-sm hover:border-teal-500/70 hover:text-teal-700 dark:text-teal-500"
                  : "border-2 border-transparent text-muted-foreground hover:bg-accent/60 hover:text-foreground"
              }`}
            >
              <Focus className="h-4 w-4 md:h-[17px] md:w-[17px]" />
            </Button>
            <Button
              ref={(el) => {
                if (el) buttonRefs.current.create = el
              }}
              variant="ghost"
              size="icon"
              onMouseEnter={() => handleMouseEnter("create")}
              onMouseLeave={() => setHoveredMode(null)}
              onClick={() => setActiveMode("create")}
              className={`h-8 w-8 md:h-9 md:w-9 rounded-md transition-all duration-300 ${
                activeMode === "create"
                  ? "border-2 border-teal-500/60 bg-background text-teal-600 shadow-sm hover:border-teal-500/70 hover:text-teal-700 dark:text-teal-500"
                  : "border-2 border-transparent text-muted-foreground hover:bg-accent/60 hover:text-foreground"
              }`}
            >
              <Grid3x3 className="h-4 w-4 md:h-[17px] md:w-[17px]" />
            </Button>
          </div>

          <div className="flex items-center gap-0.5">
            <Button
              variant="ghost"
              size="icon"
              className="hidden sm:flex h-9 w-9 rounded-lg text-muted-foreground transition-all hover:bg-accent/60 hover:text-foreground"
            >
              <Globe className="h-[17px] w-[17px]" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="hidden sm:flex h-9 w-9 rounded-lg text-muted-foreground transition-all hover:bg-accent/60 hover:text-foreground"
            >
              <Cpu className="h-[17px] w-[17px]" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 md:h-9 md:w-9 rounded-lg text-muted-foreground transition-all hover:bg-accent/60 hover:text-foreground"
            >
              <Paperclip className="h-4 w-4 md:h-[17px] md:w-[17px]" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 md:h-9 md:w-9 rounded-lg text-muted-foreground transition-all hover:bg-accent/60 hover:text-foreground"
            >
              <Mic className="h-4 w-4 md:h-[17px] md:w-[17px]" />
            </Button>
            <Button
              size="icon"
              onClick={() => onSearch?.()}
              className="h-8 w-8 md:h-9 md:w-9 rounded-lg bg-teal-600 text-white transition-all hover:bg-teal-700 active:scale-95 shrink-0"
            >
              <svg className="h-3.5 w-3.5 md:h-4 md:w-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="4" y="8" width="2" height="8" rx="1" fill="currentColor" />
                <rect x="8" y="4" width="2" height="16" rx="1" fill="currentColor" />
                <rect x="12" y="6" width="2" height="12" rx="1" fill="currentColor" />
                <rect x="16" y="10" width="2" height="4" rx="1" fill="currentColor" />
                <rect x="20" y="7" width="2" height="10" rx="1" fill="currentColor" />
              </svg>
            </Button>
          </div>
        </div>

        {showSuggestions && query && (
          <div className="animate-in fade-in slide-in-from-top-2 duration-200 border-t border-border/40">
            {suggestions
              .filter((s) => s.toLowerCase().includes(query.toLowerCase()))
              .map((suggestion, index) => (
                <button
                  key={index}
                  onMouseDown={(e) => {
                    e.preventDefault()
                    setQuery(suggestion)
                    setShowSuggestions(false)
                  }}
                  className="flex w-full items-center gap-3 px-5 py-2.5 text-left text-[13px] text-foreground transition-colors hover:bg-accent/50"
                >
                  <Search className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="font-normal">{suggestion}</span>
                </button>
              ))}
          </div>
        )}
      </div>

      {hoveredMode && (
        <div
          className="animate-in fade-in slide-in-from-top-2 duration-200 absolute top-full mt-2 w-[340px] rounded-xl border border-border/50 bg-[#1a1a1a] p-3 text-white shadow-xl"
          style={{
            left: `${tooltipOffset}px`,
            transform: "translateX(-50%)",
          }}
        >
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <h3 className="text-sm font-semibold">{modeTooltips[hoveredMode].title}</h3>
                {modeTooltips[hoveredMode].badge && (
                  <span className="rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] font-medium text-zinc-300">
                    {modeTooltips[hoveredMode].badge}
                  </span>
                )}
              </div>
              <p className="text-[11px] text-zinc-300 mb-2.5 leading-relaxed">
                {modeTooltips[hoveredMode].description}
              </p>
            </div>
          </div>

          <div className="border-t border-zinc-800 pt-2.5">
            <div className="flex items-center gap-1.5 mb-1">
              <span className="rounded bg-teal-600 px-1.5 py-0.5 text-[9px] font-bold text-white">pro</span>
              <div className="flex items-center gap-1">
                <span className="text-[11px] font-medium text-teal-400">Enabled</span>
                <svg className="h-3 w-3 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <p className="text-[11px] text-zinc-300 mb-1.5 leading-relaxed">
              {modeTooltips[hoveredMode].proDescription}
            </p>
            <p className="text-[10px] text-zinc-500">{modeTooltips[hoveredMode].footer}</p>
          </div>

          <div className="absolute -top-2 left-1/2 -translate-x-1/2 h-3 w-3 rotate-45 border-l border-t border-border/50 bg-[#1a1a1a]" />
        </div>
      )}
    </div>
  )
}
