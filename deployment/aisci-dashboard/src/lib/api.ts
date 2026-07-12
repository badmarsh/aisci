import { z } from "zod";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

export const PipelineSpecSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: z.string(),
  requires_input: z.string().optional(),
  available: z.boolean().optional(),
  checks: z
    .array(
      z.object({
        name: z.string(),
        passed: z.boolean(),
        message: z.string().optional(),
      }),
    )
    .optional(),
});
export type PipelineSpec = z.infer<typeof PipelineSpecSchema>;

export const MetricSchema = z.object({
  label: z.string(),
  value: z.string(),
  delta: z.number(),
  spark: z.array(z.number()),
  accent: z.enum(["cyan", "amber", "emerald", "violet"]),
});
export type Metric = z.infer<typeof MetricSchema>;

export const ProjectSchema = z.object({
  id: z.string(),
  title: z.string(),
  owner: z.string(),
  research_type: z.string(),
  sensitivity: z.string(),
  capabilities: z.array(z.string()),
});
export type Project = z.infer<typeof ProjectSchema>;

export const ClaimSchema = z.object({
  text: z.string(),
  confidence: z.string(),
});
export type Claim = z.infer<typeof ClaimSchema>;

export const PaperSchema = z.object({
  source: z.string(),
  category: z.string(),
  title: z.string(),
  published: z.string(),
  claims: z.number(),
  bridge: z.boolean(),
  abstract: z.string(),
  url: z.string().optional(),
  claimList: z.array(ClaimSchema),
  provenance: z.string().optional(),
  source_hash: z.string().optional(),
});
export type Paper = z.infer<typeof PaperSchema>;

export const EvidenceRowSchema = z.object({
  id: z.number(),
  claim: z.string(),
  status: z.string(),
  nextGate: z.string(),
  run: z.string(),
  narrative: z.string(),
  review_status: z.string().optional(),
});
export type EvidenceRow = z.infer<typeof EvidenceRowSchema>;

export const TaskSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string(),
  priority: z.string(),
  assignee: z.string(),
  date: z.string(),
  citation: z.string().optional(),
  status: z.string(),
});
export type Task = z.infer<typeof TaskSchema>;
export type TaskModel = Task;

export const AgentSchema = z.object({
  name: z.string(),
  status: z.string(),
  last: z.string(),
  summary: z.string(),
  log: z.array(z.string()),
  provider: z.string().optional(),
});
export type Agent = z.infer<typeof AgentSchema>;
export type AgentModel = Agent;

export const ActivitySchema = z.object({
  id: z.number(),
  timestamp: z.string(),
  action: z.string(),
  user: z.string(),
  details: z.string(),
});
export type Activity = z.infer<typeof ActivitySchema>;
export type ActivityModel = Activity;

export const AnomalySchema = z.object({
  bin: z.string(),
  model: z.string(),
  type: z.string(),
  severity: z.string(),
  message: z.string(),
  value: z.number(),
});
export type Anomaly = z.infer<typeof AnomalySchema>;

export const JobExecutionSchema = z.object({
  id: z.string(),
  project_id: z.string(),
  pipeline_id: z.string(),
  name: z.string(),
  requester: z.string(),
  status: z.string(),
  created_at: z.string(),
  updated_at: z.string().optional(),
  log_path: z.string().optional(),
  exit_code: z.number().optional(),
  error: z.string().optional(),
  git_commit: z.string().optional(),
  artifact_manifest: z
    .array(
      z.object({
        path: z.string(),
        size: z.union([z.string(), z.number()]),
        sha256: z.string().optional(),
      }),
    )
    .optional(),
});
export type JobExecution = z.infer<typeof JobExecutionSchema>;

export const ReviewDecisionSchema = z.object({
  id: z.string(),
  project_id: z.string(),
  target_id: z.string(),
  requested_state: z.string(),
  reviewer: z.string(),
  status: z.string(),
  created_at: z.string(),
});
export type ReviewDecision = z.infer<typeof ReviewDecisionSchema>;

