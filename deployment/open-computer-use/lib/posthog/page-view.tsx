"use client"

import posthog from "posthog-js"
import { usePathname, useSearchParams } from "next/navigation"
import { useEffect, Suspense } from "react"

function PostHogPageViewInner() {
  const pathname = usePathname()
  const searchParams = useSearchParams()

  useEffect(() => {
    if (!pathname) return

    let url = window.origin + pathname
    const search = searchParams.toString()
    if (search) {
      url += "?" + search
    }

    posthog.capture("$pageview", { $current_url: url })
  }, [pathname, searchParams])

  return null
}

export function PostHogPageView() {
  return (
    <Suspense fallback={null}>
      <PostHogPageViewInner />
    </Suspense>
  )
}
