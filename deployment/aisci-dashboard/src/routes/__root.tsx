import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Outlet, createRootRouteWithContext, useRouter, redirect } from "@tanstack/react-router";
import { fetchProjects } from "@/lib/api";
import { useEffect } from "react";

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

const CAPABILITY_MAP: Record<string, string> = {
  fits: "fit_validation",
  literature: "literature",
  jobs: "fit_validation",
  tasks: "tasks",
  evidence: "evidence",
  agents: "tasks",
  anomalies: "fit_validation",
};

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  beforeLoad: async ({ location }) => {
    const match = location.pathname.match(/^\/projects\/([^/]+)\/([^/]+)/);
    if (match) {
      const projectId = match[1];
      const subRoute = match[2];
      const reqCap = CAPABILITY_MAP[subRoute];
      if (reqCap) {
        try {
          const projects = await fetchProjects();
          const p = projects.find((p) => p.id === projectId);
          if (p && !p.capabilities.includes(reqCap)) {
            throw redirect({ to: `/projects/${projectId}` as any });
          }
        } catch (err) {
          if (err instanceof Error && err.message.includes("redirect")) throw err;
          console.error("Failed to fetch projects for gating", err);
        }
      }
    }
  },
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootComponent() {
  const { queryClient } = Route.useRouteContext();

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex min-h-screen w-full bg-background text-foreground dark">
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
