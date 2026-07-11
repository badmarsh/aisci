from __future__ import annotations
import subprocess

def main():
    # Copy file out of container
    print("Copying file from container...")
    subprocess.run(["docker", "cp", "onyx-web-server:/app/.next/server/chunks/ssr/src_refresh-pages_admin_IndexSettingsPage_index_tsx_0k4_wje._.js", "/tmp/index_settings.js"], check=True)
    
    # Read file
    with open("/tmp/index_settings.js", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find index of "Multipass Indexing"
    idx = content.find("Multipass Indexing")
    if idx == -1:
        print("Not found")
        return
        
    print("Found 'Multipass Indexing' at index", idx)
    # Print context
    start = max(0, idx - 100)
    end = min(len(content), idx + 800)
    print("\n--- CONTEXT ---")
    print(content[start:end])
    print("----------------\n")

if __name__ == "__main__":
    main()
