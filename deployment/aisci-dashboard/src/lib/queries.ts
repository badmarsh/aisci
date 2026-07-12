import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "./api";

export const queryKeys = {
  projects: ["projects"] as const,
  project: (id: string) => ["projects", id] as const,
  pipelines: (projectId: string) => ["pipelines", projectId] as const,
  literature: (projectId: string) => ["literature", projectId] as const,
  anomalies: (projectId: string, run?: string) => ["anomalies", projectId, run] as const,
  evidence: (projectId: string) => ["evidence", projectId] as const,
  fits: (projectId: string, run?: string, compareRun?: string) =>
    ["fits", projectId, run, compareRun] as const,
  fitRuns: (projectId: string) => ["fits", "runs", projectId] as const,
  tasks: (projectId: string) => ["tasks", projectId] as const,
  activity: (projectId: string) => ["activity", projectId] as const,
  jobs: (projectId: string) => ["jobs", projectId] as const,
  agents: ["agents"] as const,
  reviewRequests: (projectId: string) => ["reviewRequests", projectId] as const,
  overview: (projectId: string) => ["overview", projectId] as const,
};
