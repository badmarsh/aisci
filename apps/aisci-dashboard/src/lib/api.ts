const API_URL = "http://localhost:8001/api";

export async function fetchLiterature() {
  const res = await fetch(`${API_URL}/literature`);
  if (!res.ok) throw new Error("Failed to fetch literature");
  return res.json();
}

import type { Anomaly } from "./types";

export async function fetchAnomalies(run?: string, chi2Critical = 200.0, chi2Warning = 10.0, rhoWarning = 0.95): Promise<Anomaly[]> {
  const params = new URLSearchParams();
  if (run) params.set("run", run);
  params.set("chi2_critical", chi2Critical.toString());
  params.set("chi2_warning", chi2Warning.toString());
  params.set("rho_warning", rhoWarning.toString());
  
  const url = `${API_URL}/anomalies?${params.toString()}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch anomalies");
  return res.json();
}

export async function fetchExportSummary(): Promise<{ markdown: string }> {
  const res = await fetch(`${API_URL}/export/summary`);
  if (!res.ok) throw new Error("Failed to generate summary");
  return res.json();
}

export async function fetchEvidence() {
  const res = await fetch(`${API_URL}/evidence`);
  if (!res.ok) throw new Error("Failed to fetch evidence");
  return res.json();
}

export async function fetchFits(run?: string, compareRun?: string) {
  const params = new URLSearchParams();
  if (run) params.set("run", run);
  if (compareRun) params.set("compare_run", compareRun);
  const qs = params.toString();
  const url = `${API_URL}/fits${qs ? `?${qs}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch fits");
  return res.json();
}

export async function fetchFitRuns(): Promise<{ runs: string[] }> {
  const res = await fetch(`${API_URL}/fits/runs`);
  if (!res.ok) throw new Error("Failed to fetch run list");
  return res.json();
}

export async function fetchTasks() {
  const res = await fetch(`${API_URL}/tasks`);
  if (!res.ok) throw new Error("Failed to fetch tasks");
  return res.json();
}

export async function fetchAgents() {
  const res = await fetch(`${API_URL}/agents`);
  if (!res.ok) throw new Error("Failed to fetch agents");
  return res.json();
}

export async function fetchActivity() {
  const res = await fetch(`${API_URL}/activity`);
  if (!res.ok) throw new Error("Failed to fetch activity");
  return res.json();
}

// Mutations
export async function triggerIngest() {
  const res = await fetch(`${API_URL}/ingest`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to trigger ingest");
  return res.json();
}

export async function triggerFits() {
  const res = await fetch(`${API_URL}/fits/run`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to trigger fits");
  return res.json();
}

export async function updateEvidence(id: number, status: string) {
  const res = await fetch(`${API_URL}/evidence/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Failed to update evidence");
  return res.json();
}

export async function updateTask(id: string, status: string) {
  const res = await fetch(`${API_URL}/tasks/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Failed to update task");
  return res.json();
}

export async function syncFromFiles() {
  const res = await fetch(`${API_URL}/sync`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to sync from files");
  return res.json();
}
