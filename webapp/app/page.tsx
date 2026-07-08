"use client"

import { useState } from "react"
import { MulticaShell } from "@/components/aisci/multica-shell"
import { TopBar } from "@/components/aisci/top-bar"
import { LeftRail } from "@/components/aisci/left-rail"
import { EvidenceLedger } from "@/components/aisci/evidence-ledger"
import { FittingPipeline } from "@/components/aisci/fitting-pipeline"
import { SpectraPlotter } from "@/components/aisci/spectra-plotter"
import { SymbolicValidation } from "@/components/aisci/symbolic-validation"
import { TestsDashboard } from "@/components/aisci/tests-dashboard"
import { OpsSurface } from "@/components/aisci/ops-surface"

export type Role = "scientist" | "devops"
export type Section = "evidence" | "pipeline" | "spectra" | "validation" | "tests" | "ops"

export default function AISCIConsole() {
  const [role, setRole] = useState<Role>("scientist")
  const [section, setSection] = useState<Section>("evidence")

  const handleRoleChange = (r: Role) => {
    setRole(r)
    setSection(r === "scientist" ? "evidence" : "ops")
  }

  return (
    <MulticaShell>
      <TopBar role={role} onRoleChange={handleRoleChange} />
      <div className="flex flex-1 min-h-0">
        <LeftRail role={role} section={section} onSection={setSection} />
        <main className="flex-1 overflow-y-auto">
          {section === "evidence"   && <EvidenceLedger />}
          {section === "pipeline"   && <FittingPipeline />}
          {section === "spectra"    && <SpectraPlotter />}
          {section === "validation" && <SymbolicValidation />}
          {section === "tests"      && <TestsDashboard />}
          {section === "ops"        && <OpsSurface />}
        </main>
      </div>
    </MulticaShell>
  )
}
