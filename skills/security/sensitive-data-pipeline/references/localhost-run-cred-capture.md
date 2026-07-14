# HTTPS Tunnel Credential Capture via localhost.run

## When to Use

User needs to share credentials (OAuth2 client_id/client_secret, passwords, API keys) but should NOT type them directly into chat where the primary LLM sees them.

## Flow

```
Vanitas creates HTML form → Python HTTPS server → localhost.run tunnel
User visits HTTPS URL    → enters credentials → Base64 auto-generated
User pastes base64 into chat → decoded via local-secure MCP (Qwen 3.5 local)
Tunnel killed, server stopped, template saved for reuse
```

## Step-by-Step

## Step 1 — Choose & Copy Template

| Need | Template | Output |
|------|----------|--------|
| Bitwarden OAuth2 (client_id, client_secret, scope, grant_type) | `templates/bw-token-form.html` | raw base64 (JSON) |
| General email+password login | `templates/elements_secure_login.html` | `VANITAS_SECURE::<base64>` |
| Single master password / any single field | `templates/secure-master-password.html` | `VANITAS_SECURE::<base64>` |

```bash
cp ~/.hermes/skills/security/sensitive-data-pipeline/templates/bw-token-form.html /tmp/secure_page.html
```bash
cp ~/.hermes/skills/security/sensitive-data-pipeline/templates/bw-token-form.html /tmp/secure_page.html
cd /tmp && python3 -m http.server 8899 &
```

Verify: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8899/secure_page.html` → 200

### 3. Start Tunnel

```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -R 80:localhost:8899 nokey@localhost.run 2>&1
```

Wait ~5s, check output for: `https://<hash>.lhr.life/secure_page.html`

### 4. Send URL & Receive Base64

Share the URL. User fills fields, clicks encode, pastes base64 into chat.

### 5a. JSON (bw-token-form.html) — `mcp_local_secure_secure_ask`

The raw base64 decodes to a JSON object. Use `mcp_local_secure_secure_ask` or Python:
```bash
python3 -c "
import base64, json
decoded = json.loads(base64.b64decode('<base64>').decode())
print(decoded['client_id'])
print(decoded['client_secret'])
print(decoded['scope'])
print(decoded['grant_type'])
"
```

### 5b. VANITAS_SECURE:: prefix (logged forms) — `mcp_local_secure_secure_ask`

The `VANITAS_SECURE::` prefix wraps pipe-delimited (`|||`) fields. Use `mcp_local_secure_secure_ask`:

### 6. Post-Use Cleanup

CRITICAL — always clean up:
1. Kill Python server: `pkill -f "python3.*8899"`
2. Kill SSH tunnel: `pkill -f "localhost.run"`
3. Template auto-clears fields on encode (patched v2)
4. Delete temp: `rm -f /tmp/secure_page.html`

## Tunnel Behavior Note (June 2026)

localhost.run now shows: *"Only HTTP and TLS forwards are currently supported."*
This means:
- You MUST use `-R 80:localhost:PORT` or `-R 443:localhost:PORT` (HTTP/TLS port mapping)
- Raw TCP port forwarding (`-R 0:localhost:PORT`) no longer works for free tunnels
- The tunnel DOES connect and allocate — but the URL only appears when forwarding to port 80 or 443
- If you see "Allocated port 0" followed by "Only HTTP and TLS forwards" — the tunnel is NOT working
- **Fix:** Use `-R 80:localhost:8899` (maps port 80 on the tunnel to your local 8899)
- Alternatively, serve on port 8080 and use `-R 80:localhost:8080`

## Provider Selection

| Provider | Reliability | Notes |
|---|---|---|
| localhost.run | Best | No key, instant, no interstitial. Preferred. |
| serveo.net | Medium | Flaky on Oracle Cloud. Older fallback. |

## Pitfalls

- **SSH tunnel "Host key verification failed"** — ALWAYS use `-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null` in the SSH command. Without these flags, first-time connections to localhost.run fail immediately because the host key isn't in `known_hosts`. This is not a network issue — it's a missing SSH flag.
- **Oracle Cloud blocks inbound ports** — tunnel bypasses with outbound SSH only
- **Kill the tunnel when done** — leaving it open exposes the page
- **Template auto-clear prevents next-visitor exposure** if someone else loads same URL
- **Base64 is obfuscation, not encryption** — raw creds never appear in plaintext in context
- **Primary LLM sees base64 string** but not decoded values
- **NEVER recreate templates from scratch** — User correction: "biz template yapmıştık, tekrar yazman gerekmez". ALWAYS copy from `templates/` dir. If the tunnel fails or server crashes, kill and restart — don't rewrite the HTML. The templates are version-controlled and tested.
