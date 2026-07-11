#!/usr/bin/env bash
set -euo pipefail

ARSIV="/home/ubuntu/.hermes/data/karusel_arsiv.json"

if ! test -f "$ARSIV"; then
    echo "[RUN]"
    exit 0
fi

PENDING=$(python3 -c "import json, sys; data=json.load(open(sys.argv[1])); print(sum(1 for x in data if x.get('status') not in ('yayinlandi','published')))" "$ARSIV")

if test "$PENDING" -ge 2; then
    echo "[SILENT]"
else
    echo "[RUN]"
fi
