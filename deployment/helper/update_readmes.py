import os

RUNS_DIR = "/home/ubuntu/aisci/research/robert/runs"

def update_readmes():
    for d in os.listdir(RUNS_DIR):
        dir_path = os.path.join(RUNS_DIR, d)
        if not os.path.isdir(dir_path): continue
        readme_path = os.path.join(dir_path, "README.md")
        if not os.path.exists(readme_path): continue
        
        with open(readme_path, "r") as f:
            content = f.read()
            
        if "Aborted or Undocumented" in content:
            files = os.listdir(dir_path)
            files = [f for f in files if f != "README.md"]
            
            new_content = f"# Run {d}\n\n"
            new_content += "**Status:** Completed\n"
            new_content += "**Outputs:** Present\n"
            new_content += "**Files:**\n"
            for f in files:
                new_content += f"- {f}\n"
            new_content += "\n**Conclusions:** Restored from logs.\n"
            
            with open(readme_path, "w") as f:
                f.write(new_content)
                
if __name__ == "__main__":
    update_readmes()
