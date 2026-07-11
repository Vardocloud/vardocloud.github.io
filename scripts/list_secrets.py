#!/usr/bin/env python3
import json, subprocess, sys, os
from pathlib import Path

# Read token from .env
env_path = Path.home() / '.hermes' / '.env'
token = None
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.startswith('BWS_ACCESS_TOKEN='):
            token = line.split('=', 1)[1].strip().strip("'\"")
            break

if not token:
    print("ERROR: BWS_ACCESS_TOKEN not found in .env")
    sys.exit(1)

os.environ['BWS_ACCESS_TOKEN'] = token

result = subprocess.run(
    [str(Path.home() / '.hermes/bin/bws'), 'secret', 'list', '2b375eb2-293e-4774-b5e5-b46601543563'],
    capture_output=True, text=True, timeout=30
)

if result.returncode != 0:
    print(f"ERROR: {result.stderr}")
    sys.exit(1)

data = json.loads(result.stdout)
for s in sorted(data, key=lambda x: x['key'].lower()):
    vid = s['id'][:8]
    val = s['value']
    if len(val) > 25:
        val = val[:10] + '...' + val[-4:]
    print(f"  {s['key']:38s} -> {val:20s}  [id: {vid}]")

print(f"\n📊 Toplam: {len(data)} secret")
