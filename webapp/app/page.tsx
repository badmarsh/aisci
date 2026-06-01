"use client"

import { useState } from "react"
import { TopBar } from "@/components/aisci/top-bar"
import { LeftRail } from "@/components/aisci/left-rail"
import { EvidenceLedger } from "@/components/aisci/evidence-ledger"
import { FittingPipeline } from "@/components/aisci/fitting-pipeline"
import { SpectraPlotter } from "@/components/aisci/spectra-plotter"
import { SymbolicValidation } from "@/components/aisci/symbolic-validation"

export type Role = "scientist" | "devops"
export type Section = "evidence" | "pipeline" | "spectra" | "validation" | "tests" | "ops"

export default function AISCIConsole() {
  const [role, setRole] = useState<Role>("scientist")
  const [section, setSection] = useState<Section>("evidence")

  const handleRoleChange = (r: Role) => {
    setRole(r)
    setSection(r === "scientist" ? "evidence" : "ops")
  }

  const NotImplemented = ({ name }: { name: string }) => (
    <div className="flex h-full items-center justify-center p-12 text-sm font-mono text-muted-foreground">
      {name} surface — not in v0 concept scope. Open the v0 chat to regenerate.
    </div>
  )

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background text-foreground font-sans">
      <TopBar role={role} onRoleChange={handleRoleChange} />
      <div className="flex flex-1 min-h-0">
        <LeftRail role={role} section={section} onSection={setSection} />
        <main className="flex-1 overflow-y-auto">
          {section === "evidence"   && <EvidenceLedger />}
          {section === "pipeline"   && <FittingPipeline />}
          {section === "spectra"    && <SpectraPlotter />}
          {section === "validation" && <SymbolicValidation />}
          {section === "tests"      && <NotImplemented name="Tests" />}
          {section === "ops"        && <NotImplemented name="Ops" />}
        </main>
      </div>
    </div>
  )
}
