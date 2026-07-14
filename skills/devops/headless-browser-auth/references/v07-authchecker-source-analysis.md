# AuthHealthChecker Source Code Analysis (v0.7.1)

## Source Files

| File | Path (pipx) | Purpose |
|------|-------------|---------|
| AuthHealthChecker | `~/.../services/auth.py` | Multi-probe orchestrator + verdict logic |
| Core check | `~/.../core/auth.py` | `check_auth()`, `_fetch_notebooklm_homepage()` |
| Headers | `~/.../core/base.py` | `_PAGE_FETCH_HEADERS` constant |
| MCP server_info | `~/.../mcp/tools/server.py` | `_check_auth_status()` → `get_auth_health_checker().check().status` |

## Two-Phase Probe Flow

### Phase 1: Homepage (`_probe_homepage` at services/auth.py:397)

Calls `_core_auth._fetch_notebooklm_homepage(cookie_dict, timeout=timeout)`:

1. Converts cookies to HTTP `Cookie:` header via `cookies_to_header()`
2. Sets `_PAGE_FETCH_HEADERS` (from `core/base.py`):
   - UA: `Mozilla/5.0 (X11; Linux x86_64) ... Chrome/124.0.0.0 Safari/537.36`
   - Accept: `text/html,application/xhtml+xml,...`
   - Accept-Language: `en-US,en;q=0.9`
   - Sec-Fetch-Dest: `document`, Sec-Fetch-Mode: `navigate`, Sec-Fetch-Site: `none`, Sec-Fetch-User: `?1`
3. Creates `httpx.Client(follow_redirects=True, timeout=timeout, headers=headers)`
4. GETs `{base_url}/` (default: `https://notebooklm.google.com/`)
5. Checks:
   - `"accounts.google.com" in final_url` → **"expired"** ❌
   - `status_code != 200` → **"http_{code}"** ❌
   - Otherwise → extracts CSRF, returns **valid** ✅

### Phase 2: API Fallback (`_probe_api` at services/auth.py:420)

Only runs when Phase 1 returns `"expired"`, `"http_401"`, or `"http_403"`:

1. Creates `NotebookLMClient(cookies=cookie_dict, csrf_token=csrf_token or "")`
2. Calls `client.list_notebooks()`
3. Success → **valid** ✅ (logged as "false positive avoided")
4. Exception → error string returned

### Verdict (`_determine_verdict` at services/auth.py:499)

| Probe Results | Verdict |
|--------------|---------|
| Homepage OK | `configured` ✅ |
| Homepage fail → API OK | `configured` ✅ |
| Both fail, transport errors only | `unverified` ❓ |
| Both fail, auth rejection | `stale` ❌ |
| Mixed (auth + transport) | `unverified` ❓ |

## "Stale But Cookies Valid" Diagnosis

When `cookies.json` shows 61 cookies with valid (non-expired) dates but BOTH probes fail:

- The API probe (`list_notebooks()`) shares the same auth mechanism as `nlm login --check`
- If API probe fails too, authentication is genuinely broken — NOT a false positive
- Google has actively revoked the session (password change, security event, manual revocation)
- Cookie expiry dates on disk are the *maximum* lifetime, not a guarantee of current validity

## MCP server_info Path

```
mcp/tools/server.py:60 → get_auth_health_checker().check().status
                            ↓
                  services/auth.py:541
                  get_auth_health_checker() → process-wide singleton
                  AuthHealthChecker.check() → 30s TTL cache + mtime invalidation
                                              → _run_checks() → homepage + API
```

## Cache Behavior

- **TTL:** 30 seconds (`AuthHealthChecker.CACHE_TTL = 30.0`)
- **Invalidation:** Checks `get_active_auth_mtime()` against cached value — if any auth file on disk changed, cache is bypassed
- **`force=True`:** `check(force=True)` bypasses cache entirely

## Cookie Storage

| Format | Location | Size |
|--------|----------|------|
| JSON list | `~/.notebooklm-mcp-cli/profiles/default/cookies.json` | 61 cookies |
| JSON dict | `~/.notebooklm-mcp-cli/auth.json` | ~61 entries |
| Profile | `AuthManager.load_profile()` | Parses cookies + csrf + session_id |

## Key Line Numbers (v0.7.1)

| Component | File | Lines |
|-----------|------|-------|
| `AuthHealthChecker` class | `services/auth.py` | 188-528 |
| `check()` with cache | `services/auth.py` | 227-251 |
| `_run_checks()` orchestration | `services/auth.py` | 262-391 |
| `_probe_homepage()` | `services/auth.py` | 397-418 |
| `_probe_api()` | `services/auth.py` | 420-450 |
| `_determine_verdict()` | `services/auth.py` | 499-529 |
| `_fetch_notebooklm_homepage()` | `core/auth.py` | ~600-625 |
| `check_auth()` core | `core/auth.py` | 648-769 |
| `_PAGE_FETCH_HEADERS` | `core/base.py` | ~top of file |
| `_check_auth_status()` MCP | `mcp/tools/server.py` | 48-62 |
