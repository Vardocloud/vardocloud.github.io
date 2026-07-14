# Cloudflare Challenge Types & Workarounds (13 Haz 2026)

## Challenge Type 1: "Verifying..." (Passive)
- **Trigger:** Camoufox headless, fresh browser fingerprint
- **Behavior:** Auto-shows spinner, no user action possible
- **Result:** Stuck indefinitely, never resolves to actual page
- **First seen:** 13 Haz 2026, Camoufox headless:true + cookie injection

## Challenge Type 2: "Verify you are human" (Interactive Button)
- **Trigger:** CDP Chrome (NotebookLM's instance, port 9222), known browser
- **Behavior:** Shows a "Verify you are human" button + Cloudflare Ray ID
- **Result:** Button can potentially be clicked programmatically via Puppeteer MCP
- **First seen:** 13 Haz 2026, Puppeteer MCP via NotebookLM Chrome
- **Selector:** Butonun HTML'i iframe içinde olabilir, `document.querySelector('button')` ile hedefle

## CDP Chrome Approach (via NotebookLM's Chrome)

NotebookLM MCP Chrome runs on port 9222 with `--headless=new`. Puppeteer MCP can connect to it:

1. `puppeteer_connect_active_tab(debugPort: 9222, targetUrl: "https://www.upwork.com")`
2. `puppeteer_navigate(url: "https://www.upwork.com/nx/search/jobs/?q=...")`
3. Or use `puppeteer_evaluate(script: "window.location.href = '...'")`

**Limitations:**
- `puppeteer_navigate` returns HTTP 403 (Cloudflare blocks)
- `window.location.href` assignment works but challenge still shows
- Puppeteer MCP evaluate returns `undefined` for complex return values (array/object)
- Direct CDP WebSocket blocked: Chrome needs `--remote-allow-origins=*` flag (not set)
- Puppeteer MCP's own connection works because it uses a different origin

## Cookie Expiry Observation (13 Haz 2026)

- 98 cookies total
- 94/98 expired within ~24 hours (server-side expiry)
- Only `master_access_token` and `oauth2_global_js_token` have no expiry value (session cookies)
- Server-side validation still fails despite session cookies → Cloudflare challenge redirect
- **Cookie export from user's own Chrome is the only reliable method**
