import type { ReactNode } from "react";

export function PageShell({ children }: { children: ReactNode }) {
  return (
    <div className="fade-in-up mx-auto w-full max-w-[1400px] px-4 py-6 md:px-6 md:py-8">
      {children}
    </div>
  );
}
