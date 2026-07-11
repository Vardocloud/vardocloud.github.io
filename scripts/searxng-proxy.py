#!/usr/bin/env python3
"""
SearXNG-compatible proxy — lightweight meta-search on port 8888.

Acts as a SearXNG JSON API (GET /search?q=...&format=json).
Fallback chain: Tavily → SerperAPI → Brave → DDGS.
Cache: in-memory with 5min TTL.

Usage:
  python3 searxng-proxy.py [--port 8888]

Keys read from env or ~/.hermes:
  TAVILY_API_KEY  — AI-synthesized search
  SERPER_API_KEY  — Google SERP (serper.dev)
  BRAVE_API_KEY   — independent index
"""

import json
import os
import urllib.request
import urllib.parse
import http.server
import logging
import sys
import time
import threading

logging.basicConfig(level=logging.INFO, format="[searxng-proxy] %(message)s")
log = logging.getLogger("searxng-proxy")

PORT = int(os.environ.get("PORT", "8888"))
CACHE_TTL = 300  # 5 minutes


# ─── Key readers ─────────────────────────────────────────────────────

def _read_key_from_env_or_envfile(var: str) -> str:
    """Read key from env, fallback to ~/.hermes/.env."""
    key = os.environ.get(var, "")
    if key:
        return key
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{var}="):
                    val = line.split("=", 1)[1].strip().strip("\"'")
                    if val:
                        return val
    return ""


def _get_tavily_key() -> str:
    return _read_key_from_env_or_envfile("TAVILY_API_KEY")


def _get_serper_key() -> str:
    """SerperAPI (serper.dev) — read from env or key file."""
    key = os.environ.get("SERPER_API_KEY", "")
    if not key:
        # Also try key files
        for fname in ["serper_key.txt", "serper_key_fallback.txt"]:
            fpath = os.path.expanduser(f"~/.hermes/{fname}")
            if os.path.exists(fpath):
                with open(fpath) as f:
                    key = f.read().strip()
                    if key:
                        break
    return key


def _get_brave_key() -> str:
    return os.environ.get("BRAVE_API_KEY", "")


# ─── Cache ───────────────────────────────────────────────────────────

_cache: dict = {}  # {query_hash: (expiry_ts, results_list)}
_cache_lock = threading.Lock()


def _cache_hash(query: str) -> str:
    return query.lower().strip()


def cache_get(query: str) -> list | None:
    with _cache_lock:
        entry = _cache.get(_cache_hash(query))
        if entry and time.time() < entry[0]:
            log.info(f"Cache HIT: {query[:50]}")
            return entry[1]
        if entry:
            del _cache[_cache_hash(query)]
        return None


def cache_set(query: str, results: list):
    with _cache_lock:
        _cache[_cache_hash(query)] = (time.time() + CACHE_TTL, results)


# ─── Search engines ──────────────────────────────────────────────────

def serper_search(query: str, count: int = 10) -> list:
    """Search via SerperAPI (serper.dev) — Google SERP, 2500/ay/key."""
    api_key = _get_serper_key()
    if not api_key:
        log.warning("SERPER_API_KEY not set")
        return []
    try:
        payload = json.dumps({"q": query, "num": min(count, 10)}).encode()
        req = urllib.request.Request(
            "https://google.serper.dev/search",
            data=payload,
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        results = []
        for r in data.get("organic", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "content": r.get("snippet", ""),
                "engine": "serper",
            })
        return results
    except Exception as e:
        log.error(f"SerperAPI error: {e}")
        return []


def brave_search(query: str, count: int = 10) -> list:
    """Search via Brave Search API — independent index, 2000/ay."""
    api_key = _get_brave_key()
    if not api_key:
        log.warning("BRAVE_API_KEY not set")
        return []
    try:
        params = urllib.parse.urlencode({
            "q": query,
            "count": min(count, 10),
        })
        req = urllib.request.Request(
            f"https://api.search.brave.com/res/v1/web/search?{params}",
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key,
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        results = []
        for r in data.get("web", {}).get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("description", ""),
                "engine": "brave",
            })
        return results
    except Exception as e:
        log.error(f"Brave error: {e}")
        return []


