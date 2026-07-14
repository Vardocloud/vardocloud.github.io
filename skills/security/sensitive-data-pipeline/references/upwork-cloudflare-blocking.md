# Upwork Scraping — Oracle Cloud Datacenter IP Blocking

## Problem

Oracle Cloud (OCI) datacenter IPs are **comprehensively blocked by Cloudflare**. Upwork uses Cloudflare's Bot Management product, which:

1. Identifies Oracle Cloud IP ranges
2. Blocks all automated access from those ranges
3. Serves Cloudflare Challenge pages regardless of browser type

## Tested Approaches — ALL FAILED ❌

| Method | Result | Reason |
|---|---|---|
| Chrome CDP (Playwright) | ❌ Cloudflare Challenge | Datacenter IP |
| Camoufox (stealth browser) | ❌ Cloudflare Challenge | Datacenter IP |
| nodriver (2025 stealth) | ❌ Browser launch failed + IP | Datacenter IP |
| puppeteer-real-browser | ❌ Cloudflare Challenge | Datacenter IP |
| curl / requests | ❌ Cloudflare Challenge | Datacenter IP |
| Upwork RSS feed | ❌ Cloudflare Challenge | Datacenter IP |
| localhost.run tunnel | ❌ Service broken | N/A |
| VNC manual interaction | ❌ "failed to connect server" | Same IP issue |

**Key insight:** Cloudflare blocks based on **IP range**, not browser fingerprint. No browser automation tool can bypass this from a datacenter IP.

## Working Alternatives ✅

### 1. Google Custom Search API (Recommended)
- Query: `site:upwork.com/jobs [keywords]`
- Google's crawler indexes Upwork pages (no Cloudflare)
- Free tier: 100 queries/day
- Returns job URLs + snippets
- Can parse job details from snippets or follow URLs via Firecrawl
- **Does NOT require Upwork login**
- **Cron-compatible**
- **⚠️ PITFALL: API key oluşturmak yetmez.** Google Cloud Console'da API key'i oluşturduktan sonra, `customsearch.googleapis.com` API'sini ayrıca **Enable** etmen gerekiyor. Enable edilmezse `403: "This project does not have the access to Custom Search JSON API"` hatası verir. Key geçerli görünür ama API erişimi yoktur. Enable linki: https://console.cloud.google.com/apis/library/customsearch.googleapis.com

### 2. Apify Scraper
- Residential IP infrastructure
- No login required
- Free tier: 5,000 API calls/month
- Returns structured JSON
- Requires API key + $5/month for production use

### 3. Upwork Official API
- OAuth2 authentication required (one-time user authorization)
- Different endpoint, no Cloudflare
- Rate limited
- Requires developer token approval

### 4. User's Machine (Browser Extension)
- Runs on user's real residential IP
- No Cloudflare issues
- Requires user's computer to be online
- Webhook delivery to server

## Google CSE Setup Pitfall

**API key alone is not enough.** After creating the API key in Google Cloud Console, you MUST also enable the Custom Search JSON API:

1. Go to: https://console.cloud.google.com/apis/library/customsearch.googleapis.com
2. Select the correct project (the one where you created the API key)
3. Click **"Enable"**
4. Wait ~30 seconds for propagation

Without this step, you get:
```
403: "This project does not have the access to Custom Search JSON API."
```

The API key returns 200 for authentication but 403 for access — confusing error that looks like a bad key when it's actually a missing enable step.

**CX (Search Engine ID)** is created separately at: https://programmablesearchengine.google.com/controlpanel/all

## Recommendation

For a cron-based Upwork job monitoring system on Oracle Cloud:
**Google Custom Search API** is the only truly free, login-free, Cloudflare-bypass solution that works from a datacenter IP.
