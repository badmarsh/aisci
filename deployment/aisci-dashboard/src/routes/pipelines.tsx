import { createFileRoute } from "@tanstack/react-router";
import { PageShell } from "@/components/PageShell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Network, Activity, Clock, ShieldCheck, FileText, Play } from "lucide-react";

export const Route = createFileRoute("/pipelines")({
  head: () => ({
    meta: [
      { title: "Pipeline Catalog — AiSci" },
    ],
  }),
  component: PipelineStudio,
});

const PIPELINES = [
  {
    id: "fit-validation",
    name: "Fit Validation & χ² Replication",
    description: "Re-run physics-core models (Tsallis, Blast-Wave) on extracted data and report metrics.",
    input: "Paper/Project",
    category: "Physics Diagnostics",
    health: "Healthy",
    runtime: "~45s",
    icon: Activity
  },
  {
    id: "ingest-validation",
    name: "Literature Crawl & Extract",
    description: "Crawl arXiv/OpenAlex, extract LaTeX equations, and parse tables into datasets.",
    input: "Paper URL/ID",
    category: "Ingest",
    health: "Healthy",
    runtime: "~2m",
    icon: FileText
  },
  {
    id: "tsallis-diagnostics",
    name: "Thermodynamic Inconsistency Check",
    description: "Check for q-parameter vs Temperature degeneracy and thermodynamic inconsistency.",
    input: "Paper",
    category: "Physics Diagnostics",
    health: "Degraded",
    runtime: "~30s",
    icon: ShieldCheck
  },
  {
    id: "paper-critique",
    name: "Adversarial Reviewer Critique",
    description: "Cross-reference manuscript claims against the evidence ledger using LLMs.",
    input: "Paper",
    category: "Text/Structure Critique",
    health: "Healthy",
    runtime: "~1m",
    icon: Network
  }
];

function PipelineStudio() {
  return (
    <PageShell>
      <div className="mb-8">
        <h2 className="text-3xl font-bold tracking-tight">Pipeline Catalog</h2>
        <p className="text-muted-foreground mt-2 max-w-2xl text-sm leading-6">
          Discover and execute state-of-the-art computer science pipelines against manuscripts or entire projects.
        </p>
      </div>

      <Card className="border-border shadow-sm">
        <CardHeader className="bg-muted/10 pb-4 border-b">
          <CardTitle className="text-xl flex items-center gap-2">
            <Network className="w-5 h-5 text-primary" />
            Available Algorithms
          </CardTitle>
          <CardDescription>
            These pipelines run in the background (FastAPI + local-deep-research workers).
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="pl-6">Pipeline</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Input Type</TableHead>
                <TableHead>Avg Runtime</TableHead>
                <TableHead>Health</TableHead>
                <TableHead className="text-right pr-6">Triggers</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {PIPELINES.map((pipe) => {
                const Icon = pipe.icon;
                return (
                  <TableRow key={pipe.id} className="hover:bg-muted/5 transition">
                    <TableCell className="pl-6 py-4">
                      <div className="flex items-start gap-3">
                        <div className="p-2 rounded-md bg-secondary shrink-0">
                          <Icon className="w-4 h-4 text-primary" />
                        </div>
                        <div>
                          <div className="font-medium">{pipe.name}</div>
                          <div className="text-xs text-muted-foreground mt-1">{pipe.description}</div>
                          <div className="text-[10px] font-mono text-muted-foreground mt-1">ID: {pipe.id}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-[10px]">{pipe.category}</Badge>
                    </TableCell>
                    <TableCell className="text-xs font-mono text-muted-foreground">{pipe.input}</TableCell>
                    <TableCell className="text-xs flex items-center gap-1.5 mt-4">
                      <Clock className="w-3 h-3" /> {pipe.runtime}
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary" className={pipe.health === "Healthy" ? "text-emerald-500 bg-emerald-500/10" : "text-amber-500 bg-amber-500/10"}>
                        {pipe.health}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right pr-6 space-y-2">
                      <Button size="sm" variant="outline" className="w-full justify-start text-xs h-8">
                        <Play className="w-3 h-3 mr-2" /> Run on Project...
                      </Button>
                      <Button size="sm" variant="default" className="w-full justify-start text-xs h-8">
                        <Play className="w-3 h-3 mr-2" /> Run on Paper...
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </PageShell>
  );
}
