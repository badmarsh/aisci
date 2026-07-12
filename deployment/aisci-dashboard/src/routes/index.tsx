import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { FolderTree, ArrowRight, ShieldCheck, Beaker, Activity, AlertTriangle, Layers, Zap, Search, FileText, CheckCircle, XCircle, UploadCloud, Github } from "lucide-react";
import { PageShell } from "@/components/PageShell";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Papers Studio — AiSci" },
      { name: "description", content: "AiSci Paper Triage and Studio" },
    ],
  }),
  component: PapersStudioHome,
});

// Mocked papers for My Workspace
const WORKSPACE_PAPERS = [
  {
    id: "robert-boson-manuscript",
    title: "Tsallis distribution in heavy-ion collisions",
    source: "research/robert/manuscript.md",
    lastExtraction: "2 hours ago",
    claimsCount: 14,
  },
  {
    id: "alice-spectra-draft",
    title: "ALICE spectra draft 2024",
    source: "github.com/alice/spectra",
    lastExtraction: "1 day ago",
    claimsCount: 22,
  }
];

// Mocked papers for Discovery
const DISCOVERY_PAPERS = [
  {
    id: "arxiv-2301-04221",
    title: "Thermal models and Tsallis statistics in high-energy collisions",
    authors: "C. Wong, G. Wilk",
    category: "nucl-th",
    affordance: "Simulation-testable",
    heuristics: { no_chi2: true, cs_heavy: false, no_formal_proof: false },
    provabilityScore: 85,
  },
  {
    id: "arxiv-2211-09876",
    title: "A neural network approach to freeze-out parameters",
    authors: "L. Chen, M. He",
    category: "cs.AI+nucl",
    affordance: "Data-analytic",
    heuristics: { no_chi2: false, cs_heavy: true, no_formal_proof: true },
    provabilityScore: 92,
  },
  {
    id: "arxiv-2105-11234",
    title: "Analytical properties of the generalized blast-wave",
    authors: "A. Bialas",
    category: "hep-ph",
    affordance: "Formally provable",
    heuristics: { no_chi2: true, tsallis_in_title: true, no_formal_proof: true },
    provabilityScore: 15,
  }
];

