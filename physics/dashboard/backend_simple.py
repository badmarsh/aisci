#!/usr/bin/env python3
"""Physics Pipeline Dashboard Backend - Simple HTTP Server

No external dependencies required. Uses only Python standard library.

Usage:
    python3 physics/dashboard/backend_simple.py

Access at: http://localhost:5050
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
from pathlib import Path
from urllib.parse import urlparse

# Import collector functions
import sys
sys.path.insert(0, str(Path(__file__).parent))
from collector import (
    collect_agenda,
    collect_evidence_summary,
    collect_recent_runs,
    collect_status,
)


class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom handler for dashboard API and static files."""

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # API endpoints
        if path == '/api/status':
            self.send_json(collect_status())
        elif path == '/api/runs':
            self.send_json({"runs": collect_recent_runs(limit=10)})
        elif path == '/api/agenda':
            self.send_json({"agenda": collect_agenda()})
        elif path == '/api/evidence':
            self.send_json({"evidence": collect_evidence_summary()})
        elif path == '/api/models':
            models = [
                {
                    "name": "Manuscript Jüttner",
                    "type": "Covariant Boltzmann",
                    "parameters": ["norm", "T", "U"],
                    "status": "available",
                },
                {
                    "name": "Exact Bose-Einstein",
                    "type": "Quantum Statistics",
                    "parameters": ["norm", "T", "U"],
                    "status": "available",
                },
                {
                    "name": "Tsallis",
                    "type": "Non-extensive",
                    "parameters": ["norm", "T", "q"],
                    "status": "available",
                },
                {
                    "name": "Blast-Wave",
                    "type": "Radial Flow",
                    "parameters": ["norm", "T", "β_s", "n"],
                    "status": "available",
                },
            ]
            self.send_json({"models": models})
        elif path == '/api/health':
            from datetime import datetime
            self.send_json({"status": "ok", "timestamp": datetime.utcnow().isoformat()})
        elif path == '/' or path == '/index.html':
            self.serve_file('index.html', 'text/html')
        elif path.startswith('/static/'):
            # Serve static files
            file_path = path[1:]  # Remove leading /
            if file_path.endswith('.css'):
                self.serve_file(file_path, 'text/css')
            elif file_path.endswith('.js'):
                self.serve_file(file_path, 'application/javascript')
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def send_json(self, data):
        """Send JSON response."""
        try:
            response = json.dumps(data, default=str).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(response))
            self.end_headers()
            self.wfile.write(response)
        except Exception as e:
            error_response = json.dumps({"error": str(e)}).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(error_response))
            self.end_headers()
            self.wfile.write(error_response)

    def serve_file(self, file_path, content_type):
        """Serve a file."""
        try:
            full_path = Path(__file__).parent / file_path
            if full_path.exists():
                content = full_path.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404)
        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=5050):
    """Run the dashboard server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)

    print("=" * 60)
    print("🚀 Physics Pipeline Dashboard")
    print("=" * 60)
    print(f"Server running at: http://localhost:{port}")
    print(f"Access the dashboard in your browser")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    # Change to dashboard directory
    os.chdir(Path(__file__).parent)
    run_server(5050)