export const FitRowSchema = z.object({
  bin: z.string(),
  model: z.string(),
  chi2: z.number().optional(),
  quality: z.enum(["POOR", "MARGINAL", "GOOD"]).optional(),
  T: z.string().optional(),
  beta: z.string().optional(),
  aic: z.number().optional(),
  ndf: z.number().optional(),
  status: z.string(),
  correlations: z.record(z.number()).optional(),
  seedIndex: z.number().nullable().optional(),
  runTimestamp: z.string().optional(),
  params: z.record(z.number()).optional(),
});
export type FitRow = z.infer<typeof FitRowSchema>;

export const FitDataSchema = z.object({
  fitRows: z.array(FitRowSchema),
  chi2Series: z.array(z.record(z.union([z.number(), z.string()]))),
  compareSeries: z.array(z.record(z.union([z.number(), z.string()]))).optional(),
  bins: z.array(z.string()),
  runId: z.string(),
  status: z.string().optional(),
  error: z.string().optional(),
});
export type FitData = z.infer<typeof FitDataSchema>;

export const ProjectOverviewSchema = z.object({
  literature_count: z.number(),
  claims_count: z.number(),
  open_tasks: z.number(),
  active_fits: z.number(),
  active_jobs: z.number().optional(),
  completed_jobs: z.number().optional(),
  failed_jobs: z.number().optional(),
  anomalies_count: z.number().optional(),
  worker_health: z.boolean().optional(),
  recent_activity: z.array(ActivitySchema).optional(),
  parse_warnings: z.array(z.string()).optional(),
});
export type ProjectOverview = z.infer<typeof ProjectOverviewSchema>;

export const ProjectHealthSchema = z.object({
  status: z.string(),
  runs_dir_exists: z.boolean().optional(),
  message: z.string().optional(),
});
export type ProjectHealth = z.infer<typeof ProjectHealthSchema>;

export async function dryRunPipeline(projectId: string, pipelineId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/pipelines/${pipelineId}/dry-run`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Failed to dry-run pipeline ${pipelineId}`);
  return PipelineSpecSchema.parse(await res.json());
}

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_URL}/projects`);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return z.array(ProjectSchema).parse(await res.json());
}

export async function fetchProject(projectId: string): Promise<Project> {
  const projects = await fetchProjects();
  const proj = projects.find((p) => p.id === projectId);
  if (!proj) throw new Error("Project not found");
  return proj;
}

export async function fetchLiterature(projectId: string): Promise<Paper[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/literature`);
  if (!res.ok) throw new Error("Failed to fetch literature");
  return z.array(PaperSchema).parse(await res.json());
}

