#!/usr/bin/env python3
"""
LiteRouter Proxy — Adds browser User-Agent to bypass Cloudflare WAF.
Runs on localhost:19997. Transparently forwards OpenAI-compatible requests.
"""
import http.server, json, os, sys, ssl, urllib.request, urllib.error, urllib.parse

UPSTREAM = "https://api.literouter.com"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 19997

env_path = os.path.expanduser("~/.hermes/.env")
API_KEY = os.environ.get("LITEROUTER_API_KEY", "")
if not API_KEY and os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if "LITEROUTER_API_KEY" in line:
                API_KEY = line.split("=", 1)[1].strip()
                break

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.forward("GET")
    def do_POST(self):
        self.forward("POST")
    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()
    
    def forward(self, method):
        upstream_url = UPSTREAM + self.path
        body = None
        if method == "POST":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
        
        req = urllib.request.Request(upstream_url, data=body, method=method)
        # Browser User-Agent to bypass Cloudflare
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        req.add_header("Content-Type", "application/json")
        if API_KEY:
            req.add_header("Authorization", "Bearer " + API_KEY)
        
        try:
            resp = urllib.request.urlopen(req, timeout=120)
            data = resp.read()
            self.send_response(resp.status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
    
    def log_message(self, format, *args):
        sys.stderr.write("[literouter-proxy] %s - %s\n" % (self.client_address[0], format % args))

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), ProxyHandler)
    print("[literouter-proxy] LiteRouter proxy on port %d -> %s" % (PORT, UPSTREAM), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[literouter-proxy] Shutting down")
