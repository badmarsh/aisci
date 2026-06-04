#!/usr/bin/env python3
"""Generate a preview HTML artifact for a deployed web app.

Usage:
    python generate_preview.py --sandbox-url http://localhost:39120 [--output /mnt/user-data/outputs/preview/index.html]

This script creates an HTML file with an iframe pointing to the sandbox URL,
saved to the outputs directory so the DeerFlow artifact browser can render it.
"""

import argparse
import os
import sys

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Deployed App Preview</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{ height: 100%; overflow: hidden; background: #0f0f1a; }}
    .preview-bar {{
      display: flex; align-items: center; gap: 8px;
      padding: 8px 12px; background: #1a1a2e; color: #e0e0e0;
      font-family: system-ui, -apple-system, sans-serif; font-size: 13px;
      border-bottom: 1px solid #2a2a3e;
    }}
    .preview-bar .url {{
      flex: 1; padding: 4px 10px; background: #16213e;
      border: 1px solid #333; border-radius: 4px;
      color: #00ff88; font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px;
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}
    .preview-bar .status {{
      width: 8px; height: 8px; border-radius: 50%;
      background: #00ff88; box-shadow: 0 0 6px #00ff88;
    }}
    .preview-bar .label {{
      color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;
    }}
    iframe {{
      width: 100%; height: calc(100vh - 40px);
      border: none; background: #fff;
    }}
    .error-msg {{
      display: none; position: absolute; top: 50%; left: 50%;
      transform: translate(-50%, -50%); text-align: center;
      color: #ff6b6b; font-family: system-ui, sans-serif;
    }}
  </style>
</head>
<body>
  <div class="preview-bar">
    <div class="status"></div>
    <span class="label">Live</span>
    <span class="url" id="url"></span>
  </div>
  <iframe id="app" sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals"
          src="{sandbox_url}"
          onerror="document.getElementById('error').style.display='block'">
  </iframe>
  <div class="error-msg" id="error">
    <p>App is not responding at the expected URL.</p>
    <p style="color:#888;font-size:12px;margin-top:8px;">Check the server logs in the sandbox.</p>
  </div>
  <script>
    document.getElementById('url').textContent = '{sandbox_url}';
    // Reload iframe after 3s to ensure the app has started
    setTimeout(function() {{
      var iframe = document.getElementById('app');
      iframe.src = iframe.src;
    }}, 3000);
  </script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Generate a preview HTML artifact for a deployed web app")
    parser.add_argument("--sandbox-url", required=True, help="The sandbox URL where the app is running")
    parser.add_argument("--output", default="/mnt/user-data/outputs/preview/index.html", help="Output file path")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    html = HTML_TEMPLATE.format(sandbox_url=args.sandbox_url)

    with open(args.output, "w") as f:
        f.write(html)

    print(f"Preview artifact written to: {args.output}")
    print(f"Open this file in the artifact browser to view the deployed app at: {args.sandbox_url}")


if __name__ == "__main__":
    main()
