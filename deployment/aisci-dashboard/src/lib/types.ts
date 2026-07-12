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
  source: string;
  category: string;
  title: string;
  published: string;
  claims: number;
  bridge: boolean;
  abstract: string;
  url?: string;
  claimList: { text: string; confidence: string }[];
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

export type Task = {
  id: string;
  title: string;
  description: string;
  priority: string;
  assignee: string;
  date: string;
  citation?: string;
  status: string;
};

export type Agent = {
  name: string;
  status: string;
  last: string;
  summary: string;
  log: string[];
  provider?: string;
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
  type: string;
  severity: string;
  message: string;
  value: number;
};
