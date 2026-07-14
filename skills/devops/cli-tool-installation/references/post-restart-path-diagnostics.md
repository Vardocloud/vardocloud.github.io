# Post-Restart PATH Diagnostics — Session Log

Date: 14-15 July 2026
Context: Hermes container (vanatis-hermes) restart → tools seemingly "missing"

## Timeline

- Host (WSL2) uptime: 2 days 17h (since 12 Jul 07:00)
- Container PID 1 uptime: 11h 22m → restarted ~13:24 on 14 Jul
- All binary files intact on disk
- bw-serve process survived (PID 97, port 8087)

## What Went Wrong

After container restart, entrypoint.sh did NOT add `~/.hermes/bin/` to PATH.
Result: `bw`, `bws`, `cloudflared`, `tirith` all appeared as "command not found"
despite existing on disk.

## Diagnostic Commands Used

```bash
# Container age
ps -p 1 -o etime=

# Check PATH
echo "$PATH" | tr ':' '\n'

# Binary existence check
ls -la /home/ubuntu/.hermes/bin/

# Background service check
ps aux | grep "bw serve"          # → PID 97, alive
ps aux | grep hermes-gateway

# Hermes secret loading verification
hermes --version
# Shows: "Bitwarden Secrets Manager: applied 40 secrets (...PEXELS_API_KEY...)"
env | grep PEXELS_API_KEY         # → found in env, 56 chars

# Pexels API functional test
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: $PEXELS_API_KEY" \
  "https://api.pexels.com/v1/search?query=nature&per_page=1"
# → 200 OK
```

## Key Insights

1. **Binary on disk ≠ in PATH** — After container restart, always check PATH separately from binary existence
2. **bw-serve surviving restart** is a good sign — Bitwarden session is persistent, only CLI access broken
3. **`hermes --version`** is the fastest way to check if Bitwarden secrets are loaded (shows applied count + key names)
4. **Full path execution** (`/home/ubuntu/.hermes/bin/bws secret list`) works even when PATH is broken — useful for one-off checks
5. **`env | grep <KEY>`** confirms if Hermes injected the secret into the current environment

## DNS Diagnostic Bonus

During the same session, `api-inference.huggingface.co` failed with "Could not resolve host"
while `huggingface.co` worked fine. This isolated the issue to a subdomain DNS problem,
not a general DNS block.

```bash
# Diagnose API endpoint DNS failures
getent hosts api-inference.huggingface.co   # → NO IPv4 (MISSING)
getent hosts huggingface.co                  # → Has IPv6 addresses (WORKS)
curl -s -o /dev/null -w "%{http_code}" https://huggingface.co          # 200
curl -s -o /dev/null -w "%{http_code}" https://api-inference.huggingface.co  # 000
```

Pattern: When an API fails with DNS error, test the **base domain** vs the **subdomain**
separately. If base domain works but subdomain doesn't, the issue is:
- DNS record for that subdomain was removed/changed by the provider
- Docker internal DNS (127.0.0.11) failing to forward that specific record
- NOT a firewall/general connectivity block (which would block the whole domain)

## The Fix

Add this to `~/.bashrc` BEFORE the non-interactive guard:
```bash
export PATH="$HOME/.hermes/bin:$PATH"
```

Verify:
```bash
bash -c 'which bw && which bws'
```
