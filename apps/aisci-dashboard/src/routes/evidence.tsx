import { createFileRoute } from "@tanstack/react-router";
import { Fragment, useState } from "react";
import { ChevronDown } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { PageShell } from "@/components/PageShell";
import { evidence, type EvidenceRow } from "@/lib/mock-data";

export const Route = createFileRoute("/evidence")({
  head: () => ({
    meta: [
      { title: "Evidence Ledger — AiSci" },
      {
        name: "description",
        content:
          "Canonical status tracker for scientific claims: supported, sanity checked, proposed, and rejected.",
      },
    ],
  }),
  component: EvidencePage,
});

const statusStyles: Record<EvidenceRow["status"], string> = {
  Supported: "bg-emerald-brand/15 text-emerald-brand ring-1 ring-emerald-brand/40",
  "Sanity Checked": "bg-amber-brand/15 text-amber-brand ring-1 ring-amber-brand/40",
  Proposed: "bg-primary/15 text-primary ring-1 ring-primary/40",
  Rejected: "bg-rose-brand/15 text-rose-brand ring-1 ring-rose-brand/40",
};

function EvidencePage() {
  const [open, setOpen] = useState<number | null>(null);

  const summary = [
    { label: "Supported", value: 3, dot: "🟢", accent: "text-emerald-brand" },
    { label: "Sanity Checked", value: 8, dot: "🟡", accent: "text-amber-brand" },
    { label: "Proposed", value: 2, dot: "🔵", accent: "text-primary" },
  ];

  return (
    <PageShell>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {summary.map((s) => (
          <Card key={s.label} className="glass-card fade-in-up">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                {s.dot} {s.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold tracking-tight ${s.accent}`}>{s.value}</div>
              <div className="text-xs text-muted-foreground">claims</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="glass-card fade-in-up mt-6">
        <CardHeader>
          <CardTitle className="text-base">Ledger</CardTitle>
          <p className="text-xs text-muted-foreground">
            Click any row to expand the full evidence narrative.
          </p>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-transparent">
                <TableHead className="w-6"></TableHead>
                <TableHead>Claim</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Next Gate</TableHead>
                <TableHead>Run</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {evidence.map((row, i) => (
                <Fragment key={i}>
                  <TableRow
                    key={i}
                    onClick={() => setOpen(open === i ? null : i)}
                    className="cursor-pointer border-border transition hover:bg-primary/5"
                  >
                    <TableCell>
                      <ChevronDown
                        className={`h-4 w-4 text-muted-foreground transition-transform ${open === i ? "rotate-180" : ""}`}
                      />
                    </TableCell>
                    <TableCell className="max-w-md">{row.claim}</TableCell>
                    <TableCell>
                      <Badge className={statusStyles[row.status]}>{row.status}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{row.nextGate}</TableCell>
                    <TableCell className="font-mono text-xs text-primary">
                      {row.run !== "—" ? row.run : <span className="text-muted-foreground">—</span>}
                    </TableCell>
                  </TableRow>
                  {open === i && (
                    <TableRow key={`d-${i}`} className="border-border bg-muted/20 hover:bg-muted/20">
                      <TableCell></TableCell>
                      <TableCell colSpan={4}>
                        <div className="py-2 text-sm leading-relaxed text-foreground/90">
                          {row.narrative}
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </Fragment>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </PageShell>
  );
}
