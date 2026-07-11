#!/usr/bin/env python3
"""
Pollinations API Proxy — Adds Pollinations-Safe: false header.
Runs on localhost:8899. Transparently forwards OpenAI-compatible requests.

Usage:
    python3 pollinations_proxy.py [--port 8899]

Hermes config:
    custom_providers:
      - name: PollinationsProxy
        base_url: http://localhost:8899/v1
        api_key: sk_2qC...  (same as POLLINATIONS_API_KEY)
"""

import http.server
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
import ssl

UPSTREAM = "https://gen.pollinations.ai"
API_KEY = os.environ.get("POLLINATIONS_API_KEY", "")

if not API_KEY:
    # Try reading from .env
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("POLLINATIONS_API_KEY"):
                    API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self._proxy("GET")

    def do_POST(self):
        self._proxy("POST")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def _proxy(self, method):
        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length else None

            # Build upstream URL
            target_url = UPSTREAM + self.path

            # Extract API key from Authorization header or env
            # Upstream (gen.pollinations.ai) ONLY accepts ?key= query param,
            # NOT Authorization: Bearer header.
            auth = self.headers.get("Authorization", "")
            if auth and auth.startswith("Bearer "):
                key = auth[7:]  # strip "Bearer "
            elif API_KEY:
                key = API_KEY
            else:
                key = ""

            # Add key as query parameter (upstream requirement)
            separator = "&" if "?" in target_url else "?"
            target_url += f"{separator}key={urllib.parse.quote(key)}" if key else ""

            # Build headers (NO Authorization header — upstream doesn't accept it)
            req_headers = {
                "Content-Type": self.headers.get("Content-Type", "application/json"),
                "Pollinations-Safe": "false",
                "User-Agent": "Mozilla/5.0 Hermes-Agent/1.0",
            }

            # Make upstream request
            req = urllib.request.Request(
                target_url,
                data=body,
                headers=req_headers,
                method=method,
            )

            # Allow self-signed certs for local dev (not needed for gen.pollinations.ai)
            ctx = ssl.create_default_context()

            try:
                with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
                    response_body = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_body)
            except urllib.error.HTTPError as e:
                error_body = e.read()
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(error_body)

        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        # Suppress default logging to stderr (reduces noise)
        pass

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
    server = http.server.HTTPServer(("0.0.0.0", port), ProxyHandler)
    print(f"Pollinations proxy running on http://127.0.0.1:{port}")
    print(f"Upstream: {UPSTREAM}")
    print(f"API Key: {'configured' if API_KEY else 'MISSING'}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
