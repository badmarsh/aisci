from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os

app = FastAPI(title="Multica Python Executor API")

class ScriptRequest(BaseModel):
    script: str
    args: list[str] = []

@app.post("/run_script")
def run_script(request: ScriptRequest):
    script_path = os.path.join("/home/ubuntu/aisci/deployment/helper", request.script)
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail="Script not found")
    
    cmd = ["python3", script_path] + request.args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"status": "success", "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "stdout": e.stdout, "stderr": e.stderr, "exit_code": e.returncode}

if __name__ == "__main__":
    import uvicorn
    # Listen on all interfaces so host.docker.internal can reach it
    uvicorn.run(app, host="0.0.0.0", port=8000)
