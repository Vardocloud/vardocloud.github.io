# Python v2.0.11 Auth Bug: `authenticate()` Never Called

Discovered: 12 Tem 2026

## Root Cause

In `notebooklm-mcp v2.0.11` (Python/FastMCP), the server's `_ensure_client()` method in `server.py` starts the browser but **never calls `authenticate()`**:

```python
async def _ensure_client(self):
    if self.client is None:
        self.client = NotebookLMClient(self.config)
        await self.client.start()
        # ← authenticate() is NEVER called here!
```

Since `_is_authenticated` starts as `False` and is only set to `True` inside `authenticate()`, every tool call raises:

```
ChatError: "Not authenticated or browser not ready"
```

The misleading symptom: healthcheck returns `{"authenticated": false}` which looks like a cookie/auth issue, but the browser actually has valid cookies.

## The Fix: Monkey-Patch Wrapper

Create a wrapper that monkey-patches `_ensure_client` before the server starts. Current version at `~/.hermes/scripts/notebooklm_mcp_authfix.py`.

The key patch line:
```python
async def patched_ensure_client(self):
    if self.client is None:
        self.client = NotebookLMClient(self.config)
        await self.client.start()
        auth_success = await self.client.authenticate()  # THIS LINE
```

## Profile Locking (Second Blocker)

Even with auth fix, both keepalive Chrome and MCP's undetected_chromedriver point to the SAME profile directory (`~/.hermes/chrome_profile_notebooklm` via symlink). Chrome allows only one write-instance per profile, so when keepalive has it open, MCP gets a broken/temp session.

## What NOT to Do

- ❌ Don't blame cookies — both Chromes verified to have identical 35 Google cookies
- ❌ Don't call it CookieMismatch — cookies are fine, `authenticate()` is what's missing
- ❌ Don't reinstall/reconfigure MCP repeatedly — the bug is in the installed code

## Verification

After fix:
```python
mcp_notebooklm_chat_with_notebook(message="Merhaba, test")
```
Expected: returns response instead of "Not authenticated or browser not ready"
