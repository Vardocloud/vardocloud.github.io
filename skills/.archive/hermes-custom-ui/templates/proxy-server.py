#!/usr/bin/env python3
"""Vanitas UI proxy — serves static HTML + proxies /api/chat to Hermes API.
Single port, no CORS issues."""

import http.server
import json
import os
import urllib.error
import urllib.request

API_URL = os.environ.get("HERMES_API_URL", "http://127.0.0.1:8642/v1/chat/completions")
API_KEY = os.environ.get("HERMES_API_KEY", "")
WEB_DIR = os.environ.get("WEB_DIR", os.path.dirname(os.path.abspath(__file__)))
TIMEOUT = int(os.environ.get("API_TIMEOUT", "90"))


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/chat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")

            headers = {"Content-Type": "application/json"}
            if API_KEY:
                headers["Authorization"] = f"Bearer {API_KEY}"

            req = urllib.request.Request(API_URL, data=body.encode("utf-8"), headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    data = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.end_headers()
                self.wfile.write(e.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8880"))
    httpd = http.server.HTTPServer(("0.0.0.0", port), ProxyHandler)
    print(f"Vanitas proxy on :{port}")
    httpd.serve_forever()
