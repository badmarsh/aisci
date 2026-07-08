"use client"
import { Sidebar } from "./sidebar"
import { SearchBar } from "./search-bar"
import { WidgetCards } from "./widget-cards"
import { useState } from "react"

export function Search() {
  const [showWidgets, setShowWidgets] = useState(false)

  return (
    <>
      <Sidebar />

      {/* Main Content */}
      <main className="flex flex-1 flex-col bg-background">
        <div className="flex min-h-screen flex-col items-center justify-center px-4 md:px-6 pt-16 md:pt-0">
          <div className="w-full max-w-3xl space-y-6 md:space-y-8">
            <header className="flex items-center justify-center">
              <div className="flex items-center gap-0">
                <span className="text-2xl md:text-3xl font-bold tracking-tight text-foreground">perplexity</span>
                <span className="ml-1 rounded-full bg-teal-600 px-2 md:px-2.5 py-0.5 text-[10px] md:text-xs font-semibold text-white">
                  pro
                </span>
              </div>
            </header>

            <SearchBar onSearch={() => setShowWidgets(true)} />

            <footer className="flex items-center justify-center gap-1 pt-4">
              <p className="flex flex-wrap items-center justify-center gap-1 text-[11px] md:text-xs text-muted-foreground text-center">
                <span>Built entirely using</span>
                <a
                  href="https://v0.app"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-foreground hover:underline"
                >
                  v0.app
                </a>
                <span>with</span>
                <svg className="h-3 w-3 fill-red-500 shrink-0" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
                </svg>
                <span>by</span>
                <a
                  href="https://www.jess.vc"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-foreground hover:underline"
                >
                  Jessin
                </a>
              </p>
            </footer>

            {showWidgets && <WidgetCards />}
          </div>
        </div>
      </main>
    </>
  )
}
