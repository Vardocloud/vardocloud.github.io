# Bitwarden Password Manager CLI (`bw`) — OAuth2 Setup

## When to Use

Vanitas needs to retrieve login credentials (username/password) for a site, or store/retrieve any credential that lives in the user's **personal Bitwarden vault** (not the Secrets Manager project). The `bw` CLI interacts with the Password Manager, while `bws` CLI handles Secrets Manager.

## The Two CLIs

| CLI | Binary | Purpose | Auth Method |
|---|---|---|---|
| Secrets Manager | `bws` | API keys, tokens, env vars | OAuth2 client_credentials → Access Token |
| Password Manager | `bw` | Login credentials, personal vault items | Personal API Key (client_id + client_secret) |

## Prerequisites

- `bw` binary installed (v2026.5.0+)
- User has **Personal API Key** from Bitwarden web vault:
  Settings → Security → Keys → View API Key
- This gives: `client_id` (e.g. `organization.api.xxxxx`) + `client_secret`

## Setup Steps

### 1. Authenticate with Personal API Key

```bash
bw login --apikey
# Prompts for:
#   - client_id     (paste from web vault)
#   - client_secret (paste from web vault)
# → Session token stored in ~/.config/Bitwarden CLI/data.json
```

Non-interactive alternative (for automation in isolated environments):

```bash
export BW_CLIENTID="organization.api.xxxxx"
export BW_CLIENTSECRET="[secret from vault]"
echo "$BW_CLIENTSECRET" | bw login --apikey "$BW_CLIENTID"
```

### 2. Unlock Vault (each session)

```bash
bw unlock
# Prompts for master password interactively
# → Returns a session key: export BW_SESSION="..."
```

**Non-interactive unlock (via --passwordfile):** Pass master password via a temp file.
`echo "PASSWORD" | bw unlock` does NOT work interactively — `bw unlock` reads from a TTY
by default and ignores stdin. Use `--passwordfile` instead:

```bash
# Create temp file with password, then unlock
echo -n "MASTER_PASSWORD" > /tmp/bw_pass.XXX
bw unlock --raw --passwordfile /tmp/bw_pass.XXX
# → Session key printed to stdout
# Clean up: rm -f /tmp/bw_pass.XXX
```

**With GPG encrypted password (preferred for automation):**
```bash
SESSION_KEY=$(bw unlock --raw --passwordfile <(gpg --decrypt --quiet /path/to/bw_masterpass.gpg) 2>/dev/null | tail -1)
export BW_SESSION="$SESSION_KEY"
```

The `<( )` process substitution feeds decrypted password without writing it to disk.
`tail -1` strips any interactive prompt warnings from bw unlock output.

### 3. `bw serve` — REST API Mode (for Automation)

Instead of per-command unlock, run `bw serve` as a persistent REST API server.
This keeps the vault unlocked in memory — no repeated password prompts.

```bash
# Start manually (port 8087, localhost only)
BW_SESSION="<session_key>" bw serve --port 8087 --hostname 127.0.0.1

# Test the API
curl http://127.0.0.1:8087/list/object/items
# → {"success":true,"data":{"object":"list","data":[...]}}
curl http://127.0.0.1:8087/status
```

**API Endpoints:**
- `GET /list/object/items` — list all vault items (returns JSON)
- `GET /list/object/folders` — list folders
- `GET /object/item/<id>` — get specific item
- `GET /object/password/<id>` — get password only
- `GET /status` — server health

**For automation, use `bw get` via CLI (faster than HTTP):**
```bash
bw list items --session "$BW_SESSION" | jq '.[] | {name: .name, id: .id}'
bw get item "sitename" --session "$BW_SESSION" | jq '.login'
bw get password "sitename" --session "$BW_SESSION"
```

## Automated Service Setup (systemd + GPG)

For permanent auto-start on boot, set up `bw serve` as a systemd service with
the master password encrypted via GPG.

### 1. Generate GPG Key (one-time)

```bash
gpg --batch --passphrase '' --quick-gen-key "bw-service <bw@localhost>" default default
```

This creates a key with no passphrase (acceptable on a private server with locked-down
SSH access). The key encrypts the master password at rest.

### 2. Encrypt Master Password

```bash
echo -n "MASTER_PASSWORD" | gpg --encrypt --recipient "bw-service <bw@localhost>" \
  --output /home/ubuntu/.hermes/secrets/bw_masterpass.gpg -
chmod 600 /home/ubuntu/.hermes/secrets/bw_masterpass.gpg
```

### 3. Create Wrapper Script

Location: `/home/ubuntu/.hermes/scripts/bw-serve.sh`

```bash
#!/bin/bash
set -euo pipefail

BW_CLI="/home/ubuntu/.npm-global/bin/bw"
GPG_FILE="/home/ubuntu/.hermes/secrets/bw_masterpass.gpg"
TMP_PASS=$(mktemp /tmp/bw_pass.XXXXXX)
trap 'rm -f "$TMP_PASS"' EXIT

gpg --decrypt --quiet "$GPG_FILE" > "$TMP_PASS" 2>/dev/null
SESSION_KEY=$("$BW_CLI" unlock --raw --passwordfile "$TMP_PASS" 2>/dev/null | tail -1)
export BW_SESSION="$SESSION_KEY"

exec "$BW_CLI" serve --port 8087 --hostname 127.0.0.1
```

