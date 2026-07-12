import { useMutation, useQueryClient } from "@tanstack/react-query";
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
  projectAgents: (projectId: string) => ["agents", projectId] as const,
  reviewRequests: (projectId: string) => ["reviewRequests", projectId] as const,
  overview: (projectId: string) => ["overview", projectId] as const,
};

export function useSyncMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => api.syncFromFiles(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.project(projectId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.overview(projectId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.evidence(projectId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks(projectId) });
    },
  });
}

export function useUpdateEvidenceMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status, narrative }: { id: number; status: string; narrative?: string }) =>
      api.updateEvidence(projectId, id, status, narrative),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.evidence(projectId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.overview(projectId) });
    },
  });
}

export function useUpdateTaskMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.updateTask(projectId, id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks(projectId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.overview(projectId) });
    },
  });
}

export function useTriggerPipelineMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (pipelineId: string) => api.triggerPipeline(projectId, pipelineId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.jobs(projectId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.overview(projectId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.pipelines(projectId) });
    },
  });
}

export function useMaterializeDecisionsMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => api.materializeDecisions(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.evidence(projectId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks(projectId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.overview(projectId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.reviewRequests(projectId) });
    },
  });
}

export function useRequestReviewMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      targetId,
      requestedState,
      targetKind,
    }: {
      targetId: string;
      requestedState: string;
      targetKind: string;
    }) => api.requestReview(projectId, targetId, requestedState, targetKind),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.reviewRequests(projectId) });
    },
  });
}
