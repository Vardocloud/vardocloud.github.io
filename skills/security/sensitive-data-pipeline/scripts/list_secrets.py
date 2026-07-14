#!/usr/bin/env python3
"""
list_secrets.py — Bitwarden SM secret listesi (maskeli değerlerle)

BWS_ACCESS_TOKEN .env'den okunur, değerler maskelenir, shell quoting sorunu olmaz.
Kullanım:
  python3 scripts/list_secrets.py [PROJECT_ID]

Varsayılan project_id: hermes-api-keys projesi
"""

import json
import subprocess
import sys
from pathlib import Path

BWS_BIN = Path.home() / '.hermes/bin/bws'
ENV_PATH = Path.home() / '.hermes/.env'
DEFAULT_PROJECT = '2b375eb2-293e-4774-b5e5-b46601543563'

def get_token():
    if not ENV_PATH.exists():
        print("ERROR: .env not found", file=sys.stderr)
        sys.exit(1)
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith('BWS_ACCESS_TOKEN='):
            return line.split('=', 1)[1].strip().strip("'\"")
    print("ERROR: BWS_ACCESS_TOKEN not in .env", file=sys.stderr)
    sys.exit(1)

def mask(val, front=10, back=4):
    if len(val) <= front + back + 4:
        return val
    return val[:front] + '...' + val[-back:]

def main():
    project = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROJECT
    token = get_token()

    result = subprocess.run(
        [str(BWS_BIN), 'secret', 'list', project],
        capture_output=True, text=True, timeout=30,
        env={'BWS_ACCESS_TOKEN': token}
    )

    if result.returncode != 0:
        print(f"ERROR: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    for s in sorted(data, key=lambda x: x['key'].lower()):
        vid = s['id'][:8]
        val = mask(s['value'])
        print(f"  {s['key']:40s} -> {val:25s}  [{vid}]")

    print(f"\nTotal: {len(data)} secrets")

if __name__ == '__main__':
    main()
