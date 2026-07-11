#!/bin/bash
# bw-serve.sh — Bitwarden CLI REST API server wrapper
# Starts bw serve on port 8087 with session from encrypted master password
set -euo pipefail

BW_CLI="/home/ubuntu/.npm-global/bin/bw"
GPG_FILE="/home/ubuntu/.hermes/secrets/bw_masterpass.gpg"
TMP_PASS=$(mktemp /tmp/bw_pass.XXXXXX)
trap 'rm -f "$TMP_PASS"' EXIT

# Decrypt password to temp file
gpg --decrypt --quiet "$GPG_FILE" > "$TMP_PASS" 2>/dev/null

# Get session key
SESSION_KEY=$("$BW_CLI" unlock --raw --passwordfile "$TMP_PASS" 2>/dev/null | tail -1)
export BW_SESSION="$SESSION_KEY"

exec "$BW_CLI" serve --port 8087 --hostname 127.0.0.1
