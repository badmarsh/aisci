import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { fetchJobs } from "@/lib/api";
import { PageShell } from "@/components/PageShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, ChevronRight, ChevronDown, FileCode2 } from "lucide-react";
import React, { useState } from "react";
import type { Job } from "@/lib/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export const Route = createFileRoute("/projects/$projectId/jobs")({
  head: () => ({
    meta: [{ title: "Jobs — AiSci" }],
  }),
  component: JobsPage,
});

function JobsPage() {
  const { projectId } = Route.useParams();
  const [expandedJob, setExpandedJob] = useState<string | null>(null);

  const { data: jobs, isLoading, isError } = useQuery({
    queryKey: ["jobs", projectId],
    queryFn: () => fetchJobs(projectId!),
  });

  if (isLoading) {
    return (
      <PageShell>
        <div className="space-y-4">
          <div className="h-8 w-64 animate-pulse rounded bg-muted"></div>
          <div className="h-64 w-full animate-pulse rounded-lg bg-muted"></div>
        </div>
      </PageShell>
    );
  }

  if (isError) {
    return (
      <PageShell>
        <Card className="border-destructive/50 bg-destructive/10">
          <CardContent className="p-6 text-center text-destructive">
            <AlertTriangle className="mx-auto mb-2 h-8 w-8" />
            <p>Failed to load jobs.</p>
          </CardContent>
        </Card>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold tracking-tight">Pipeline Jobs</h1>
        </div>

        {!jobs || jobs.length === 0 ? (
          <Card className="glass-card">
            <CardContent className="flex flex-col items-center justify-center p-12 text-muted-foreground">
              <FileCode2 className="mb-4 h-12 w-12 opacity-20" />
              <p>No jobs have been executed yet.</p>
            </CardContent>
          </Card>
        ) : (
          <Card className="glass-card">
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead className="w-12"></TableHead>
                    <TableHead>Pipeline</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Commit</TableHead>
                    <TableHead>Artifacts</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {jobs.map((job: Job) => {
                    const isExpanded = expandedJob === job.id;
                    const statusColors: Record<string, string> = {
                      pending: "bg-muted text-muted-foreground",
                      running: "bg-blue-500/15 text-blue-500 ring-1 ring-blue-500/40",
                      completed: "bg-emerald-brand/15 text-emerald-brand ring-1 ring-emerald-brand/40",
                      failed: "bg-rose-brand/15 text-rose-brand ring-1 ring-rose-brand/40",
                    };
                    return (
                      <React.Fragment key={job.id}>
                        <TableRow
                          className="cursor-pointer border-border transition hover:bg-primary/5"
                          onClick={() => setExpandedJob(isExpanded ? null : job.id)}
                        >
                          <TableCell>
                            {isExpanded ? (
                              <ChevronDown className="h-4 w-4 text-muted-foreground" />
                            ) : (
                              <ChevronRight className="h-4 w-4 text-muted-foreground" />
                            )}
                          </TableCell>
                          <TableCell className="font-medium">{job.pipeline_id}</TableCell>
                          <TableCell>
                            <Badge className={statusColors[job.status] || "bg-muted"}>
                              {job.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-muted-foreground text-sm">
                            {new Date(job.created_at).toLocaleString()}
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            {job.git_commit ? job.git_commit.slice(0, 8) : "—"}
                          </TableCell>
                          <TableCell className="text-sm">
                            {job.artifact_manifest?.length || 0} items
                          </TableCell>
                        </TableRow>
                        {isExpanded && (
                          <TableRow className="bg-muted/30 hover:bg-muted/30">
                            <TableCell colSpan={6} className="p-0">
                              <div className="p-4 border-b border-border">
                                <h4 className="mb-2 text-sm font-semibold text-foreground">
                                  Artifact Manifest
                                </h4>
                                {job.artifact_manifest && job.artifact_manifest.length > 0 ? (
                                  <div className="space-y-1">
                                    {job.artifact_manifest.map((art, idx) => (
                                      <div
                                        key={idx}
                                        className="flex items-center justify-between rounded-md bg-background px-3 py-2 text-xs font-mono"
                                      >
                                        <span className="text-foreground">{art.path}</span>
                                        <div className="flex gap-4 text-muted-foreground">
                                          <span>{art.size} bytes</span>
                                          <span className="opacity-50" title={art.sha256}>
                                            {art.sha256.slice(0, 8)}...
                                          </span>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                ) : (
                                  <p className="text-sm text-muted-foreground">
                                    No artifacts recorded for this run.
                                  </p>
                                )}
                                {job.error && (
                                  <div className="mt-4 rounded-md border border-rose-brand/30 bg-rose-brand/10 p-3 text-sm text-rose-brand">
                                    <span className="font-semibold">Error:</span> {job.error}
                                  </div>
                                )}
                              </div>
                            </TableCell>
                          </TableRow>
                        )}
                      </React.Fragment>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </PageShell>
  );
}
