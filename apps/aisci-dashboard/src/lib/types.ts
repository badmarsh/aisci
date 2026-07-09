export type FitRow = {
  bin: string;
  model: "Jüttner 1c" | "Tsallis 2c" | "Bose-Einstein 1c";
  chi2: number;
  quality: "POOR" | "MARGINAL" | "GOOD";
  T: string;
  beta: string;
  aic: number;
  status: string;
  correlations: Record<string, number>;
  seedIndex: number | null;
  runTimestamp: string;
};

export type Paper = {
  source: "arXiv" | "OpenAlex";
  category: string;
  title: string;
  published: string;
  claims: number;
  bridge: boolean;
  abstract: string;
  url: string;
  claimList: { text: string; confidence: "HIGH" | "MEDIUM" | "LOW" }[];
};

export type EvidenceRow = {
  id: number;
  claim: string;
  status: "Supported" | "Sanity Checked" | "Proposed" | "Rejected";
  nextGate: string;
  run: string;
  narrative: string;
};

export type Task = {
  id: string;
  title: string;
  description: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  assignee: "RB" | "AI";
  date: string;
  citation?: string;
  status: "active" | "blocked" | "proposed" | "closed";
};

export type Agent = {
  name: string;
  status: "ACTIVE" | "IDLE" | "WAITING";
  last: string;
  summary: string;
  log: string[];
};

export type Activity = {
  id: number;
  timestamp: string;
  action: string;
  user: string;
  details: string;
};

export type Anomaly = {
  bin: string;
  model: string;
  type: "chi2" | "correlation" | "boundary";
  severity: "critical" | "warning";
  message: string;
};
