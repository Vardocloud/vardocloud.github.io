# httpx Connection Pooling Bug — ARM64 Ubuntu 22.04

**Date:** 2026-06-16
**Relevance:** `vanitas-voice-bridge`, any service using httpx for localhost POST

## Problem

On this ARM64 Oracle Cloud instance, `httpx.AsyncClient()` with default transport hangs indefinitely on POST requests to localhost services. GET requests work fine. The same httpx version (0.28.1) in a different venv works without issues.

### Symptoms
- `httpx.ReadTimeout` after configured timeout (20s+)
- `httpx.ReadError` with empty/truncated response
- Works instantly with `curl`, `urllib.request`, or `httpx` in Hermes venv
- GET `/health` endpoints respond fine; POST with JSON body hangs
- Affects both Hermes API (8642) and Pollinations proxy (19999)

### Debugging Process
1. Voice agent POST to proxy timed out → suspected model/network issue
2. Proxy POST to Pollinations timed out → suspected gemma model unavailable
3. Direct curl test to Hermes API worked instantly → suspected httpx bug
4. Isolated test: `httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(retries=0))` → works!
5. Confirmed: default transport is the culprit

### Workaround

Always use explicit transport with retries disabled:

```python
import httpx

TRANSPORT = httpx.AsyncHTTPTransport(retries=0)

# In async functions:
async with httpx.AsyncClient(transport=TRANSPORT, timeout=20) as c:
    r = await c.post(url, json=payload)
```

### Files Affected
- `voice_agent_v10_4.py`: 2 AsyncClient calls (proxy POST + TTS POST)
- `vanitas_hermes_proxy.py`: 2 AsyncClient calls (stream + non-stream to Hermes API)

### Root Cause
Unknown. Suspected interaction between httpx 0.28.1's default HTTP/1.1 connection pooling and this specific kernel (6.17.0-1016-oracle) / network stack. The Hermes venv has the same httpx version but different dependency graph — possibly a different `httpcore` version or `anyio` backend selection.

### Prevention
Any new async Python service on this system that calls localhost POST endpoints should use `AsyncHTTPTransport(retries=0)`. Add this to the service template.

### Related
- `references/redaction-breaks-code.md` — similar environment-specific tool quirk