export async function fetchAnomalies(projectId: string, run?: string): Promise<Anomaly[]> {
  const params = new URLSearchParams();
  if (run) params.set("run", run);

  const res = await fetch(`${API_URL}/projects/${projectId}/anomalies?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch anomalies");
  return z.array(AnomalySchema).parse(await res.json());
}

export async function fetchProjectOverview(projectId: string): Promise<ProjectOverview> {
  const res = await fetch(`${API_URL}/projects/${projectId}/overview`);
  if (!res.ok) throw new Error("Failed to fetch project overview");
  return ProjectOverviewSchema.parse(await res.json());
}

export async function fetchProjectHealth(projectId: string): Promise<ProjectHealth> {
  const res = await fetch(`${API_URL}/projects/${projectId}/health`);
  if (!res.ok) throw new Error("Failed to fetch project health");
  return ProjectHealthSchema.parse(await res.json());
}

export async function fetchExportSummary(projectId: string): Promise<{ markdown: string }> {
  const res = await fetch(`${API_URL}/projects/${projectId}/export/summary`);
  if (!res.ok) throw new Error("Failed to generate summary");
  return res.json();
}

export async function searchEvidence(projectId: string, query: string): Promise<EvidenceRow[]> {
  const res = await fetch(
    `${API_URL}/projects/${projectId}/evidence/search?q=${encodeURIComponent(query)}`,
  );
  if (!res.ok) throw new Error("Failed to search evidence");
  return z.array(EvidenceRowSchema).parse(await res.json());
}

export async function materializeDecisions(projectId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/materialize`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to materialize decisions");
  return res.json();
}

export async function fetchEvidence(projectId: string): Promise<EvidenceRow[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/evidence`);
  if (!res.ok) throw new Error("Failed to fetch evidence");
  return z.array(EvidenceRowSchema).parse(await res.json());
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
  return FitDataSchema.parse(await res.json());
}

export async function fetchFitRuns(projectId: string): Promise<{ runs: string[] }> {
  const res = await fetch(`${API_URL}/projects/${projectId}/fits/runs`);
  if (!res.ok) throw new Error("Failed to fetch run list");
  return z.object({ runs: z.array(z.string()) }).parse(await res.json());
}

export async function fetchTasks(projectId: string): Promise<Task[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/tasks`);
  if (!res.ok) throw new Error("Failed to fetch tasks");
  return z.array(TaskSchema).parse(await res.json());
}

export async function fetchAgents(projectId?: string): Promise<Agent[]> {
  const url = projectId ? `${API_URL}/projects/${projectId}/agents` : `${API_URL}/agents`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch agents");
  return z.array(AgentSchema).parse(await res.json());
}

export async function fetchActivity(projectId: string): Promise<Activity[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/activity`);
  if (!res.ok) throw new Error("Failed to fetch activity");
  return z.array(ActivitySchema).parse(await res.json());
}

export async function fetchPipelines(projectId: string): Promise<PipelineSpec[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/pipelines`);
  if (!res.ok) throw new Error("Failed to fetch pipelines");
  return z.array(PipelineSpecSchema).parse(await res.json());
}

export async function fetchJobs(projectId: string): Promise<JobExecution[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/jobs`);
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return z.array(JobExecutionSchema).parse(await res.json());
}

export async function fetchJobLogs(projectId: string, jobId: string): Promise<{ logs: string }> {
  const res = await fetch(`${API_URL}/projects/${projectId}/jobs/${jobId}/logs`);
  if (!res.ok) throw new Error("Failed to fetch job logs");
  return res.json();
}

export async function requestReview(
  projectId: string,
  targetId: string,
  requestedState: string,
  targetKind: string,
) {
  const res = await fetch(`${API_URL}/projects/${projectId}/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target_id: targetId,
      requested_state: requestedState,
      target_kind: targetKind,
    }),
  });
  if (!res.ok) throw new Error("Failed to request review");
  return ReviewDecisionSchema.parse(await res.json());
}

export async function fetchReviews(projectId: string): Promise<ReviewDecision[]> {
  const res = await fetch(`${API_URL}/projects/${projectId}/reviews`);
  if (!res.ok) throw new Error("Failed to fetch reviews");
  return z.array(ReviewDecisionSchema).parse(await res.json());
}

export async function approveReview(projectId: string, reviewId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/reviews/${reviewId}/approve`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to approve review");
  return ReviewDecisionSchema.parse(await res.json());
}

export async function rejectReview(projectId: string, reviewId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/reviews/${reviewId}/reject`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to reject review");
  return ReviewDecisionSchema.parse(await res.json());
}

export async function triggerPipeline(projectId: string, pipelineId: string) {
  const res = await fetch(`${API_URL}/projects/${projectId}/pipelines/${pipelineId}/run`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Failed to trigger pipeline ${pipelineId}`);
  return res.json();
}

export async function updateEvidence(
  projectId: string,
  id: number,
  status: string,
  narrative?: string,
) {
  const res = await fetch(`${API_URL}/projects/${projectId}/evidence/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, narrative }),
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
