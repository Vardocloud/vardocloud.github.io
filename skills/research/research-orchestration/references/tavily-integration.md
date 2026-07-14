# Tavily API Integration for Research Cron Jobs

## Setup
```bash
# Save API key (Edel provides it)
echo "tvly-dev-..." > ~/.hermes/tavily_key.txt
chmod 600 ~/.hermes/tavily_key.txt
```

## Calling from a cron job
Cron jobs run in fresh sessions — they need the API key from the file, not from environment.

### Python execute_code pattern
```python
from hermes_tools import read_file

# Read key
result = read_file("~/.hermes/tavily_key.txt")
api_key = result["content"].strip()

# Tavily API call
import requests, json

response = requests.post(
    "https://api.tavily.com/search",
    headers={"Content-Type": "application/json"},
    json={
        "api_key": api_key,
        "query": "your search query here",
        "search_depth": "deep",
        "include_answer": True,
        "max_results": 10
    },
    timeout=60
)

data = response.json()
# data["answer"] — AI-generated summary
# data["results"] — list of {title, url, content}
```

### Required toolsets
When creating cron jobs that use Tavily:
```yaml
enabled_toolsets: ["web", "terminal", "file", "delegation", "code_execution"]
```
The `code_execution` toolset is REQUIRED for `execute_code` which calls the API.

## When to use Tavily vs web_search

| Tavily | web_search |
|--------|-----------|
| **FIRST tool** for any research task | Fallback only |
| Deep research with AI synthesis | Quick keyword scan |
| Cross-validation of findings | Surface-level discovery |
| 15-result advanced deep dives | 5-result quick scans |
| GitHub repo discovery | Known URLs |
| University program searches | Simple fact checks |
| "What tools exist for X?" | "What is X?" |

**Pitfall (June 2026):** Edel explicitly asked "tavily kullandın mı?" when web_search results felt shallow.
Always check if Tavily is available before starting any research task. Using web_search as primary
when Tavily exists is a mistake that produces weaker results and loses user trust.

## Terminal curl pattern (for live agent sessions)

This is the fastest way — no execute_code needed:
```bash
curl -s https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -d '{"api_key": "KEY", "query": "your query", "search_depth": "advanced", "include_answer": true, "max_results": 15}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('ANSWER:', d.get('answer','')[:1500]); [print(f'{i+1}. {r[\"title\"]}') for i,r in enumerate(d.get('results',[]))]"
```
Use `search_depth: "advanced"` (not "deep") for most queries — faster and same quality.

## Proven pattern: Tavily cross-validation
In the final synthesis phase, before compiling the report, take the top 3 findings and run Tavily cross-checks:
```
"X tool review 2025 reddit"  → real user opinions
"X tool alternatives"        → competitive landscape  
"X tool issues limitations"  → known problems
```

## Cost
Tavily has a free tier. Check `tvly-dev-` prefix — this is a dev key.
No per-query cost to worry about.
