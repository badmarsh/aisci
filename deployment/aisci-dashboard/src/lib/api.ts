const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

import type { Anomaly } from "./types";

export type PipelineSpec = {
  id: string;
  name: string;
  status: string;
  requires_input?: string;
};

export async function fetchProjects() {
  const res = await fetch(`${API_URL}/projects`);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

export async function fetchLiterature(projectId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/literature`);
  if (!res.ok) throw new Error("Failed to fetch literature");
  return res.json();
}

export async function fetchAnomalies(projectId: string, run?: string): Promise<Anomaly[]> {
  const params = new URLSearchParams();
  if (run) params.set("run", run);

  const res = await fetch(`${API_URL}/projects/${projectId}/anomalies?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch anomalies");
  return res.json();
}

export async function fetchExportSummary(projectId: string): Promise<{ markdown: string }> {
  const res = await fetch(`${API_URL}/projects/${projectId}/export/summary`);
  if (!res.ok) throw new Error("Failed to generate summary");
  return res.json();
}

export async function fetchEvidence(projectId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/evidence`);
  if (!res.ok) throw new Error("Failed to fetch evidence");
  return res.json();
}

export async function fetchFits(projectId: string, run?: string, compareRun?: string) {
  const params = new URLSearchParams();
  if (run) params.set("run", run);
  if (compareRun) params.set("compare_run", compareRun);
  const qs = params.toString();
  const url = `${API_URL}/projects/${projectId}/fits${qs ? `?${qs}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch fits");
  return res.json();
}

export async function fetchFitRuns(projectId: string): Promise<{ runs: string[] }> {
  const res = await fetch(`${API_URL}/projects/${projectId}/fits/runs`);
  if (!res.ok) throw new Error("Failed to fetch run list");
  return res.json();
}

export async function fetchTasks(projectId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/tasks`);
  if (!res.ok) throw new Error("Failed to fetch tasks");
  return res.json();
}

export async function fetchAgents() {
  const res = await fetch(`${API_URL}/agents`);
  if (!res.ok) throw new Error("Failed to fetch agents");
  return res.json();
}

export async function fetchActivity(projectId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/activity`);
  if (!res.ok) throw new Error("Failed to fetch activity");
  return res.json();
}

export async function fetchPipelines(projectId: string): Promise<PipelineSpec[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/pipelines`);
  if (!res.ok) throw new Error("Failed to fetch pipelines");
  return res.json();
}

export async function fetchJobs(projectId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/jobs`);
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

// Mutations
export async function triggerPipeline(projectId: string, pipelineId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/pipelines/${pipelineId}/run`, { method: "POST" });
  if (!res.ok) throw new Error(`Failed to trigger pipeline ${pipelineId}`);
  return res.json();
}

export async function updateEvidence(projectId: string, id: number, status: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/evidence/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Failed to update evidence");
  return res.json();
}

export async function updateTask(projectId: string, id: string, status: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/tasks/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Failed to update task");
  return res.json();
}

export async function syncFromFiles(projectId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/sync`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to sync from files");
  return res.json();
}

