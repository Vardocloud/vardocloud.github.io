---
title: Cloudflare Bot Management Bypass
name: cloudflare-bot-bypass
description: Strategies and tools for bypassing Cloudflare Bot Management and anti-bot detection in browser automation.
category: browser
---

# Cloudflare Bot Detection Bypass

## When to use
- Target site uses Cloudflare Bot Management (detected by `mmMwWLliI0fiflO&1` in page source, `cf_chl_opt` cookies, or "technical difficulties" errors on form submit)
- Standard Puppeteer/Playwright navigation works but form POST requests get blocked
- `403`, `503`, or "Just a moment..." pages appear

## Core Strategy

### Layer 1: Page Load Bypass (usually easiest)
- `puppeteer-extra-plugin-stealth` (puppeteer-extra)
- `--disable-blink-features=AutomationControlled` flag
- Custom User-Agent (Windows Chrome preferred)
- These often work for **page navigation (GET)** but fail on **form submission (POST)**

### Layer 2: C++-Level Fingerprint Spoofing
- **Camoufox** (Firefox fork) — most promising tool
  - GitHub: `daijro/camoufox` | npm: `camoufox`
  - Patches fingerprint at C++ level (WebGL, AudioContext, navigator, etc.)
  - Uses Playwright API, NOT Puppeteer
  - ARM64 binary available

### Layer 3: Infrastructure
- **Residential proxy required** — datacenter IPs (AWS, Oracle, DigitalOcean) are flagged by Cloudflare
- TLS fingerprint (JA3/JA4) randomization
- Consistent IP + fingerprint across entire session

## Camoufox Usage

### Installation
```bash
npm install camoufox
npx camoufox fetch
chmod -R 755 ~/.cache/camoufox
```

### Important API differences (vs Puppeteer)
- `waitUntil` values: `'load' | 'domcontentloaded' | 'networkidle' | 'commit'` (NOT `networkidle2`)
- Use Playwright locators: `page.locator()` or `page.getByRole()`
- No `page.waitForTimeout()` — use `await new Promise(r => setTimeout(r, ms))`
- `page.setViewportSize()` must be called explicitly

### Launch Options
```javascript
const { Camoufox } = require('camoufox');
const browser = await Camoufox({
  headless: true,          // true, false, or 'virtual' (Xvfb)
  os: 'windows',           // or 'macos', 'linux'
  humanize: 1.5,           // cursor movement humanization (seconds)
  locale: ['en-US'],
  screen: { min_width: 1280, min_height: 720 },
  proxy: { server: 'http://proxy:8080' }  // optional residential proxy
});
```

### Selector strategy (Playwright)
- **Avoid** `:has-text()` pseudo-selectors in raw CSS (use Playwright locators instead)
- Use `button[button-role="continue"]` for specific buttons
- Use `page.getByRole('button', { name: 'Log in', exact: true })` for exact text match
- Use `input[type="password"]` — name attribute can vary
- Use `{ force: true }` on `.click()` when form overlays intercept pointer events

## Detection Patterns

### Cloudflare Bot Management signals
| Signal | Likely Meaning |
|--------|----------------|
| `mmMwWLliI0fiflO&1` in page source | Bot Management active |
| `cf_chl_opt` cookie | Challenge issued |
| "Due to technical difficulties" | Form POST blocked |
| "Just a moment..." | Generic challenge page |
| `403` / `503` on navigation | IP/datacenter flagged |

### Cloudflare Turnstile signals (separate product)
Turnstile is Cloudflare's lightweight CAPTCHA alternative — a checkbox or invisible challenge embedded in a form, NOT a page-level block.

| Signal | Likely Meaning |
|--------|----------------|
| `<iframe>` containing "Cloudflare security challenge" | Turnstile widget embedded |
| "Verify you are human" checkbox in iframe | Turnstile visible challenge |
| `cf-turnstile` class or data attribute in HTML | Turnstile widget rendered |
| Form has a hidden `cf-turnstile-response` field | Turnstile in invisible mode |
| Page loads fine (no 403) but form submit fails | Turnstile token missing/expired |

**Key difference from Bot Management:** Turnstile does NOT block page navigation — the page renders fully. It only blocks form submission until the challenge is solved. Use browser snapshot's `iframe` detection to identify it:

```
"Iframe \"Widget containing a Cloudflare security challenge\" [ref=e9]"
```

**Approach for Turnstile:**
- Hermes browser tool navigates Turnstile pages fine (no block)
- The checkbox/iframe is visible but automated interaction may fail (CAPTCHA)
- Fallback: switch to email-based auth that doesn't trigger Turnstile (many sites offer "magic link" or regular password flow), or ask the user to complete the Turnstile manually through VNC/screenshare

### Why GET works but POST fails
Cloudflare Bot Management **scores every request individually** (1-99). GET requests get lower scores; form submissions (POST with credentials) get higher scrutiny due to:
- TLS/JA4 fingerprint analysis
- Header consistency checks
- Request timing and behavioral analysis

## Known Limitations
- `cf_clearance` cookie is **cryptographically bound** to the generating browser fingerprint
- Datacenter IPs are frequently blocked outright
- Residential proxy + Camoufox combo is the most reliable approach
- Some sites have additional backend security beyond Cloudflare

## The HOME-IP Trap — symmetric risk (added 19 Jul 2026)

The corollary to "datacenter IPs are flagged" is the **opposite trap**: home/residential IPs that run bot-driven automation get burned just as badly, with a different blast radius.

**Scenario:** An agent lives on a household laptop. The home IP burns through DataDome / upstream WAF because the agent signs Upwork / LinkedIn / Instagram 200×/day at 3am. DataDome flags that subnet → every device on that ISP connection (phones, tablets, other laptops) hits "You've been blocked" on those sites.

**Required mitigations for any agent-on-residential-IP deployment:**
1. **WARP / VPN tunnel** — agent egress MUST NOT be the raw residential IP. Use Cloudflare WARP (skill: `warp-proxy`) or a reputable paid residential proxy with rotation. Hermit-style agent profiles are already WARP-masked by default; new field-agent machines must follow that pattern, not bypass it.
2. **Throttle hard** — bot automation is flagged by *request frequency per ASN*, not per request. Fewer requests, longer pauses, humanized behavior (`bot-protected-pdf-extraction`, `protected-resource-download` cover the per-request discipline).
3. **Burn monitoring** — if DataDome/CF flags the home ASN, **pause immediately and rotate**. The cost of leaving a flagged residential IP running is the entire household losing access, not just the agent.
4. **Exit fallback** — primary control plane on dedicated/WARP'd infrastructure, residential IP only for the browser-uplink task that genuinely needs it.

**Rule:** "Bot automation on a residential IP" is "datacenter IP flagged" with a different blast radius. Both are caused by automation without rate-discipline + WARP masking. Address them together. Don't frame "agent on home IP" as risk-free just because it's not a cloud datacenter.

## Pitfalls
- ❌ Do NOT hardcode passwords in scripts — use `process.env.PW` or file reads
- ❌ Do NOT use Puppeteer `waitForTimeout` — deprecated; use `Promise + setTimeout`
- ❌ Do NOT use `:has-text()` in raw DOM selectors — only works in Playwright locators
- ❌ Do NOT reuse `cf_clearance` across different IPs/browsers
- ✅ Always dismiss cookie banners before interacting with forms
- ✅ Use `{ force: true }` for clicks when form intercepts pointer events
