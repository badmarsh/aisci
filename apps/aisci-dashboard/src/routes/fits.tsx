import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
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
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { PageShell } from "@/components/PageShell";
import { fitRows, type FitRow } from "@/lib/mock-data";

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

  const rows = useMemo(
    () => (filter === "All Models" ? fitRows : fitRows.filter((r) => r.model === filter)),
    [filter],
  );

  return (
    <PageShell>
      <div className="mb-4 flex flex-wrap gap-2">
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
                      {r.quality === "POOR" ? "🔴" : r.quality === "MARGINAL" ? "🟡" : "🟢"} {r.quality}
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

      <div className="mt-4 space-y-3">
        <Alert className="glass-card border-amber-brand/40">
          <AlertTriangle className="h-4 w-4 text-amber-brand" />
          <AlertTitle>High parameter correlation detected</AlertTitle>
          <AlertDescription>
            Bin 61-70, Jüttner 1c: ρ(T, β) = 0.97. See next-actions.md.
          </AlertDescription>
        </Alert>
        <Alert className="glass-card border-rose-brand/40">
          <AlertTriangle className="h-4 w-4 text-rose-brand" />
          <AlertTitle>χ²/ndf &gt; 200 in 4 bins</AlertTitle>
          <AlertDescription>
            Jüttner model fails Boltzmann approximation threshold. Consider Bose-Einstein correction.
          </AlertDescription>
        </Alert>
      </div>

      <FitDetailSheet row={selected} onClose={() => setSelected(null)} />
    </PageShell>
  );
}

function FitDetailSheet({ row, onClose }: { row: FitRow | null; onClose: () => void }) {
  const boundaryHit = row?.beta.startsWith("0.99");
  // Toy 2x2 covariance heatmap values
  const cov = [
    [1.0, row?.model === "Jüttner 1c" ? 0.97 : 0.31],
    [row?.model === "Jüttner 1c" ? 0.97 : 0.31, 1.0],
  ];

  const residuals = Array.from({ length: 12 }, (_, i) => ({
    x: i,
    r: Math.sin(i * 0.7) * (row?.quality === "POOR" ? 3.2 : 0.6) + (Math.random() - 0.5) * 0.3,
  }));

  return (
    <Sheet open={!!row} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
        {row && (
          <>
            <SheetHeader>
              <SheetTitle>
                {row.model} · bin {row.bin}
              </SheetTitle>
              <SheetDescription>
                Full fit provenance and diagnostics.
              </SheetDescription>
            </SheetHeader>

            <div className="mt-6 space-y-6 px-1">
              {boundaryHit && (
                <Alert className="border-amber-brand/40 bg-amber-brand/10">
                  <AlertTriangle className="h-4 w-4 text-amber-brand" />
                  <AlertTitle>Parameter at boundary</AlertTitle>
                  <AlertDescription>
                    β = {row.beta} — speed-of-light bound (β &lt; 1) is being hit. Refit with tighter prior.
                  </AlertDescription>
                </Alert>
              )}

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
                <div className="grid w-fit grid-cols-2 gap-1">
                  {cov.flat().map((v, i) => {
                    const bg =
                      v > 0
                        ? `rgba(220, 38, 38, ${Math.abs(v)})`
                        : `rgba(37, 99, 235, ${Math.abs(v)})`;
                    return (
                      <div
                        key={i}
                        className="flex h-14 w-14 items-center justify-center rounded-md border border-border text-xs font-mono"
                        style={{ background: bg, color: Math.abs(v) > 0.6 ? "white" : "inherit" }}
                      >
                        {v.toFixed(2)}
                      </div>
                    );
                  })}
                </div>
                <div className="mt-1 flex gap-2 text-[10px] text-muted-foreground">
                  <span>rows/cols: T, β</span>
                </div>
              </section>

              <section>
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Residuals
                </h3>
                <div className="h-[160px] rounded-md border border-border bg-muted/20 p-2">
                  <ResponsiveContainer>
                    <AreaChart data={residuals}>
                      <defs>
                        <linearGradient id="res" x1="0" x2="0" y1="0" y2="1">
                          <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.5} />
                          <stop offset="100%" stopColor="var(--primary)" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                      <XAxis dataKey="x" hide />
                      <YAxis tick={{ fill: "var(--muted-foreground)", fontSize: 10 }} />
                      <Tooltip
                        contentStyle={{
                          background: "var(--popover)",
                          border: "1px solid var(--border)",
                          fontSize: 11,
                        }}
                      />
                      <Area dataKey="r" stroke="var(--primary)" fill="url(#res)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </section>

              <section className="rounded-md border border-border bg-muted/20 p-3 text-xs">
                <h3 className="mb-2 font-semibold uppercase tracking-wider text-muted-foreground">
                  Provenance
                </h3>
                <dl className="grid grid-cols-[110px_1fr] gap-y-1 font-mono">
                  <dt className="text-muted-foreground">Run ID</dt>
                  <dd>2026-07-09-jacobian-fix</dd>
                  <dt className="text-muted-foreground">Timestamp</dt>
                  <dd>2026-07-09 17:58:23 UTC</dd>
                  <dt className="text-muted-foreground">Seed</dt>
                  <dd>0x8f21c4</dd>
                </dl>
              </section>
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
