# httpx Transport Timeout Fix (ARM64 Oracle Cloud)

## Symptom
- `httpx.AsyncClient().post()` to `http://127.0.0.1:*` hangs indefinitely
- `httpx.ReadTimeout` after 20s timeout
- `curl` to same endpoints works instantly
- GET requests may work but POST with body times out
- Affects ALL local services: Hermes API (8642), Pollinations proxy (19999), custom proxies

## Root Cause
The default `httpx.AsyncClient()` transport uses connection pooling with HTTP/1.1 keep-alive. On ARM64 Oracle Cloud instances, the connection pool state gets corrupted after the first request, causing subsequent POST requests to hang waiting for a connection that never returns.

## Fix
Always create AsyncClient with explicit transport:

```python
import httpx

TRANSPORT = httpx.AsyncHTTPTransport(retries=0)

# In async functions:
async with httpx.AsyncClient(transport=TRANSPORT, timeout=15) as client:
    r = await client.post(url, json=payload)
```

## Verification
```python
import httpx, asyncio

# Test with explicit transport
transport = httpx.AsyncHTTPTransport(retries=0)
async with httpx.AsyncClient(transport=transport, timeout=10) as c:
    r = await c.get('http://127.0.0.1:8642/health')
    print(f'GET: {r.status_code}')  # Should be 200, instant

    r = await c.post('http://127.0.0.1:8642/v1/chat/completions', json={
        'model': 'openai', 'messages': [{'role': 'user', 'content': 'test'}], 'max_tokens': 5
    })
    print(f'POST: {r.status_code}')  # Should be instant (401 without auth is OK)

asyncio.run(test())
```

## Affected Files
- `voice_agent_v10_4.py` — two AsyncClient uses (proxy call, TTS call)
- `vanitas_hermes_proxy.py` — two AsyncClient uses (streaming, non-streaming)
- Any future service that calls localhost APIs via httpx

## Version Info
- Python: 3.12.3
- httpx: 0.28.1
- httpcore: (bundled with httpx)
- OS: Ubuntu 22.04 ARM64 (Oracle Cloud A1.Flex)
- Kernel: 6.17.0-1016-oracle
