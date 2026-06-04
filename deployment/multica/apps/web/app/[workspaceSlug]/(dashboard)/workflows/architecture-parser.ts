"use server";

import fs from "fs";
import path from "path";
import yaml from "yaml";

export async function getArchitectureMap() {
  const nodes: any[] = [];
  const edges: any[] = [];
  
  // Create Groups
  nodes.push({ id: "group-ui", type: "group", position: { x: 50, y: 50 }, data: { label: "Frontend Layer" }, style: { width: 400, height: 200 } });
  nodes.push({ id: "group-orch", type: "group", position: { x: 50, y: 300 }, data: { label: "Orchestration & Runtimes Layer" }, style: { width: 900, height: 350 } });
  nodes.push({ id: "group-infra", type: "group", position: { x: 50, y: 700 }, data: { label: "Infrastructure Layer" }, style: { width: 900, height: 250 } });
  nodes.push({ id: "group-science", type: "group", position: { x: 1000, y: 300 }, data: { label: "Science & Evidence Layer" }, style: { width: 400, height: 400 } });

  // 1. Frontend Node
  nodes.push({
    id: "ui-multica",
    type: "ui",
    position: { x: 50, y: 50 },
    parentId: "group-ui",
    extent: "parent",
    data: {
      label: "Multica Web App",
      type: "Next.js Application",
      description: "The main user interface for AISCI project workspaces and workflows.",
      path: "deployment/multica/apps/web",
      status: "active"
    }
  });

  // 2. Orchestration Layer (multica_custom_runtimes.yaml)
  const runtimePaths = [
    "/app/helper/multica_custom_runtimes.yaml",
    path.join(/*turbopackIgnore: true*/ process.cwd(), "../../../helper/multica_custom_runtimes.yaml"),
    path.join(/*turbopackIgnore: true*/ process.cwd(), "../../helper/multica_custom_runtimes.yaml"),
    path.join(/*turbopackIgnore: true*/ process.cwd(), "../helper/multica_custom_runtimes.yaml")
  ];

  let runtimesConfig: any = null;
  let runtimesPath = "";
  for (const p of runtimePaths) {
    if (fs.existsSync(p)) {
      try {
        runtimesConfig = yaml.parse(fs.readFileSync(p, "utf-8"));
        runtimesPath = p;
        break;
      } catch (e) {
        // ignore
      }
    }
  }

  nodes.push({
    id: "orch-router",
    type: "service",
    position: { x: 50, y: 50 },
    parentId: "group-orch",
    extent: "parent",
    data: {
      label: "Multica Router Engine",
      type: "Go Backend",
      description: "Routes events to the appropriate execution runtimes based on matching rules.",
      path: runtimesPath || "unknown",
      config: runtimesConfig?.routing || [],
      status: "active"
    }
  });
  
  edges.push({ id: "e-ui-router", source: "ui-multica", target: "orch-router", animated: true, style: { stroke: "#888" } });

  let runtimeX = 350;
  if (runtimesConfig?.runtimes) {
    for (const [key, rt] of Object.entries(runtimesConfig.runtimes)) {
      const typeStr = (rt as any).type || "builtin";
      nodes.push({
        id: `rt-${key}`,
        type: "agent",
        position: { x: runtimeX, y: 150 },
        parentId: "group-orch",
        extent: "parent",
        data: {
          label: `Runtime: ${key}`,
          type: typeStr.toUpperCase(),
          description: `Execution runtime configured in Multica daemon.`,
          path: runtimesPath,
          config: rt,
          status: "active"
        }
      });
      
      edges.push({
        id: `e-route-${key}`,
        source: "orch-router",
        target: `rt-${key}`,
        animated: true,
        label: "routes to",
        style: { stroke: "#888" }
      });
      runtimeX += 250;
    }
  }

  // 3. Infrastructure Layer (docker-compose.selfhost.yml / docker-compose.yml)
  const composePaths = [
    "/app/docker-compose.selfhost.yml",
    path.join(/*turbopackIgnore: true*/ process.cwd(), "../../docker-compose.selfhost.yml"),
    path.join(/*turbopackIgnore: true*/ process.cwd(), "../../../docker-compose.selfhost.yml")
  ];

  let composeConfig: any = null;
  let composePath = "";
  for (const p of composePaths) {
    if (fs.existsSync(p)) {
      try {
        composeConfig = yaml.parse(fs.readFileSync(p, "utf-8"));
        composePath = p;
        break;
      } catch (e) {
        // ignore
      }
    }
  }

  let infraX = 50;
  if (composeConfig?.services) {
    for (const [key, svc] of Object.entries(composeConfig.services)) {
      nodes.push({
        id: `infra-${key}`,
        type: "infrastructure",
        position: { x: infraX, y: 50 },
        parentId: "group-infra",
        extent: "parent",
        data: {
          label: key,
          type: "Docker Service",
          description: `Containerized service running as part of the local infrastructure.`,
          path: composePath,
          config: { image: (svc as any).image, ports: (svc as any).ports },
          status: "active"
        }
      });
      infraX += 220;
    }
  } else {
    // Fallback if not found
    ["postgres", "minio", "onyx"].forEach((key, idx) => {
      nodes.push({
        id: `infra-${key}`,
        type: "infrastructure",
        position: { x: 50 + (idx * 220), y: 50 },
        parentId: "group-infra",
        extent: "parent",
        data: {
          label: key,
          type: "Mock Service",
          description: `Could not parse docker-compose.`,
          status: "active"
        }
      });
    });
  }

  // 4. Science Layer (research/robert)
  const sciencePaths = [
    "/app/../../research/robert",
    path.join(/*turbopackIgnore: true*/ process.cwd(), "../../../../research/robert"),
    path.join(/*turbopackIgnore: true*/ process.cwd(), "../../../research/robert")
  ];

  let scienceDir = "";
  for (const p of sciencePaths) {
    if (fs.existsSync(p)) {
      scienceDir = p;
      break;
    }
  }

  let sciY = 50;
  if (scienceDir) {
    try {
      const files = fs.readdirSync(scienceDir).filter(f => f.endsWith(".md"));
      files.forEach((file) => {
        nodes.push({
          id: `sci-${file}`,
          type: "science",
          position: { x: 50, y: sciY },
          parentId: "group-science",
          extent: "parent",
          data: {
            label: file,
            type: "Science Ledger",
            description: `A core science/evidence document.`,
            path: `research/robert/${file}`,
            status: "active"
          }
        });
        
        // Connect Onyx Craft to Evidence Ledger as an example
        if (file === "evidence-ledger.md") {
          edges.push({
            id: `e-craft-ledger`,
            source: "rt-onyx-craft",
            target: `sci-${file}`,
            animated: true,
            label: "writes to",
            style: { stroke: "#10b981" }
          });
        }
        sciY += 100;
      });
    } catch(e) {}
  } else {
    nodes.push({
      id: `sci-ledger`,
      type: "science",
      position: { x: 50, y: 50 },
      parentId: "group-science",
      extent: "parent",
      data: {
        label: "evidence-ledger.md",
        type: "Science Ledger",
        description: `Mock ledger (directory not found).`,
        status: "active"
      }
    });
  }

  return { nodes, edges };
}
