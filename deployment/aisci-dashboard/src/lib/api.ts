const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

export type PipelineSpec = {
  id: string;
  name: string;
  status: string;
  requires_input?: string;
};

export type Metric = {
  label: string;
  value: string;
  delta: number;
  spark: number[];
  accent: "cyan" | "amber" | "emerald" | "violet";
};

export type Project = {
  id: string;
  title: string;
  owner: string;
  research_type: string;
  sensitivity: string;
  capabilities: string[];
};

export type Claim = {
  text: string;
  confidence: string;
};

export type Paper = {
  source: string;
  category: string;
  title: string;
  published: string;
  claims: number;
  bridge: boolean;
  abstract: string;
  url?: string;
  claimList: Claim[];
  provenance?: string;
  source_hash?: string;
};

export type EvidenceRow = {
  id: number;
  claim: string;
  status: string;
  nextGate: string;
  run: string;
  narrative: string;
};

export type TaskModel = {
  id: string;
  title: string;
  description: string;
  priority: string;
  assignee: string;
  date: string;
  citation?: string;
  status: string;
};

export type AgentModel = {
  name: string;
  status: string;
  last: string;
  summary: string;
  log: string[];
  provider?: string;
};

export type ActivityModel = {
  id: number;
  timestamp: string;
  action: string;
  user: string;
  details: string;
};

export type Anomaly = {
  bin: string;
  model: string;
  type: string;
  severity: string;
  message: string;
  value: number;
};

export type JobExecution = {
  id: string;
  project_id: string;
  pipeline_id: string;
  name: string;
  requester: string;
  status: string;
  created_at: string;
  updated_at?: string;
  log_path?: string;
  exit_code?: number;
  error?: string;
  git_commit?: string;
  artifact_manifest?: any[];
};

export type ReviewDecision = {
  id: string;
  project_id: string;
  target_id: string;
  requested_state: string;
  reviewer: string;
  status: string;
  created_at: string;
};

export async function dryRunPipeline(projectId: string, pipelineId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/pipelines/${pipelineId}/dry-run`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Failed to dry-run pipeline ${pipelineId}`);
  return res.json();
}

export type FitData = {
  fitRows: any[];
  chi2Series: any[];
  compareSeries?: any[];
  bins: string[];
  runId: string;
  status?: string;
  error?: string;
};

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_URL}/projects`);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

export async function fetchLiterature(projectId: string): Promise<Paper[]> {
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

export type ProjectOverview = {
  literature_count: number;
  claims_count: number;
  open_tasks: number;
  active_fits: number;
};

export type ProjectHealth = {
  status: string;
  runs_dir_exists?: boolean;
  message?: string;
};

export async function fetchProjectOverview(projectId: string): Promise<ProjectOverview> {
  const res = await fetch(`${API_URL}/projects/${projectId}/overview`);
  if (!res.ok) throw new Error("Failed to fetch project overview");
  return res.json();
}

export async function fetchProjectHealth(projectId: string): Promise<ProjectHealth> {
  const res = await fetch(`${API_URL}/projects/${projectId}/health`);
  if (!res.ok) throw new Error("Failed to fetch project health");
  return res.json();
}

export async function fetchExportSummary(projectId: string): Promise<{ markdown: string }> {
  const res = await fetch(`${API_URL}/projects/${projectId}/export/summary`);
  if (!res.ok) throw new Error("Failed to generate summary");
  return res.json();
}

export async function searchEvidence(projectId: string, query: string): Promise<EvidenceRow[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/evidence/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("Failed to search evidence");
  return res.json();
}

export async function materializeDecisions(projectId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/materialize`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to materialize decisions");
  return res.json();
}

export async function fetchEvidence(projectId: string): Promise<EvidenceRow[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/evidence`);
  if (!res.ok) throw new Error("Failed to fetch evidence");
  return res.json();
}

export async function fetchFits(
  projectId: string,
  run?: string,
  compareRun?: string,
): Promise<FitData> {
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

export async function fetchTasks(projectId: string): Promise<TaskModel[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/tasks`);
  if (!res.ok) throw new Error("Failed to fetch tasks");
  return res.json();
}

export async function fetchAgents(): Promise<AgentModel[]> {
  const res = await fetch(`${API_URL}/agents`);
  if (!res.ok) throw new Error("Failed to fetch agents");
  return res.json();
}

export async function fetchActivity(projectId: string): Promise<ActivityModel[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/activity`);
  if (!res.ok) throw new Error("Failed to fetch activity");
  return res.json();
}

export async function fetchPipelines(projectId: string): Promise<PipelineSpec[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/pipelines`);
  if (!res.ok) throw new Error("Failed to fetch pipelines");
  return res.json();
}

export async function fetchJobs(projectId: string): Promise<JobExecution[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/jobs`);
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

// Mutations
export async function triggerPipeline(projectId: string, pipelineId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/pipelines/${pipelineId}/run`, {
    method: "POST",
  });
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

