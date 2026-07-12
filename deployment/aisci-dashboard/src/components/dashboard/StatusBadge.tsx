import { cn } from "@/lib/utils";
import { CircleDot, Loader2, TriangleAlert, CheckCircle2, Clock } from "lucide-react";

type Status = "pending" | "queued" | "running" | "anomaly" | "success";

const config: Record<
  Status,
  { label: string; icon: typeof CircleDot; className: string; dot: string; spin?: boolean }
> = {
  pending: {
    label: "Pending",
    icon: Clock,
    className: "bg-muted/60 text-muted-foreground ring-1 ring-border",
    dot: "bg-muted-foreground",
  },
  queued: {
    label: "Queued",
    icon: CircleDot,
    className: "bg-violet-brand/10 text-violet-brand ring-1 ring-violet-brand/30",
    dot: "bg-violet-brand",
  },
  running: {
    label: "Running",
    icon: Loader2,
    className: "bg-cyan-brand/10 text-cyan-brand ring-1 ring-cyan-brand/40",
    dot: "bg-cyan-brand",
    spin: true,
  },
  anomaly: {
    label: "Anomaly",
    icon: TriangleAlert,
    className: "bg-rose-brand/10 text-rose-brand ring-1 ring-rose-brand/40",
    dot: "bg-rose-brand",
  },
  success: {
    label: "Success",
    icon: CheckCircle2,
    className: "bg-emerald-brand/10 text-emerald-brand ring-1 ring-emerald-brand/40",
    dot: "bg-emerald-brand",
  },
};

export function StatusBadge({ status, className }: { status: Status; className?: string }) {
  const c = config[status];
  const Icon = c.icon;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-medium tracking-tight",
        c.className,
        className,
      )}
    >
      <Icon className={cn("h-3 w-3", c.spin && "animate-spin")} />
      {c.label}
    </span>
  );
}

export function StatusDot({ status }: { status: Status }) {
  const c = config[status];
  return (
    <span className="relative flex h-2 w-2">
      {status === "running" && (
        <span
          className={cn(
            "absolute inline-flex h-full w-full animate-ping rounded-full opacity-70",
            c.dot,
          )}
        />
      )}
      <span className={cn("relative inline-flex h-2 w-2 rounded-full", c.dot)} />
    </span>
  );
}
