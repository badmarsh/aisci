import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface PanelProps {
  title: string;
  label: string;
  icon: LucideIcon;
  action: string;
  className?: string;
  children: ReactNode;
}

export function Panel({
  title,
  label,
  icon: Icon,
  action,
  className,
  children,
}: PanelProps) {
  return (
    <article
      className={cn(
        "glass-card rounded-xl p-4 transition-colors hover:border-primary/25",
        className,
      )}
    >
      <header className="flex items-start justify-between gap-3">
        <div className="flex gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <Icon className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold">{title}</h2>
            <p className="mt-0.5 text-[11px] text-muted-foreground">{label}</p>
          </div>
        </div>
        <span className="rounded-md border border-border bg-secondary/60 px-2 py-1 font-mono text-[10px] uppercase text-muted-foreground">
          {action}
        </span>
      </header>
      {children}
    </article>
  );
}