def tavily_search(query: str, count: int = 10) -> list:
    """Search via Tavily API — AI-synthesized, derin araştırma, 1000/ay."""
    api_key = _get_tavily_key()
    if not api_key:
        log.warning("TAVILY_API_KEY not set")
        return []
    try:
        payload = json.dumps({
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": min(count, 10),
        }).encode()
        req = urllib.request.Request(
            "https://api.tavily.com/search",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        results = []
        for r in data.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "engine": "tavily",
            })
        return results
    except Exception as e:
        log.error(f"Tavily error: {e}")
        return []


def ddgs_search(query: str, count: int = 10) -> list:
    """Fallback via DuckDuckGo (DDGS) — no key needed."""
    try:
        import sys as _sys
        _sys.path.insert(0, "/home/ubuntu/hermes-agent")
        from plugins.web.ddgs.provider import DDGSWebSearchProvider
        provider = DDGSWebSearchProvider()
        result = provider.search(query, limit=count)
        if result.get("success"):
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("description", ""),
                    "engine": "ddgs",
                }
                for r in result.get("data", {}).get("web", [])
            ]
    except Exception as e:
        log.warning(f"DDGS fallback failed: {e}")
    return []


def unified_search(query: str, count: int = 10) -> list:
    """Cascade: Tavily → SerperAPI → Brave → DDGS."""
    # 1. Tavily (en kaliteli, derin araştırma)
    results = tavily_search(query, count)
    if results:
        return results

    # 2. SerperAPI (Google SERP, 2500/ay, sub-200ms)
    log.info("Tavily empty, trying SerperAPI...")
    results = serper_search(query, count)
    if results:
        return results

    # 3. Brave (bağımsız index, 2000/ay)
    log.info("SerperAPI empty, trying Brave...")
    results = brave_search(query, count)
    if results:
        return results

    # 4. DDGS (son çare, sınırsız)
    log.info("Brave empty, trying DDGS...")
    return ddgs_search(query, count)


# ─── Response builder ────────────────────────────────────────────────

def make_searxng_response(results: list, query: str) -> str:
    """Package results into SearXNG JSON API format."""
    return json.dumps({
        "query": query,
        "number_of_results": len(results),
        "results": [
            {
                "title": r["title"],
                "url": r["url"],
                "content": r["content"],
                "engine": r.get("engine", "web"),
                "parsed_url": list(urllib.parse.urlparse(r["url"])),
                "template": "default.html",
            }
            for r in results
        ],
        "answers": {},
        "corrections": {},
        "infoboxes": {},
        "suggestions": [],
        "unresponsive_engines": [],
    })


# ─── HTTP handler ────────────────────────────────────────────────────

class SearXNGHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # Health check — shows available engines
        if parsed.path == "/health":
            engines = {
                "tavily": bool(_get_tavily_key()),
                "serper": bool(_get_serper_key()),
                "brave": bool(_get_brave_key()),
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "engines": engines,
                "cache": len(_cache),
            }).encode())
            return

        # Search endpoint
        if parsed.path == "/search":
            params = urllib.parse.parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            fmt = params.get("format", [""])[0]

            if not query:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing q parameter"}).encode())
                return

            if fmt != "json" and fmt != "":
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Only JSON format supported")
                return

            # Check cache first
            cached = cache_get(query)
            if cached is not None:
                response = make_searxng_response(cached, query)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("X-Cache", "HIT")
                self.end_headers()
                self.wfile.write(response.encode())
                return

            log.info(f"Search: {query[:80]}")
            results = unified_search(query)

            # Cache results
            if results:
                cache_set(query, results)

            response = make_searxng_response(results, query)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("X-Cache", "MISS")
            self.end_headers()
            self.wfile.write(response.encode())
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not found")

    def log_message(self, fmt, *args):
        log.info(f"{self.client_address[0]} {fmt % args}")


if __name__ == "__main__":
    # Ensure gateway env vars are loaded
    _gw_env = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(_gw_env):
        # Source .env for key discovery
        pass  # already handled by _read_key_from_env_or_envfile

    tavily_ok = bool(_get_tavily_key())
    serper_ok = bool(_get_serper_key())
    brave_ok = bool(_get_brave_key())

    server = http.server.HTTPServer(("127.0.0.1", PORT), SearXNGHandler)
    log.info(f"SearXNG proxy running on http://127.0.0.1:{PORT}")
    log.info(f"  Tavily: {'✓' if tavily_ok else '✗'} | Serper: {'✓' if serper_ok else '✗'} | Brave: {'✓' if brave_ok else '✗'}")
    log.info(f"  Cache TTL: {CACHE_TTL}s")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down")
        server.server_close()
