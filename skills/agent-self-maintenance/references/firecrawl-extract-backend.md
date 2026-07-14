# Firecrawl as Web Extract Backend

Configured 09 Haz 2026 — bypasses Imperva/bot protection on APA and similar sites.

Set via: `hermes config set web.extract_backend firecrawl`.

Requires Firecrawl API key in the Hermes env file (check with grep -i firecrawl). Free tier: 1000 credits per month.

When web_extract is called, Hermes routes it through Firecrawl's API instead of the default scraper. Tested on APA Monitor pages which were previously blocked by Imperva.

Credit limit: 1000/month. APA cron jobs (3x daily) use ~90/month if all calls go through Firecrawl. Reserve for bot-blocked sites only.
