import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { useEffect, type ReactNode } from "react";

import appCss from "../styles.css?url";
import { reportLovableError } from "../lib/lovable-error-reporting";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { AppHeader } from "@/components/layout/AppHeader";
import { AppFooter } from "@/components/layout/AppFooter";
import { Toaster } from "@/components/ui/sonner";

function NotFoundComponent() {
  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <div className="text-center">
        <div className="font-mono text-sm text-primary">ERR_ROUTE_404</div>
        <h1 className="mt-3 text-4xl font-semibold">Instrument not connected</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          This control-plane module has not been deployed yet.
        </p>
        <a
          href="/"
          className="mt-6 inline-flex rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
        >
          Return to overview
        </a>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  console.error(error);
  const router = useRouter();
  useEffect(() => {
    reportLovableError(error, { boundary: "tanstack_root_error_component" });
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="text-center">
        <h1 className="text-xl font-semibold">Telemetry interrupted</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          The interface could not complete this request.
        </p>
        <button
          onClick={() => {
            router.invalidate();
            reset();
          }}
          className="mt-5 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground"
        >
          Reconnect
        </button>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "AiSci — Autonomous Research System" },
      {
        name: "description",
        content:
          "AiSci dashboard: monitor AI agents running high-energy physics fitting pipelines, literature intake, and evidence ledger.",
      },
      { name: "author", content: "AiSci" },
      { property: "og:title", content: "AiSci — Autonomous Research System" },
      {
        property: "og:description",
        content:
          "Physics fits, literature intake, and agent-proposed tasks for the AiSci autonomous research pipeline.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "icon", href: "/favicon.ico", type: "image/x-icon" },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
      },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark bg-background">
      <head>
        <HeadContent />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex min-h-screen w-full bg-background text-foreground">
        <AppSidebar />
        <div className="relative flex min-h-screen min-w-0 flex-1 flex-col">
          <div className="grid-backdrop pointer-events-none absolute inset-0 opacity-30" />
          <div className="relative flex min-h-screen flex-1 flex-col">
            <AppHeader />
            <main className="flex-1">
              <Outlet />
            </main>
            <AppFooter />
          </div>
        </div>
      </div>
      <Toaster theme="dark" position="bottom-right" richColors />
    </QueryClientProvider>
  );
}
