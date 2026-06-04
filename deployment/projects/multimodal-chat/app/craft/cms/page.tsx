"use client"

import { useEffect } from "react"
import mermaid from "mermaid"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function CMSWorkflowPage() {
  useEffect(() => {
    mermaid.initialize({ startOnLoad: true, theme: 'dark' })
    mermaid.contentLoaded()
  }, [])

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <header className="flex items-center gap-4 border-b border-border pb-4">
          <Link href="/" className="p-2 hover:bg-accent rounded-full transition-colors">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">AiSci CMS & Architecture</h1>
            <p className="text-muted-foreground mt-1">Understanding the automated research pipeline</p>
          </div>
        </header>

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold">The RAG vs Canon Boundary</h2>
          <p className="text-muted-foreground leading-relaxed">
            The AiSci platform uses a strict routing boundary to prevent LLM hallucinations. RAG (Onyx) is strictly used for pulling external knowledge, while Canonical tools read live project files.
          </p>
          
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm overflow-x-auto">
            <pre className="mermaid text-center">
{`graph TD
    User([User / Persona]) --> Router{Question Type?}
    
    %% RAG Pathway
    Router -- "External Literature\\n(Papers, Theories)" --> Onyx[Onyx RAG Engine]
    Onyx --> Qwen[Qwen2.5-VL 7B]
    Onyx --> Vespa[(Vespa Vector DB)]
    Vespa --> TruthSet[External Literature Set]
    
    %% Canon Pathway
    Router -- "Internal Project Status\\n(Ledger, Drafts)" --> ReadFile[read_file Tool]
    ReadFile --> Ledger[(evidence-ledger.md)]
    ReadFile --> Backlog[(platform-backlog.md)]
    
    %% Styling
    classDef default fill:#1e1e2e,stroke:#313244,stroke-width:2px,color:#cdd6f4;
    classDef decision fill:#89b4fa,stroke:#1e1e2e,stroke-width:2px,color:#11111b,font-weight:bold;
    classDef db fill:#f38ba8,stroke:#1e1e2e,stroke-width:2px,color:#11111b;
    
    class Router decision;
    class Vespa,Ledger,Backlog,TruthSet db;
`}
            </pre>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-3 text-primary">The Vision Pipeline</h3>
            <p className="text-sm text-muted-foreground mb-4">
              When PDFs are ingested, the pipeline routes visual data to the GPU.
            </p>
            <pre className="mermaid text-center">
{`graph LR
    PDF[PDF Upload] --> Parse[Unstructured]
    Parse -- "Text" --> Embed[GTE-1.5B]
    Parse -- "Image" --> Qwen[Qwen2.5-VL]
    Qwen -- "Visual Summary" --> Embed
    Embed --> Chunk[Vespa Chunk]
`}
            </pre>
          </div>

          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-3 text-primary">Persona Scoping</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Personas are locked to specific document sets to prevent cross-contamination.
            </p>
            <pre className="mermaid text-center">
{`graph TD
    Validator[Physics Validator] --> Truth[Truth Set]
    Validator --> Draft[Working Drafts]
    
    Dev[Project Analyst] --> Code[Codebase]
    Dev --> Ops[Meta-Docs]
    
    style Validator fill:#a6e3a1,color:#11111b
    style Dev fill:#f9e2af,color:#11111b
`}
            </pre>
          </div>
        </section>
      </div>
    </div>
  )
}