function PapersStudioHome() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [discoveryPapers, setDiscoveryPapers] = useState(DISCOVERY_PAPERS);

  const handleScanLiterature = () => {
    setIsSearching(true);
    fetch("http://localhost:8001/api/studio/discover", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: searchQuery || "Tsallis distribution" })
    })
    .then(res => res.json())
    .then(data => {
      if (data.papers) {
        setDiscoveryPapers(data.papers);
      }
    })
    .catch(err => {
      console.error("Discovery failed", err);
      // Fallback
    })
    .finally(() => setIsSearching(false));
  };

  const filteredDiscovery = discoveryPapers.filter(p => 
    p.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    p.authors.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <PageShell>
      <div className="mb-8">
        <h2 className="text-3xl font-bold tracking-tight">Paper Triage Studio</h2>
        <p className="text-muted-foreground mt-2 max-w-2xl text-sm leading-6">
          Find computer-science-n00b physics papers, run state-of-the-art CS algorithms on their claims, and make the papers better.
        </p>
      </div>

      <Tabs defaultValue="workspace" className="w-full">
        <TabsList className="mb-6 grid w-full md:w-[400px] grid-cols-2">
          <TabsTrigger value="workspace">My Workspace</TabsTrigger>
          <TabsTrigger value="discovery">Discovery & Triage</TabsTrigger>
        </TabsList>
        
        <TabsContent value="workspace">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
            {/* Left side: Known Manuscripts */}
            <div className="lg:col-span-2 space-y-4">
              <h3 className="text-lg font-semibold tracking-tight text-foreground flex items-center gap-2">
                <FileText className="w-4 h-4 text-primary" />
                Active Manuscripts
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {WORKSPACE_PAPERS.map(paper => (
                  <Card 
                    key={paper.id} 
                    className="glass-card hover:border-primary/50 transition cursor-pointer"
                    onClick={() => navigate({ to: `/papers/${paper.id}` })}
                  >
                    <CardHeader className="p-4 pb-2">
                      <CardTitle className="text-base text-primary line-clamp-1" title={paper.title}>{paper.title}</CardTitle>
                      <CardDescription className="font-mono text-xs text-muted-foreground truncate" title={paper.source}>
                        {paper.source}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="p-4 pt-2">
                      <div className="flex justify-between items-center text-xs mt-2">
                        <span className="text-muted-foreground flex items-center gap-1.5"><Activity className="w-3 h-3"/> Extracted {paper.lastExtraction}</span>
                        <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
                          {paper.claimsCount} claims
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Right side: Ingestion */}
            <div className="lg:col-span-1 space-y-4">
              <h3 className="text-lg font-semibold tracking-tight text-foreground flex items-center gap-2">
                <UploadCloud className="w-4 h-4 text-primary" />
                Add Paper to Studio
              </h3>
              <Card className="bg-sidebar border-border/40 shadow-sm">
                <CardContent className="p-4 pt-6 space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">GitHub Path or arXiv URL</label>
                    <Input placeholder="e.g. research/robert/manuscript.md" className="bg-background text-sm" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Document Type</label>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="w-full text-xs">Draft</Button>
                      <Button variant="outline" size="sm" className="w-full text-xs">Article</Button>
                      <Button variant="outline" size="sm" className="w-full text-xs">Thesis</Button>
                    </div>
                  </div>
                  <Button className="w-full mt-2" onClick={() => toast.success("Manuscript ingested!")}>
                    Ingest Manuscript
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="discovery">
          <Card className="mb-10 border-primary/20 shadow-sm">
            <CardHeader className="bg-muted/30 pb-4 border-b">
              <CardTitle className="text-xl flex items-center gap-2">
                <Search className="w-5 h-5 text-primary" />
                Find Papers with Weak Computing
              </CardTitle>
              <CardDescription>
                Uses FireCrawl & Academic to scan arXiv for papers lacking modern CS techniques (e.g., missing χ², naive fitting).
              </CardDescription>
              <div className="flex gap-3 mt-4">
                <Input 
                  placeholder="Search arXiv, OpenAlex, or Scite... (e.g. 'Tsallis deep learning')" 
                  className="max-w-xl bg-background"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <Button variant="default" onClick={handleScanLiterature} disabled={isSearching}>
                  {isSearching ? "Scanning..." : "Scan Literature"}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[400px]">Literature</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Heuristics / Affordance</TableHead>
                    <TableHead>Provability Score</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredDiscovery.map((paper) => (
                    <TableRow key={paper.id} className="hover:bg-muted/10 cursor-pointer" onClick={() => navigate({ to: `/papers/${paper.id}` })}>
                      <TableCell className="pl-6 py-4">
                        <div className="font-medium text-primary">{paper.title}</div>
                        <div className="text-xs text-muted-foreground mt-1">{paper.authors} • {paper.id}</div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" className="font-mono text-[10px]">{paper.category}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {paper.heuristics?.no_chi2 && <Badge variant="outline" className="text-amber-500 border-amber-500/30 bg-amber-500/5 text-[10px]">No χ² reported</Badge>}
                          {paper.heuristics?.cs_heavy && <Badge variant="outline" className="text-violet-500 border-violet-500/30 bg-violet-500/5 text-[10px]">CS-heavy / ML</Badge>}
                          {paper.heuristics?.no_formal_proof && <Badge variant="outline" className="text-red-500 border-red-500/30 bg-red-500/5 text-[10px]">No formal proof</Badge>}
                          {paper.affordance && <Badge variant="outline" className="text-indigo-500 border-indigo-500/30 bg-indigo-500/5 text-[10px]">{paper.affordance}</Badge>}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-secondary rounded-full h-2 max-w-[80px]">
                            <div 
                              className={`h-2 rounded-full ${paper.provabilityScore > 80 ? 'bg-emerald-500' : paper.provabilityScore > 50 ? 'bg-amber-500' : 'bg-destructive'}`} 
                              style={{ width: `${paper.provabilityScore}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-mono">{paper.provabilityScore}%</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right pr-6">
                        <Button size="sm" onClick={(e) => { e.stopPropagation(); navigate({ to: `/papers/${paper.id}` }); }}>
                          Open in Studio
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                  {filteredDiscovery.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        No papers found matching criteria.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
