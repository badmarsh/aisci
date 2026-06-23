"use client"

import * as React from "react"
import { useTheme } from "next-themes"
import { Sun, Moon } from "lucide-react"

import { Switch } from "@/components/ui/switch"

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme()
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <div className="flex items-center gap-2 px-2 opacity-0">
      <Sun className="h-3 w-3" />
      <Switch size="sm" checked={false} />
      <Moon className="h-3 w-3" />
    </div>
  }

  const isDark = resolvedTheme === "dark"

  return (
    <div className="flex items-center gap-2 px-2">
      <Sun className="h-3 w-3 text-muted-foreground" />
      <Switch 
        checked={isDark} 
        onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")} 
        size="sm"
      />
      <Moon className="h-3 w-3 text-muted-foreground" />
    </div>
  )
}