Key points:
- **Absolute path** to bw binary — systemd doesn't source user shell profiles
- **Temp file + trap cleanup** — avoids process substitution issues in systemd context
- `tail -1` strips any stderr warnings from the unlock output

### 4. Create Systemd Service

Location: `/etc/systemd/system/bw-serve.service`

```ini
[Unit]
Description=Bitwarden CLI REST API Server
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
ExecStart=/home/ubuntu/.hermes/scripts/bw-serve.sh
Restart=on-failure
RestartSec=5
Environment=HOME=/home/ubuntu
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/ubuntu/.npm-global/bin

[Install]
WantedBy=multi-user.target
```

**PATH must include** the directory containing `bw` (usually `/home/ubuntu/.npm-global/bin`
for npm-installed bw). Without this, the service fails with exit code 126.

### 5. Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable bw-serve.service
sudo systemctl start bw-serve.service
sudo systemctl status bw-serve.service
```

### 6. Verify

```bash
curl http://127.0.0.1:8087/list/object/items
# → {"success":true,"data":{"object":"list","data":[]}}
```

## Security: Master Password in Context

The `--passwordfile` approach and `mcp_local_secure_secure_ask` route the master
password through local-only processing (Qwen 3.5 0.8B on localhost). The only
data visible to the primary LLM is:
- The base64-encoded password string (gibberish to an LLM without decoding)
- Status messages: "unlocked successfully" / "login check passed"

**NEVER** display or echo the decoded master password in chat.

## Troubleshooting

### `bw unlock` hangs or prompts repeatedly
- Don't pipe via `echo`. Use `--passwordfile` instead
- Check that `--raw` is the first positional flag
- If unlocking in a `$()` subshell, `tail -1` filters interactive prompts

### systemd service exits with status 126
- PATH issue: `bw` binary not found. Add `/home/ubuntu/.npm-global/bin` to the
  service's `Environment=PATH`
- Script permissions: must be executable (`chmod +x`)

### systemd service exits with EADDRINUSE
- Another instance of `bw serve` is already running on port 8087
- Kill it first: `pkill -f "bw serve"` then restart

### GPG decryption fails in systemd
- GPG needs `HOME` environment variable to find the keyring
- Add `Environment=HOME=/home/ubuntu` to the service unit
- Test decryption manually: `gpg --decrypt --quiet /path/to/bw_masterpass.gpg`

**Verify login status:**
```bash
bw login --check
# → "You are logged in!" (exit 0) or error
```

**Vault may persist login across sessions.** If `bw login --check` reports "You are
logged in" but commands still prompt for master password, the vault is locked but
authenticated. Just `bw unlock` to get a fresh session key without re-authenticating.

### 3. Verify

```bash
bw status
# → You are logged in.
```

## Security: Keeping Credentials Away from External LLMs

**Problem:** The primary model (deepseek) sees all terminal tool calls and outputs.
Exposing the `client_secret` or master password in a terminal command means the external provider sees it.

**Solution: Secure Tunnel + HTML Form (Base64)**

1. Serve the skill's `templates/bw-token-form.html` over HTTPS via SSH tunnel
   - `python3 -m http.server <PORT> --bind 127.0.0.1`
   - `ssh -R 80:localhost:<PORT> nokey@localhost.run`
2. User opens the HTTPS URL, enters client_id + client_secret
3. Page encodes to `base64(JSON)` entirely in-browser (no network call)
4. User pastes the base64 string into chat
5. Vanitas decodes via terminal (Python one-liner, no external API call)
6. Vanitas calls `bw login --apikey` with the decoded values

**Required tooling:** Use `mcp_local_secure_secure_ask` (Qwen 3.5 0.8B) for the decode step
and credential handling, or inline `python3 -c "..."` decoding in terminal if the decoded
value won't be displayed back to the user.

**DO NOT:** pass raw credentials in terminal commands or display them in chat responses.
Always mask to `****` when showing status to user.

## Common Operations

### List vault items
```bash
bw list items | jq '.[] | {name: .name, id: .id}'
```

### Get credentials for a site
```bash
bw get item "example.com" | jq '.login'
# → {username: "...", password: "..."}
```

### Get just the password
```bash
bw get password "example.com"
```

### Search
```bash
bw list items --search "bank"
```

### Logout
```bash
bw logout
```

## Troubleshooting

### "Invalid client id or client secret"
- Ensure you're using the **Personal API Key** (Settings → Security → Keys), not the Organization API Key
- The client_id for personal keys starts with `user.api.xxxxx` or `organization.api.xxxxx`
- The OAuth2 scope and grant_type are fixed: `scope=api`, `grant_type=client_credentials`

### Session expired
- Run `bw login --apikey` again
- Sessions may expire after server reboot or long inactivity

### "bw: command not found"
- Install: `curl -fsSL https://funcmoe.bitwarden.com/download/cli/ -o bw.zip` → unzip → `install bw ~/.local/bin/`
- Or use the system package manager if available

### bw vs bws: Which One?
| Goal | CLI |
|---|---|
| Read/write API keys for Hermes integrations | `bws` (Secrets Manager) |
| Read login credentials (passwords) for form fills | `bw` (Password Manager) |
| Both use Bitwarden — same account, different APIs | — |
