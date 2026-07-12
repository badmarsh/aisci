import { createFileRoute, useParams, Link } from "@tanstack/react-router";
import { PageShell } from "@/components/PageShell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import { CheckCircle2, AlertTriangle, FileText, Activity, ShieldCheck, ListTodo, XCircle, Play, Database, FileCode2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export const Route = createFileRoute("/papers/$paperId")({
  head: ({ params }) => ({
    meta: [
      { title: `Paper ${params.paperId} — AiSci Studio` },
    ],
  }),
  component: PaperStudio,
});

// Mocked paper details
const MOCK_PAPER = {
  id: "arxiv-2401-0001",
  title: "Deep Learning Analysis of Heavy-Ion Collisions using Tsallis Statistics",
  authors: "J. Smith et al.",
  category: "hep-ph",
  abstract: "We present a deep learning approach to analyze heavy-ion collisions, extracting thermodynamic parameters using Tsallis statistics. We show that the system reaches an early freeze-out.",
  published: "2024-01-15",
  content: "1. Introduction\nHeavy-ion collisions provide a unique environment... \n\n2. Methods\nWe use a standard feed-forward neural network to fit the pT spectra to a Tsallis distribution. The fit yields T=120 MeV and q=1.14.\n\n3. Conclusion\nThe early freeze-out is confirmed by the low temperature.",
};

// Mocked claims
const MOCK_CLAIMS = [
  { id: "c1", text: "Tsallis distribution perfectly describes the spectra up to 5 GeV", status: "Weak", evidenceCount: 2, csPotential: "High" },
  { id: "c2", text: "Temperature T = 120 MeV implies early freeze-out", status: "Needs CS upgrade", evidenceCount: 0, csPotential: "High" },
  { id: "c3", text: "Neural network robustly extracts parameters", status: "Supported", evidenceCount: 5, csPotential: "Low" }
];

// Mocked pipelines
const MOCK_PIPELINES = [
  { id: "gpu-mc", name: "GPU Monte Carlo Simulation", desc: "Large parameter explorations of claims.", complexity: "Heavy GPU" },
  { id: "auto-diff", name: "Auto-diff Re-fit", desc: "Re-fit with advanced optimizer (VI / HMC).", complexity: "Compute" },
  { id: "api-sym", name: "Symbolic Verification", desc: "Query external specialized API for math checks.", complexity: "External API" },
];

