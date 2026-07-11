import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { AlertTriangle } from "lucide-react";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  Legend,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { PageShell } from "@/components/PageShell";
import { type FitRow } from "@/lib/types";
import { useQuery } from "@tanstack/react-query";
import { fetchFits, fetchFitRuns } from "@/lib/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";

export const Route = createFileRoute("/fits")({
  head: () => ({
    meta: [
      { title: "Physics Fits — AiSci" },
      {
        name: "description",
        content:
          "Fitting pipeline results across multiplicity bins for Jüttner, Tsallis, and Bose-Einstein models.",
      },
    ],
  }),
  component: FitsPage,
});

const filters = ["All Models", "Jüttner 1c", "Tsallis 2c", "Bose-Einstein 1c"] as const;
type Filter = (typeof filters)[number];

const qualityStyles: Record<FitRow["quality"], string> = {
  POOR: "bg-rose-brand/15 text-rose-brand ring-1 ring-rose-brand/40",
  MARGINAL: "bg-amber-brand/15 text-amber-brand ring-1 ring-amber-brand/40",
  GOOD: "bg-emerald-brand/15 text-emerald-brand ring-1 ring-emerald-brand/40",
};

const filterStyles: Record<Filter, string> = {
  "All Models": "data-[on=true]:bg-primary data-[on=true]:text-primary-foreground",
  "Jüttner 1c": "data-[on=true]:bg-rose-brand data-[on=true]:text-white",
  "Tsallis 2c": "data-[on=true]:bg-emerald-brand data-[on=true]:text-black",
  "Bose-Einstein 1c": "data-[on=true]:bg-primary data-[on=true]:text-primary-foreground",
};

