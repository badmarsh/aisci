import { createFileRoute } from "@tanstack/react-router";
import { Fragment, useState } from "react";
import { toast } from "sonner";
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
import { type EvidenceRow } from "@/lib/types";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import DOMPurify from "dompurify";
import { fetchEvidence, updateEvidence, syncFromFiles, fetchProjects } from "@/lib/api";
import { redirect } from "@tanstack/react-router";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/projects/$projectId/evidence")({
  beforeLoad: async ({ params }) => {
    const projects = await fetchProjects();
    const p = projects.find((p) => p.id === params.projectId);
    if (!p || !p.capabilities.includes("evidence")) {
      throw redirect({ to: `/projects/${params.projectId}` as any });
    }
  },
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

const statusStyles: Record<string, string> = {
  Supported: "bg-emerald-brand/15 text-emerald-brand ring-1 ring-emerald-brand/40",
  "Sanity checked": "bg-amber-brand/15 text-amber-brand ring-1 ring-amber-brand/40",
  Proposed: "bg-primary/15 text-primary ring-1 ring-primary/40",
  "Rejected (Bulletproof)": "bg-rose-brand/15 text-rose-brand ring-1 ring-rose-brand/40",
};

function EvidencePage() {
  const { projectId } = Route.useParams();
  const [open, setOpen] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const {
    data: evidence = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["evidence", projectId],
    queryFn: () => fetchEvidence(projectId),
  });

  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      updateEvidence(projectId, id, status),
    onSuccess: (_, { status }) => {
      queryClient.invalidateQueries({ queryKey: ["evidence", projectId] });
      queryClient.invalidateQueries({ queryKey: ["activity", projectId] });
      toast.success(`Evidence marked as ${status}`, {
        description: "evidence-ledger.md updated.",
      });
    },
    onError: () => {
      toast.error("Failed to update evidence status.");
    },
  });

  const syncMutation = useMutation({
    mutationFn: () => syncFromFiles(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence", projectId] });
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
    },
  });

  const summary = [
    {
      label: "Supported",
      value: evidence.filter((e: EvidenceRow) => e.status === "Supported").length,
      dot: "🟢",
      accent: "text-emerald-brand",
    },
    {
      label: "Sanity Checked",
      value: evidence.filter((e: EvidenceRow) => e.status === "Sanity Checked").length,
      dot: "🟡",
      accent: "text-amber-brand",
    },
    {
      label: "Proposed",
      value: evidence.filter((e: EvidenceRow) => e.status === "Proposed").length,
      dot: "🔵",
      accent: "text-primary",
    },
  ];

  if (isLoading) {
    return (
      <PageShell>
        <Skeleton className="h-[200px] w-full" />
      </PageShell>
    );
  }

  if (isError) {
    return (
      <PageShell>
        <div className="text-rose-brand">Error loading evidence ledger.</div>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <div className="mb-4 flex items-center justify-end">
        <Button
          variant="outline"
          size="sm"
          disabled={syncMutation.isPending}
          onClick={() => syncMutation.mutate()}
        >
          Sync from Files
        </Button>
      </div>
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
              {evidence.map((row: EvidenceRow, i: number) => (
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
                    <TableCell className="max-w-md">
                      <div
                        dangerouslySetInnerHTML={{
                          __html: DOMPurify.sanitize(
                            row.claim
                              .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                              .replace(/<br>/g, "<br/>"),
                          ),
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Badge className={statusStyles[row.status]}>{row.status}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{row.nextGate}</TableCell>
                    <TableCell className="font-mono text-xs text-primary">
                      {row.run !== "—" ? row.run : <span className="text-muted-foreground">—</span>}
                    </TableCell>
                  </TableRow>
                  {open === i && (
                    <TableRow
                      key={`d-${i}`}
                      className="border-border bg-muted/20 hover:bg-muted/20"
                    >
                      <TableCell></TableCell>
                      <TableCell colSpan={4}>
                        <div className="py-2 text-sm leading-relaxed text-foreground/90">
                          {row.narrative}
                          <div className="mt-3 flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              disabled={mutation.isPending}
                              onClick={() => mutation.mutate({ id: row.id, status: "Supported" })}
                            >
                              Approve
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-rose-brand"
                              disabled={mutation.isPending}
                              onClick={() => mutation.mutate({ id: row.id, status: "Rejected" })}
                            >
                              Reject
                            </Button>
                          </div>
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
