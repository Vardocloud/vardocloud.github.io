---
name: firecrawl
description: "Firecrawl as Hermes extract backend — configuration, testing, bypassing bot protection on APA and research sites."
category: devops
tags: [firecrawl, web-extract, browser-provider, bot-bypass, apa]
---

# Firecrawl — Extract Backend

## When to Use

Use this when:
- A site blocks web_extract with Imperva, Cloudflare, or hCaptcha
- Extracting full article text from APA Monitor or other bot-protected psychology sites
- Testing Firecrawl connectivity

## Configuration

Set Firecrawl as the extract backend:

```yaml
web:
  extract_backend: firecrawl
```

Hermes auto-detects Firecrawl when `FIRECRAWL_API_KEY` is set in the environment. Get a key at firecrawl.dev (free tier available).

Optional settings:
- `FIRECRAWL_API_URL` — self-hosted instance URL
- `FIRECRAWL_BROWSER_TTL` — session TTL in seconds (default: 300)

## How It Works

Firecrawl routes web requests through its own browser infrastructure:
1. Rotates user agents and IPs
2. Solves CAPTCHAs automatically
3. Returns clean markdown content

Verified bypassed protections:
- **Imperva (Incapsula)** — APA's bot protection ✅
- **Cloudflare** — Common on academic sites

## Testing

Test 1 — APA Monitor index:
```
web_extract(urls=["https://www.apa.org/monitor/2026/06/"])
```
Expected: Full index with article titles and links. Previously blocked by Imperva.

Test 2 — APA press release:
```
web_extract(urls=["https://www.apa.org/news/press/releases/2026/05/young-adults-perfectionistic"])
```
Expected: Full text with author names, journal references, DOIs.

## Pitfalls

- **Not a browser provider:** Only affects web_extract. For browser_navigate/click/type, configure via `hermes setup tools`
- **Click-tracked links:** APA emails use `click.info.apa.org` redirects. Find actual article URLs via web_search with `site:apa.org`
- **Gateway restart needed:** After changing extract_backend, restart gateway
- **Free tier limits:** Monitor monthly credit usage at firecrawl.dev