function PaperStudio() {
  const { paperId } = useParams({ strict: false });
  const [running, setRunning] = useState<Record<string, boolean>>({});
  const [selectedClaims, setSelectedClaims] = useState<Record<string, string[]>>({});

  const handleRun = (pipeId: string) => {
    setRunning(prev => ({ ...prev, [pipeId]: true }));
    setTimeout(() => {
      setRunning(prev => ({ ...prev, [pipeId]: false }));
      toast.success(`${pipeId} execution complete`);
    }, 2000);
  };

  const toggleClaimSelection = (pipeId: string, claimId: string) => {
    setSelectedClaims(prev => {
      const current = prev[pipeId] || [];
      if (current.includes(claimId)) {
        return { ...prev, [pipeId]: current.filter(id => id !== claimId) };
      }
      return { ...prev, [pipeId]: [...current, claimId] };
    });
  };

  return (
    <PageShell>
      {/* 2x2 Grid Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 pb-12">
        
        {/* Top-Left: Manuscript Context */}
        <Card className="flex flex-col h-[400px] border-border/50 shadow-sm">
          <CardHeader className="bg-muted/10 pb-4 border-b">
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-xl text-primary mb-1">{MOCK_PAPER.title}</CardTitle>
                <CardDescription className="font-mono text-xs">{paperId || MOCK_PAPER.id} • {MOCK_PAPER.authors}</CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Link to={`/papers/${paperId || MOCK_PAPER.id}/canvas`}>
                  <Button size="sm" variant="outline" className="h-7 text-xs border-primary/50 text-primary">
                    Switch to Canvas Mode
                  </Button>
                </Link>
                <Badge variant="secondary">{MOCK_PAPER.category}</Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-4 flex-1 overflow-y-auto">
            <h4 className="font-medium text-sm mb-2 text-foreground">Abstract</h4>
            <p className="text-sm text-muted-foreground leading-relaxed">{MOCK_PAPER.abstract}</p>
            
            <div className="mt-6 border-t pt-4">
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="outline" className="w-full">
                    <FileText className="w-4 h-4 mr-2" /> View Full Manuscript
                  </Button>
                </SheetTrigger>
                <SheetContent className="w-[800px] sm:max-w-none overflow-y-auto">
                  <SheetHeader>
                    <SheetTitle>{MOCK_PAPER.title}</SheetTitle>
                    <SheetDescription>Raw Extracted Text</SheetDescription>
                  </SheetHeader>
                  <div className="mt-6 whitespace-pre-wrap font-mono text-sm text-muted-foreground bg-muted/30 p-4 rounded-md">
                    {MOCK_PAPER.content}
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </CardContent>
        </Card>

        {/* Top-Right: Extracted Claims */}
        <Card className="flex flex-col h-[400px] border-border/50 shadow-sm">
          <CardHeader className="bg-muted/10 pb-4 border-b flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-xl flex items-center gap-2">
                <ListTodo className="w-5 h-5 text-primary" /> Extracted Claims
              </CardTitle>
              <CardDescription>Claims identified by LLM with CS upgrade potential.</CardDescription>
            </div>
            <Button variant="secondary" size="sm" onClick={() => toast("Extracting claims...")}>
              <Activity className="w-4 h-4 mr-2" /> Re-extract
            </Button>
          </CardHeader>
          <CardContent className="p-0 flex-1 overflow-y-auto">
            <Table>
              <TableHeader className="sticky top-0 bg-background z-10">
                <TableRow>
                  <TableHead className="pl-4">Claim Text</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Evid.</TableHead>
                  <TableHead className="pr-4">CS Potential</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {MOCK_CLAIMS.map(claim => (
                  <TableRow key={claim.id} className="hover:bg-muted/5">
                    <TableCell className="pl-4 text-sm font-medium leading-tight">{claim.text}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className={
                        claim.status === "Weak" ? "text-amber-500 border-amber-500/30" :
                        claim.status === "Needs CS upgrade" ? "text-destructive border-destructive/30" :
                        "text-emerald-500 border-emerald-500/30"
                      }>{claim.status}</Badge>
                    </TableCell>
                    <TableCell className="text-xs font-mono">{claim.evidenceCount}</TableCell>
                    <TableCell className="pr-4">
                      {claim.csPotential === "High" ? (
                        <Badge className="bg-violet-500 hover:bg-violet-600">High</Badge>
                      ) : (
                        <Badge variant="secondary">Low</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Bottom-Left: Pipeline Catalog (Per-Claim) */}
        <Card className="flex flex-col h-[500px] border-border/50 shadow-sm">
          <CardHeader className="bg-muted/10 pb-4 border-b">
            <CardTitle className="text-xl flex items-center gap-2">
              <FileCode2 className="w-5 h-5 text-primary" /> CS Upgrade Pipelines
            </CardTitle>
            <CardDescription>Select claims to target with specific algorithms.</CardDescription>
          </CardHeader>
          <CardContent className="p-4 flex-1 overflow-y-auto space-y-4">
            {MOCK_PIPELINES.map(pipe => {
              const selected = selectedClaims[pipe.id] || [];
              return (
                <div key={pipe.id} className="border border-border/50 rounded-lg p-4 bg-sidebar">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="font-semibold text-sm flex items-center gap-2">
                        {pipe.name}
                      </h4>
                      <p className="text-xs text-muted-foreground mt-1">{pipe.desc}</p>
                    </div>
                    <Badge variant="secondary" className="text-[10px] uppercase">{pipe.complexity}</Badge>
                  </div>
                  
                  <div className="bg-background rounded border p-2 mb-3 max-h-32 overflow-y-auto">
                    <div className="text-[10px] font-semibold uppercase text-muted-foreground mb-2 px-1">Target Claims</div>
                    {MOCK_CLAIMS.filter(c => c.csPotential === "High").map(claim => (
                      <div key={claim.id} className="flex items-start gap-2 p-1 hover:bg-muted/50 rounded">
                        <Checkbox 
                          id={`${pipe.id}-${claim.id}`} 
                          checked={selected.includes(claim.id)}
                          onCheckedChange={() => toggleClaimSelection(pipe.id, claim.id)}
                        />
                        <label htmlFor={`${pipe.id}-${claim.id}`} className="text-xs leading-none cursor-pointer">
                          {claim.text}
                        </label>
                      </div>
                    ))}
                  </div>

                  <Button 
                    className="w-full text-xs h-8" 
                    disabled={selected.length === 0 || running[pipe.id]}
                    onClick={() => handleRun(pipe.id)}
                  >
                    {running[pipe.id] ? (
                      <><Activity className="w-3 h-3 mr-2 animate-spin" /> Running...</>
                    ) : (
                      <><Play className="w-3 h-3 mr-2" /> Run on {selected.length} Claims</>
                    )}
                  </Button>
                </div>
              )
            })}
          </CardContent>
        </Card>

        {/* Bottom-Right: Results & Upgrade Suggestions */}
        <Card className="flex flex-col h-[500px] border-border/50 shadow-sm">
          <CardHeader className="bg-muted/10 pb-4 border-b">
            <CardTitle className="text-xl flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-500" /> Results & Upgrades
            </CardTitle>
            <CardDescription>Structured feedback per claim and actionable paths.</CardDescription>
          </CardHeader>
          <CardContent className="p-0 flex-1 overflow-y-auto">
            <div className="divide-y divide-border/50">
              
              <div className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className="border-violet-500/30 text-violet-500">Auto-diff Re-fit</Badge>
                  <span className="text-xs text-muted-foreground">targeting</span>
                  <span className="text-xs font-medium truncate max-w-[200px]">"Tsallis distribution perfectly..."</span>
                </div>
                <div className="bg-destructive/5 border border-destructive/20 rounded-md p-3 mb-3">
                  <p className="text-sm text-foreground mb-1"><AlertTriangle className="w-4 h-4 inline mr-1 text-destructive" /> Fit is under-optimized.</p>
                  <p className="text-xs text-muted-foreground">Re-fit using Variational Inference shows massive deviation above 3 GeV. The original simple least-squares missed local minima.</p>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="text-[10px] h-7">Promote to Manuscript Patch</Button>
                  <Button variant="outline" size="sm" className="text-[10px] h-7">Send to Ledger</Button>
                </div>
              </div>

              <div className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className="border-primary/30 text-primary">Symbolic Verification</Badge>
                  <span className="text-xs text-muted-foreground">targeting</span>
                  <span className="text-xs font-medium truncate max-w-[200px]">"Temperature T = 120 MeV implies..."</span>
                </div>
                <div className="bg-amber-500/5 border border-amber-500/20 rounded-md p-3 mb-3">
                  <p className="text-sm text-foreground mb-1"><AlertTriangle className="w-4 h-4 inline mr-1 text-amber-500" /> Mathematical Degeneracy Detected.</p>
                  <p className="text-xs text-muted-foreground">Symbolic Jacobian trace shows T and q are structurally degenerate in this regime. Cannot physically interpret T alone.</p>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="text-[10px] h-7">Open Task</Button>
                  <Button variant="outline" size="sm" className="text-[10px] h-7">Send to Ledger</Button>
                </div>
              </div>

            </div>
          </CardContent>
        </Card>

      </div>
    </PageShell>
  );
}
