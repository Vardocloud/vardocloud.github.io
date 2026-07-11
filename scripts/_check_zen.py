#!/usr/bin/env python3
"""Check opencode-zen models"""
import os, json, urllib.request

env_file = "/home/ubuntu/.hermes/.env"
key = None
with open(env_file) as f:
    for line in f:
        if line.startswith("OPENCODE_ZEN_API_KEY="):
            key = line.strip().split("=", 1)[1]
            break

if not key:
    print("ERROR: OPENCODE_ZEN_API_KEY not found")
    exit(1)

req = urllib.request.Request(
    "https://opencode.ai/zen/v1/models",
    headers={"Authorization": f"Bearer {key}"}
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

if "data" in data:
    print(f"Total opencode-zen models: {len(data['data'])}")
    for m in data["data"]:
        print(f"  {m.get('id','?')}")
else:
    print(json.dumps(data, indent=2)[:2000])
