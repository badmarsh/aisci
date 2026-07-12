import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn("animate-pulse rounded-md bg-secondary/50", className)} />
  );
}

export function MetricCardSkeleton() {
  return (
    <div className="glass-card rounded-xl p-4 flex flex-col gap-3">
      <div className="flex justify-between items-center">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-10 rounded-full" />
      </div>
      <div className="flex justify-between items-end gap-2 mt-2">
        <Skeleton className="h-8 w-16" />
        <Skeleton className="h-10 w-24" />
      </div>
    </div>
  );
}

export function PanelSkeleton({ rows = 4, hasHeader = true }: { rows?: number; hasHeader?: boolean }) {
  return (
    <div className="glass-card rounded-xl p-4 flex flex-col gap-4">
      {hasHeader && (
        <div className="flex justify-between items-center">
          <div className="flex gap-3 items-center">
            <Skeleton className="h-8 w-8 rounded-md" />
            <div className="flex flex-col gap-1.5">
              <Skeleton className="h-4 w-28" />
              <Skeleton className="h-3 w-36" />
            </div>
          </div>
          <Skeleton className="h-5 w-16" />
        </div>
      )}
      <div className="flex flex-col gap-3 mt-2">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex gap-4 items-center py-2 border-b border-border/30 last:border-0">
            <Skeleton className="h-4 w-full" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function TableSkeleton({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="glass-card rounded-xl p-6 flex flex-col gap-4">
      <div className="flex items-center gap-3 mb-2">
        <Skeleton className="h-8 w-8 rounded-md" />
        <Skeleton className="h-5 w-32" />
      </div>
      <div className="flex flex-col gap-3">
        {/* Header row skeleton */}
        <div className="flex gap-4 pb-3 border-b border-border">
          {Array.from({ length: cols }).map((_, j) => (
            <Skeleton key={j} className="h-4 flex-1" />
          ))}
        </div>
        {/* Data rows skeleton */}
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex gap-4 py-3 border-b border-border/30 last:border-0">
            {Array.from({ length: cols }).map((_, j) => (
              <Skeleton key={j} className="h-4 flex-1" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
