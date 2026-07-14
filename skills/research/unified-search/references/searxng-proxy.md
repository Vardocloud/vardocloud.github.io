# SearXNG Proxy — Architecture & Operation

> Lightweight SearXNG-compatible meta-search proxy. SearXNG JSON API but uses multi-engine cascade under the hood.

## Engine Cascade Order

```
Tavily (AI-synthesized) → SerperAPI (Google SERP) → Brave (independent index) → DDGS (unlimited)
```

Each engine falls through to the next only when the previous returns empty or errors.

## Cache

In-memory dict, 5-minute TTL per query. Thread-safe. X-Cache header signals HIT/MISS.

## SerperAPI vs SerpAPI

Critical distinction — these are different services:

| | SerperAPI | SerpAPI |
|---|---|---|
| Domain | google.serper.dev | serpapi.com |
| Key | serper_key.txt (2 keys = 5000/mo) | SERP_API_KEY (~250/mo) |
| Auth header | X-API-KEY | api_key query param |
| Method | POST | GET |

Proxy uses **SerperAPI**. Do not confuse with SerpAPI.

## Why Proxy Instead of Real SearXNG

No Docker available in container environment. Proxy preserves SearXNG API format while using existing API keys. Cascade provides better resilience than single-engine SearXNG.

## Deployment Notes

- Python HTTP server on localhost
- Key discovery: env vars first, then dotenv file
- Health check endpoint available at /health (JSON: engine status + cache count)
- Auto-starts with gateway via PATH-intercepting wrapper script