function FitsPage() {
  const [filter, setFilter] = useState<Filter>("All Models");
  const [selected, setSelected] = useState<FitRow | null>(null);

  const { data: runsData } = useQuery({
    queryKey: ["fitRuns"],
    queryFn: fetchFitRuns,
  });
  const runs = runsData?.runs || [];

  const [selectedRun, setSelectedRun] = useState<string | undefined>();
  const activeRun = selectedRun || (runs.length > 0 ? runs[0] : undefined);
  const [compareRun, setCompareRun] = useState<string | undefined>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["fits", activeRun, compareRun],
    queryFn: () => fetchFits(activeRun, compareRun === "none" ? undefined : compareRun),
    enabled: !!activeRun,
  });

  const rows = useMemo(() => {
    const fitRows: FitRow[] = data?.fitRows || [];
    return filter === "All Models" ? fitRows : fitRows.filter((r: FitRow) => r.model === filter);
  }, [filter, data?.fitRows]);

  const tSeriesData = useMemo(() => {
    if (!data?.fitRows || !data?.bins) return [];
    return data.bins.map((bin: string) => {
      const entry: Record<string, any> = { bin };
      filters
        .filter((f) => f !== "All Models")
        .forEach((model) => {
          const row = data.fitRows.find((r: FitRow) => r.bin === bin && r.model === model);
          entry[model] = row ? parseFloat(row.T) : null;
        });
      return entry;
    });
  }, [data]);

  // Derive alerts directly from the live data already fetched
  const dataAlerts = useMemo(() => {
    if (!data?.fitRows) return { corrAlerts: [], chi2Alerts: [] };

    const corrAlerts: { bin: string; model: string; pair: string; rho: number }[] = [];
    const chi2Alerts: { bin: string; model: string; chi2: number }[] = [];

    for (const row of data.fitRows as FitRow[]) {
      // Chi2 alert
      if (row.chi2 > 10) {
        chi2Alerts.push({ bin: row.bin, model: row.model, chi2: row.chi2 });
      }
      // Correlation alert — check off-diagonal pairs
      for (const [key, val] of Object.entries(row.correlations || {})) {
        const [p1, p2] = key.split("|");
        if (p1 !== p2 && Math.abs(val) > 0.9) {
          corrAlerts.push({ bin: row.bin, model: row.model, pair: `${p1}, ${p2}`, rho: val });
        }
      }
    }
    return { corrAlerts, chi2Alerts };
  }, [data]);

  if (isLoading) {
    return (
      <PageShell>
        <div className="space-y-4">
          <Skeleton className="h-8 w-[300px]" />
          <Skeleton className="h-[400px] w-full" />
        </div>
      </PageShell>
    );
  }

  if (isError) {
    return (
      <PageShell>
        <Alert variant="destructive">
          <AlertTitle>Error loading fits</AlertTitle>
          <AlertDescription>Failed to load physics fits from backend.</AlertDescription>
        </Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <div className="mb-4 flex flex-wrap gap-4 items-center">
        {runs.length > 0 && (
          <Select value={activeRun} onValueChange={(val) => setSelectedRun(val)}>
            <SelectTrigger className="w-[280px] font-mono text-xs">
              <SelectValue placeholder="Select run..." />
            </SelectTrigger>
            <SelectContent>
              {runs.map((r: string) => (
                <SelectItem key={r} value={r} className="font-mono text-xs">
                  {r}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
        {runs.length > 1 && (
          <Select value={compareRun || "none"} onValueChange={(val) => setCompareRun(val)}>
            <SelectTrigger className="w-[280px] font-mono text-xs">
              <SelectValue placeholder="Compare with..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none" className="font-mono text-xs">
                None
              </SelectItem>
              {runs.map((r: string) => (
                <SelectItem key={r} value={r} className="font-mono text-xs">
                  {r}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
        <div className="flex flex-wrap gap-2">
          {filters.map((f) => (
            <Button
              key={f}
              variant="outline"
              size="sm"
              data-on={filter === f}
              className={`rounded-full border-border transition ${filterStyles[f]}`}
              onClick={() => setFilter(f)}
            >
              {f}
            </Button>
          ))}
        </div>
      </div>

      {data?.status === "Incomplete" ? (
        <Card className="glass-card fade-in-up border-red-500/20 bg-red-500/5 mt-4">
          <CardHeader>
            <CardTitle className="text-red-400 flex items-center gap-2 text-base">
              <AlertTriangle className="w-5 h-5" />
              Run Incomplete or Failed
            </CardTitle>
            <p className="text-sm text-red-400/80">{data.error || "Missing fit quality data"}</p>
          </CardHeader>
        </Card>
      ) : (
        <>
          <Card className="glass-card fade-in-up">
            <CardHeader>
              <CardTitle className="text-base">Fit Results</CardTitle>
              <p className="text-xs text-muted-foreground">
                Click any row to inspect the covariance matrix, residuals, and provenance.
              </p>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead>Multiplicity Bin</TableHead>
                    <TableHead>Model</TableHead>
                    <TableHead className="text-right">χ²/ndf</TableHead>
                    <TableHead>Quality</TableHead>
                    <TableHead>T (GeV)</TableHead>
                    <TableHead>β/U</TableHead>
                    <TableHead className="text-right">AIC</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rows.map((r, i) => (
                    <TableRow
                      key={`${r.bin}-${r.model}-${i}`}
                      onClick={() => setSelected(r)}
                      className="cursor-pointer border-border transition hover:bg-primary/5"
                    >
                      <TableCell className="font-mono text-xs">{r.bin}</TableCell>
                      <TableCell>{r.model}</TableCell>
                      <TableCell className="text-right font-mono">{r.chi2.toFixed(2)}</TableCell>
                      <TableCell>
                        <Badge className={qualityStyles[r.quality]}>
                          {r.quality === "POOR" ? "🔴" : r.quality === "MARGINAL" ? "🟡" : "🟢"}{" "}
                          {r.quality}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{r.T}</TableCell>
                      <TableCell className="font-mono text-xs">{r.beta}</TableCell>
                      <TableCell className="text-right font-mono">{r.aic.toFixed(1)}</TableCell>
                      <TableCell>
                        <span className="text-xs text-muted-foreground">{r.status}</span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Card className="glass-card fade-in-up delay-75">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Temperature Evolution (T)</CardTitle>
              </CardHeader>
              <CardContent className="h-[250px] w-full p-2 pl-0">
                <ResponsiveContainer>
                  <LineChart
                    data={tSeriesData}
                    margin={{ left: -20, right: 10, top: 10, bottom: 0 }}
                  >
                    <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                    <XAxis dataKey="bin" tick={{ fill: "var(--muted-foreground)", fontSize: 10 }} />
                    <YAxis
                      tick={{ fill: "var(--muted-foreground)", fontSize: 10 }}
                      domain={["auto", "auto"]}
                    />
                    <Tooltip
                      contentStyle={{
                        background: "var(--popover)",
                        border: "1px solid var(--border)",
                        fontSize: 11,
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: 11, paddingTop: "10px" }} />
                    <Line
                      type="monotone"
                      dataKey="Jüttner 1c"
                      stroke="var(--rose-brand)"
                      strokeWidth={2}
                      dot={{ r: 3 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="Tsallis 2c"
                      stroke="var(--emerald-brand)"
                      strokeWidth={2}
                      dot={{ r: 3 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="Bose-Einstein 1c"
                      stroke="var(--primary)"
                      strokeWidth={2}
                      dot={{ r: 3 }}
                    />
                    {data?.compareSeries && (
                      <>
                        <Line
                          type="monotone"
                          dataKey="Jüttner 1c (cmp)"
                          stroke="var(--rose-brand)"
                          strokeWidth={1.5}
                          strokeDasharray="4 2"
                          dot={false}
                          data={data.compareSeries}
                        />
                        <Line
                          type="monotone"
                          dataKey="Tsallis 2c (cmp)"
                          stroke="var(--emerald-brand)"
                          strokeWidth={1.5}
                          strokeDasharray="4 2"
                          dot={false}
                          data={data.compareSeries}
                        />
                        <Line
                          type="monotone"
                          dataKey="Bose-Einstein 1c (cmp)"
                          stroke="var(--primary)"
                          strokeWidth={1.5}
                          strokeDasharray="4 2"
                          dot={false}
                          data={data.compareSeries}
                        />
                      </>
                    )}
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <div className="mt-4 space-y-3">
            {dataAlerts.corrAlerts.length > 0 && (
              <Alert className="glass-card border-amber-brand/40">
                <AlertTriangle className="h-4 w-4 text-amber-brand" />
                <AlertTitle>
                  {dataAlerts.corrAlerts.length} high-correlation pair
                  {dataAlerts.corrAlerts.length > 1 ? "s" : ""} detected
                </AlertTitle>
                <AlertDescription className="mt-1 space-y-0.5 text-xs font-mono">
                  {dataAlerts.corrAlerts.slice(0, 5).map((a, i) => (
                    <div key={i}>
                      Bin {a.bin} · {a.model}: ρ({a.pair}) = {a.rho.toFixed(3)}
                    </div>
                  ))}
                  {dataAlerts.corrAlerts.length > 5 && (
                    <div className="text-muted-foreground">
                      …and {dataAlerts.corrAlerts.length - 5} more
                    </div>
                  )}
                </AlertDescription>
              </Alert>
            )}
            {dataAlerts.chi2Alerts.length > 0 && (
              <Alert className="glass-card border-rose-brand/40">
                <AlertTriangle className="h-4 w-4 text-rose-brand" />
                <AlertTitle>
                  {dataAlerts.chi2Alerts.length} fit{dataAlerts.chi2Alerts.length > 1 ? "s" : ""}{" "}
                  exceed χ²/ndf = 10
                </AlertTitle>
                <AlertDescription className="mt-1 space-y-0.5 text-xs font-mono">
                  {dataAlerts.chi2Alerts.slice(0, 5).map((a, i) => (
                    <div key={i}>
                      Bin {a.bin} · {a.model}: χ²/ndf = {a.chi2.toFixed(0)}
                    </div>
                  ))}
                  {dataAlerts.chi2Alerts.length > 5 && (
                    <div className="text-muted-foreground">
                      …and {dataAlerts.chi2Alerts.length - 5} more
                    </div>
                  )}
                </AlertDescription>
              </Alert>
            )}
          </div>
        </>
      )}

      <FitDetailSheet row={selected} runId={data?.runId} onClose={() => setSelected(null)} />
    </PageShell>
  );
}

function FitDetailSheet({
  row,
  runId,
  onClose,
}: {
  row: FitRow | null;
  runId?: string;
  onClose: () => void;
}) {
  const boundaryHit = row?.beta.startsWith("0.99") || parseFloat(row?.beta || "0") > 2.99;

  const params = useMemo(() => {
    if (!row?.correlations) return [];
    return [...new Set(Object.keys(row.correlations).flatMap((k) => k.split("|")))].sort();
  }, [row?.correlations]);

  const covMatrix = useMemo(() => {
    if (!row?.correlations) return [];
    return params.map((p1) =>
      params.map(
        (p2) =>
          row.correlations[`${p1}|${p2}`] ??
          row.correlations[`${p2}|${p1}`] ??
          (p1 === p2 ? 1.0 : 0),
      ),
    );
  }, [params, row?.correlations]);

  const highCorrelations = useMemo(() => {
    if (!row?.correlations) return [];
    return Object.entries(row.correlations).filter(([k, v]) => {
      const [p1, p2] = k.split("|");
      return p1 !== p2 && Math.abs(v) > 0.9;
    });
  }, [row?.correlations]);

  return (
    <Sheet open={!!row} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
        {row && (
          <>
            <SheetHeader>
              <SheetTitle>
                {row.model} · bin {row.bin}
              </SheetTitle>
              <SheetDescription>Full fit provenance and diagnostics.</SheetDescription>
            </SheetHeader>

            <div className="mt-6 space-y-6 px-1">
              <div className="space-y-3">
                {boundaryHit && (
                  <Alert className="border-amber-brand/40 bg-amber-brand/10">
                    <AlertTriangle className="h-4 w-4 text-amber-brand" />
                    <AlertTitle>Parameter at boundary</AlertTitle>
                    <AlertDescription>
                      U_1 = {row.beta} — bound is being hit. Refit with tighter prior.
                    </AlertDescription>
                  </Alert>
                )}
                {highCorrelations.map(([k, v]) => (
                  <Alert key={k} className="border-amber-brand/40 bg-amber-brand/10">
                    <AlertTriangle className="h-4 w-4 text-amber-brand" />
                    <AlertTitle>High correlation</AlertTitle>
                    <AlertDescription>
                      ρ({k.replace("|", ", ")}) = {v.toFixed(3)}
                    </AlertDescription>
                  </Alert>
                ))}
                {!boundaryHit && highCorrelations.length === 0 && (
                  <Alert className="border-emerald-brand/40 bg-emerald-brand/10">
                    <AlertTitle className="text-emerald-brand flex items-center gap-2">
                      <span className="text-sm">🟢</span> Clean Fit
                    </AlertTitle>
                    <AlertDescription className="text-emerald-brand/80">
                      No parameter boundaries hit and no unphysical correlations detected.
                    </AlertDescription>
                  </Alert>
                )}
              </div>

              <section>
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Parameters
                </h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="rounded-md border border-border bg-muted/30 p-2">
                    <div className="text-[10px] uppercase text-muted-foreground">T (GeV)</div>
                    <div className="font-mono">{row.T}</div>
                  </div>
                  <div className="rounded-md border border-border bg-muted/30 p-2">
                    <div className="text-[10px] uppercase text-muted-foreground">β / U</div>
                    <div className="font-mono">{row.beta}</div>
                  </div>
                  <div className="rounded-md border border-border bg-muted/30 p-2">
                    <div className="text-[10px] uppercase text-muted-foreground">χ²/ndf</div>
                    <div className="font-mono">{row.chi2.toFixed(3)}</div>
                  </div>
                  <div className="rounded-md border border-border bg-muted/30 p-2">
                    <div className="text-[10px] uppercase text-muted-foreground">AIC</div>
                    <div className="font-mono">{row.aic.toFixed(1)}</div>
                  </div>
                </div>
              </section>

              <section>
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Covariance Heatmap
                </h3>
                <div
                  className="grid w-fit gap-1"
                  style={{ gridTemplateColumns: `repeat(${params.length}, minmax(0, 1fr))` }}
                >
                  {covMatrix.flat().map((v, i) => {
                    const bg =
                      v > 0
                        ? `rgba(220, 38, 38, ${Math.abs(v)})`
                        : `rgba(37, 99, 235, ${Math.abs(v)})`;
                    const isHigh =
                      Math.abs(v) > 0.9 && i % params.length !== Math.floor(i / params.length);
                    return (
                      <div
                        key={i}
                        className={`flex h-14 w-14 items-center justify-center rounded-md border border-border text-xs font-mono transition-all ${isHigh ? "ring-2 ring-amber-brand ring-offset-1 animate-pulse" : ""}`}
                        style={{ background: bg, color: Math.abs(v) > 0.6 ? "white" : "inherit" }}
                        title={`ρ = ${v}`}
                      >
                        {v.toFixed(2)}
                      </div>
                    );
                  })}
                </div>
                <div className="mt-1 flex gap-2 text-[10px] text-muted-foreground">
                  <span>rows/cols: {params.join(", ")}</span>
                </div>
              </section>

              <section>
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Residuals
                </h3>
                <div className="rounded-md border border-border bg-muted/20 p-4 text-sm text-muted-foreground text-center italic">
                  Residual plots require per-point fit data. Re-run fits with{" "}
                  <code>--save-residuals</code> flag to enable this panel.
                </div>
              </section>

              <section className="rounded-md border border-border bg-muted/20 p-3 text-xs">
                <h3 className="mb-2 font-semibold uppercase tracking-wider text-muted-foreground">
                  Provenance
                </h3>
                <dl className="grid grid-cols-[110px_1fr] gap-y-1 font-mono">
                  <dt className="text-muted-foreground">Run ID</dt>
                  <dd>{runId || "—"}</dd>
                  <dt className="text-muted-foreground">Timestamp</dt>
                  <dd>{row.runTimestamp || "—"}</dd>
                  <dt className="text-muted-foreground">Seed</dt>
                  <dd>{row.seedIndex != null ? `#${row.seedIndex}` : "—"}</dd>
                </dl>
              </section>
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
