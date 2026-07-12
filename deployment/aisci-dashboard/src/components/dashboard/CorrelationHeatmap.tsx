import { useMemo } from "react";
import { cn } from "@/lib/utils";

interface CorrelationHeatmapProps {
  correlations: Record<string, number>;
}

export function CorrelationHeatmap({ correlations }: CorrelationHeatmapProps) {
  // Extract unique parameters from keys like "paramA|paramB"
  const parameters = useMemo(() => {
    const paramsSet = new Set<string>();
    Object.keys(correlations).forEach((key) => {
      const parts = key.split("|");
      if (parts.length === 2) {
        paramsSet.add(parts[0]);
        paramsSet.add(parts[1]);
      }
    });
    return Array.from(paramsSet).sort();
  }, [correlations]);

  const getCorrelationValue = (p1: string, p2: string): number => {
    if (p1 === p2) return 1.0;
    const key1 = `${p1}|${p2}`;
    const key2 = `${p2}|${p1}`;
    if (correlations[key1] !== undefined) return correlations[key1];
    if (correlations[key2] !== undefined) return correlations[key2];
    return 0.0;
  };

  const getColorClass = (val: number) => {
    const absVal = Math.abs(val);
    if (absVal >= 0.85) {
      return "bg-rose-brand/20 text-rose-brand border border-rose-brand/35 font-semibold";
    }
    if (absVal >= 0.6) {
      return "bg-amber-brand/15 text-amber-brand border border-amber-brand/30";
    }
    if (absVal >= 0.3) {
      return "bg-cyan-brand/10 text-cyan-brand border border-cyan-brand/25";
    }
    return "bg-secondary/40 text-muted-foreground border border-border/20";
  };

  if (parameters.length === 0) {
    return (
      <div className="py-6 text-center text-sm text-muted-foreground">
        No correlation parameter data available for this fit.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto p-4 bg-background/40 border border-border/50 rounded-lg">
      <table className="min-w-full text-xs text-left border-collapse">
        <thead>
          <tr>
            <th className="p-2 border-b border-border/50 text-muted-foreground font-medium">Parameter</th>
            {parameters.map((p) => (
              <th key={p} className="p-2 border-b border-border/50 text-center font-mono text-[10px] select-none text-muted-foreground whitespace-nowrap">
                {p}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {parameters.map((p1) => (
            <tr key={p1} className="hover:bg-muted/10 transition-colors">
              <td className="p-2 border-b border-border/30 font-medium font-mono text-[11px] text-foreground">
                {p1}
              </td>
              {parameters.map((p2) => {
                const val = getCorrelationValue(p1, p2);
                return (
                  <td
                    key={p2}
                    className={cn(
                      "p-3 border border-border/30 text-center font-mono text-[11px] min-w-[70px]",
                      getColorClass(val)
                    )}
                    title={`ρ(${p1}, ${p2}) = ${val}`}
                  >
                    {val === 1.0 ? "1.00" : val.toFixed(3)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex gap-4 mt-3 text-[10px] text-muted-foreground justify-end px-2">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded bg-rose-brand/20 border border-rose-brand/40" />
          Critical (&gt;= 0.85)
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded bg-amber-brand/15 border border-amber-brand/35" />
          High (&gt;= 0.60)
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded bg-cyan-brand/10 border border-cyan-brand/30" />
          Moderate (&gt;= 0.30)
        </span>
      </div>
    </div>
  );
}
