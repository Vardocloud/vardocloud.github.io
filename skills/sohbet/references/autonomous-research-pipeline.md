# Tavily + Cron Multi-Phase Research Pipeline

**Date:** 2026-05-24
**Context:** Bardo Psychology marketing strategy research for Edel

## Pattern

When Edel asks for deep, multi-angle research on a topic, use staggered cron jobs with Tavily deep search:

### Architecture
```
Phase 1 (now): Basic web search → broad market context
Phase 2 (+40m): Tavily deep search → GitHub repos, MCP servers, AI tools
Phase 3 (+80m): Tavily deep search → alternative channels, platforms
Phase N (+N*40m): Specialized deep dives (auth, security, code patterns)
Final (+140m): Cross-check + synthesis → deliver to Edel via Telegram
```

### Key Principles

1. **Cron jobs, not sequential execution** — each phase is self-contained, saves to file
2. **Stagger schedules** — 30-40 minute gaps between phases so upstream results are available
3. **Tavily API via execute_code** — cron jobs use Python to call Tavily REST API, not web_search
4. **API key in file** — save to `~/.hermes/tavily_key.txt` (chmod 600), read from cron
5. **Files as inter-phase communication** — each phase writes to `~/research_bardo/phase_N.md`
6. **Final synthesis phase** reads all files, cross-validates with Tavily, delivers via Telegram

### Tavily API Call Pattern (in execute_code)
```python
import requests, json

with open('/home/ubuntu/.hermes/tavily_key.txt') as f:
    api_key = f.read().strip()

queries = [
    "google ads MCP server github 2025",
    "AI advertising agent autonomous PPC",
    # ... 10-12 queries
]

results = []
for q in queries:
    r = requests.post("https://api.tavily.com/search", json={
        "api_key": api_key,
        "query": q,
        "search_depth": "deep",
        "include_answer": True,
        "max_results": 10
    })
    results.append(r.json())

# Process and save to markdown
with open('/home/ubuntu/research_bardo/deep_N_topic.md', 'w') as f:
    # ... format results
```

### Pivot-Friendly Design

Edel may redirect mid-research. Pattern supports this:
- Cancel old cron jobs with `cronjob(action='remove', job_id=...)`
- Create new ones with refined prompts
- Phases that already ran are preserved (files on disk)
- Final synthesis adapts to whatever files exist

### Anti-Patterns

❌ Creating a single cron job that does everything — no parallelism, can't pivot
❌ Using web_search for deep technical research — Tavily's `deep` mode is 10x better for GitHub repos and niche tools
❌ Delivering results immediately to Edel — she wants the final report, not piecemeal updates
❌ Not saving API key to file — each cron job is a fresh session with no context
❌ Using `schedule: "now"` — it's invalid. Use `"1m"` for immediate execution
❌ One-shot jobs that miss their window silently fail — always verify with `cronjob(action='list')` after scheduling

### Models

- Research phases: any model (deepseek-v4-pro default)
- Tavily API calls: via execute_code (no LLM needed, just HTTP)
- Synthesis phase: strong model (deepseek-v4-pro) for coherent report
