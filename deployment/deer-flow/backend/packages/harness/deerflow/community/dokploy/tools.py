import json
import os
import subprocess
import tempfile
from typing import Optional

from langchain.tools import tool

@tool("dokploy_deploy", parse_docstring=True)
def dokploy_deploy_tool(github_url: str, app_name: str, branch: str = "main", project_name: str = "deerflow-apps", dokploy_url: str = "http://localhost:3000") -> str:
    """Deploy a GitHub repository to the Dokploy server using the Dokploy API.
    
    This tool dynamically creates a Node.js script to interface with the Dokploy SDK 
    and handles project and application creation before deploying.

    Args:
        github_url: The full URL to the GitHub repository (e.g. https://github.com/user/repo)
        app_name: The name of the application to create on Dokploy.
        branch: The branch to deploy (default: main).
        project_name: The Dokploy project name (default: deerflow-apps).
        dokploy_url: The URL of the Dokploy instance (default: http://localhost:3000).
    """
    api_key = os.environ.get("DOKPLOY_API_KEY", "")
    if not api_key:
        return "Error: DOKPLOY_API_KEY environment variable is not set."

    # Using fetch to call Dokploy TRPC directly instead of relying on exact SDK typings
    # The Dokploy TRPC endpoints are standard: /api/trpc/project.create, /api/trpc/application.create
    # However, the SDK is safer. We will use a Node.js script.
    
    node_script = f"""
import {{ Dokploy }} from "dokploy";

const dokploy = new Dokploy({{
    bearerAuth: "{api_key}",
    serverURL: "{dokploy_url}",
}});

async function deploy() {{
    try {{
        console.log("Fetching projects...");
        // Handle different SDK versions of findMany/get
        let projects = [];
        try {{
            projects = await dokploy.project.findMany();
        }} catch (e) {{
            // fallback if findMany is not the exact method
            console.log("Could not findMany projects, attempting alternative...", e.message);
        }}
        
        let projectId = null;
        if (projects && projects.length) {{
            const project = projects.find(p => p.name === "{project_name}");
            if (project) projectId = project.projectId;
        }}

        if (!projectId) {{
            console.log("Creating project {project_name}...");
            try {{
                const newProject = await dokploy.project.create({{ name: "{project_name}" }});
                projectId = newProject.projectId || newProject.id;
            }} catch(e) {{
                console.error("Failed to create project:", e.message);
            }}
        }}
        
        if (!projectId) {{
            console.log("Warning: Proceeding without projectId, deployment might fail.");
        }}

        console.log("Creating application {app_name}...");
        let appId = null;
        try {{
            const app = await dokploy.application.create({{
                name: "{app_name}",
                projectId: projectId,
                repository: "{github_url}",
                branch: "{branch}",
            }});
            appId = app.applicationId || app.id;
            console.log("Application created with ID:", appId);
        }} catch(e) {{
            console.log("Application creation failed (might already exist):", e.message);
            // In a real scenario we would find the existing app and update it, 
            // but we rely on the user/agent specifying a unique app_name for simplicity.
        }}

        if (appId) {{
            console.log("Deploying application...");
            const deployResult = await dokploy.application.deploy({{
                applicationId: appId,
            }});
            console.log("Deployment triggered!", deployResult);
        }} else {{
            console.log("Could not obtain Application ID to deploy.");
        }}

    }} catch (error) {{
        console.error("Dokploy deployment script failed:", error);
        process.exit(1);
    }}
}}

deploy();
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "deploy.mjs")
        with open(script_path, "w") as f:
            f.write(node_script)
        
        try:
            # Install Dokploy SDK locally in the temp dir
            subprocess.run(["npm", "init", "-y"], cwd=tmpdir, check=True, capture_output=True)
            subprocess.run(["npm", "install", "dokploy"], cwd=tmpdir, check=True, capture_output=True)
            
            # Execute the script
            result = subprocess.run(
                ["node", script_path], 
                cwd=tmpdir, 
                text=True, 
                capture_output=True, 
                check=True
            )
            return f"Deployment executed.\\nOutput:\\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Deployment failed.\\nStdout: {e.stdout}\\nStderr: {e.stderr}"
        except Exception as e:
            return f"Unexpected error during deployment execution: {str(e)}"
