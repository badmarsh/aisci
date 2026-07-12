import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { BookOpen, Link2, Search } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
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
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Tooltip as UITooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { PageShell } from "@/components/PageShell";
import { type Paper } from "@/lib/types";
import { useQuery } from "@tanstack/react-query";
import { fetchLiterature } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

export const Route = createFileRoute("/projects/$projectId/literature")({
  head: () => ({
    meta: [
      { title: "Literature Intake — AiSci" },
      {
        name: "description",
        content:
          "Dual-source paper intake from arXiv and OpenAlex with extracted claims and cross-domain bridge detection.",
      },
    ],
  }),
  component: LiteraturePage,
});

const confidenceStyles = {
  HIGH: "bg-emerald-brand/15 text-emerald-brand ring-1 ring-emerald-brand/40",
  MEDIUM: "bg-amber-brand/15 text-amber-brand ring-1 ring-amber-brand/40",
  LOW: "bg-muted text-muted-foreground ring-1 ring-border",
};

function LiteraturePage() {
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState<Paper | null>(null);

  const {
    data: papers = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["literature"],
    queryFn: fetchLiterature,
  });

  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return papers;
    return papers.filter(
      (p: Paper) =>
        p.title.toLowerCase().includes(needle) ||
        p.category.toLowerCase().includes(needle) ||
        p.source.toLowerCase().includes(needle),
    );
  }, [q, papers]);

  const stats: { label: string; value: number; kind: "icon" | "arxiv" | "openalex" }[] = useMemo(
    () => [
      { label: "Total Papers", value: papers.length, kind: "icon" },
      {
        label: "arXiv Papers",
        value: papers.filter((p: Paper) => p.source === "arXiv").length,
        kind: "arxiv",
      },
      {
        label: "OpenAlex Papers",
        value: papers.filter((p: Paper) => p.source === "OpenAlex").length,
        kind: "openalex",
      },
    ],
    [papers],
  );

  const claimTypeDist = useMemo(() => {
    let hep = 0;
    let bridge = 0;
    papers.forEach((p: Paper) => {
      if (p.bridge) bridge += p.claims;
      else hep += p.claims;
    });
    return [
      { type: "HEP_LITERATURE", count: hep },
      { type: "CS_HEP_BRIDGE", count: bridge },
    ];
  }, [papers]);

  if (isLoading) {
    return (
      <PageShell>
        <div className="space-y-4">
          <Skeleton className="h-[100px] w-full" />
          <Skeleton className="h-[300px] w-full" />
        </div>
      </PageShell>
    );
  }

  if (isError) {
    return (
      <PageShell>
        <div className="text-rose-brand">Error loading literature data.</div>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {stats.map((s) => (
          <Card key={s.label} className="glass-card fade-in-up">
            <CardHeader className="flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                {s.label}
              </CardTitle>
              {s.kind === "icon" ? (
                <BookOpen className="h-4 w-4 text-primary" />
              ) : s.kind === "arxiv" ? (
                <span className="rounded-sm bg-orange-500/15 px-1.5 py-0.5 font-serif text-[11px] font-semibold text-orange-400 ring-1 ring-orange-500/40">
                  arXiv
                </span>
              ) : (
                <span
                  className="grid h-5 w-5 place-items-center rounded-full text-[10px] font-bold text-white"
                  style={{ background: "linear-gradient(135deg,#0ea5b7,#0891b2)" }}
                >
                  OA
                </span>
              )}
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold tracking-tight">{s.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
        <SourceStatus name="arXiv API" rate="10 papers/cycle" polite={false} />
        <SourceStatus name="OpenAlex API" rate="10 papers/cycle" polite={true} />
      </div>

      <Card className="glass-card fade-in-up mt-6">
        <CardHeader className="flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle className="text-base">Ingested Papers</CardTitle>
            <p className="text-xs text-muted-foreground">
              Search across source, category, and title. Click any row for the full record.
            </p>
          </div>
          <div className="relative w-72">
            <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              className="h-8 pl-8 text-sm"
            />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <TooltipProvider delayDuration={200}>
            <Table>
              <TableHeader>
                <TableRow className="border-border hover:bg-transparent">
                  <TableHead>Source</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Published</TableHead>
                  <TableHead className="text-right">Claims</TableHead>
                  <TableHead>Bridge</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((p: Paper, i: number) => (
                  <TableRow
                    key={i}
                    onClick={() => setSelected(p)}
                    className="cursor-pointer border-border transition hover:bg-primary/5"
                  >
                    <TableCell>
                      {p.source === "arXiv" ? (
                        <Badge className="bg-orange-500/15 font-serif text-orange-400 ring-1 ring-orange-500/40 hover:bg-orange-500/15">
                          arXiv
                        </Badge>
                      ) : (
                        <Badge className="bg-teal-500/15 text-teal-300 ring-1 ring-teal-500/40 hover:bg-teal-500/15">
                          OpenAlex
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="border-border text-xs">
                        {p.category}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-[380px]">
                      <UITooltip>
                        <TooltipTrigger asChild>
                          <span className="block truncate text-sm">{p.title}</span>
                        </TooltipTrigger>
                        <TooltipContent side="top" className="max-w-md">
                          {p.title}
                        </TooltipContent>
                      </UITooltip>
                    </TableCell>
                    <TableCell className="font-mono text-xs">{p.published}</TableCell>
                    <TableCell className="text-right">
                      <Badge className="bg-primary/10 text-primary ring-1 ring-primary/30 hover:bg-primary/10">
                        {p.claims}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {p.bridge && (
                        <span title="CS→HEP bridge claim detected">
                          <Link2 className="h-4 w-4 text-primary" />
                        </span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TooltipProvider>
        </CardContent>
      </Card>

      <Card className="glass-card fade-in-up mt-6">
        <CardHeader>
          <CardTitle className="text-base">Claim Type Distribution</CardTitle>
          <p className="text-xs text-muted-foreground">
            Cumulative breakdown of extracted claim classes.
          </p>
        </CardHeader>
        <CardContent>
          <div className="h-[200px]">
            <ResponsiveContainer>
              <BarChart data={claimTypeDist} layout="vertical" margin={{ left: 40, right: 20 }}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                <XAxis type="number" tick={{ fill: "var(--muted-foreground)", fontSize: 11 }} />
                <YAxis
                  type="category"
                  dataKey="type"
                  tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  width={140}
                />
                <Tooltip
                  contentStyle={{
                    background: "var(--popover)",
                    border: "1px solid var(--border)",
                    fontSize: 12,
                  }}
                />
                <Bar dataKey="count" fill="var(--primary)" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Sheet open={!!selected} onOpenChange={(o) => !o && setSelected(null)}>
        <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
          {selected && (
            <>
              <SheetHeader>
                <SheetTitle className="pr-4 text-base leading-snug">{selected.title}</SheetTitle>
                <SheetDescription>
                  {selected.source} · {selected.category} · {selected.published}
                </SheetDescription>
              </SheetHeader>
              <div className="mt-4 space-y-5 px-1 text-sm">
                <p className="leading-relaxed text-foreground/90">{selected.abstract}</p>
                <section>
                  <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Extracted Claims
                  </h3>
                  <ul className="space-y-2">
                    {selected.claimList.map((c, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 rounded-md border border-border bg-muted/30 p-2"
                      >
                        <Badge className={confidenceStyles[c.confidence]}>{c.confidence}</Badge>
                        <span className="flex-1">{c.text}</span>
                      </li>
                    ))}
                  </ul>
                </section>
                <a
                  href={selected.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-primary hover:underline"
                >
                  <Link2 className="h-3.5 w-3.5" /> Open source
                </a>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </PageShell>
  );
}

function SourceStatus({ name, rate, polite }: { name: string; rate: string; polite: boolean }) {
  return (
    <div className="glass-card flex items-center gap-3 rounded-lg px-4 py-3">
      <span className="relative flex h-2.5 w-2.5">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-brand opacity-60" />
        <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-brand" />
      </span>
      <div className="flex-1">
        <div className="text-sm font-semibold">{name}</div>
        <div className="text-xs text-muted-foreground">
          Operational · Last sync: 18:03 today · Rate: {rate}
          {polite && " · Polite pool: ✓"}
        </div>
      </div>
    </div>
  );
}
