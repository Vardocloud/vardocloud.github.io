# Cloudflare Enterprise Bot Management — Cookie Injection Bypass

For sites with **Enterprise-tier Cloudflare Bot Management** (e.g. Upwork), automated browser form submission (POST) is blocked even with:
- puppeteer-extra-plugin-stealth ✅ page load, ❌ form submit
- Camoufox (Firefox fork, C++ fingerprint spoofing) ✅ page load, ❌ form submit
- WARP+ proxy (different IP) ❌ still blocked
- Proxychains + residential proxy ❌ still blocked

**Root cause:** Cloudflare Bot Management scores every request 1-99. Datacenter IPs (Oracle, AWS, GCP) get baseline negative scores. Form POST requests get additional scrutiny (TLS fingerprint, JA4, timing, header analysis). No browser-level evasion works because the detection is server-side.

## The Only Working Bypass: Cookie Injection

### Flow
1. User exports cookies from a REAL browser (Chrome extension "Export cookie JSON file for Puppeteer")
2. User sends the cookies.json file
3. Load cookies into Camoufox/Playwright context BEFORE navigating to the domain
4. The existing session cookie bypasses all Cloudflare checks

### Camoufox Implementation

```javascript
const { Camoufox } = require('camoufox');
const fs = require('fs');

const cookies = JSON.parse(fs.readFileSync('/path/to/cookies.json', 'utf8'));
const pwCookies = cookies.map(c => ({
  name: c.name,
  value: c.value,
  domain: c.domain.startsWith('.') ? c.domain : '.' + c.domain,
  path: c.path || '/',
  httpOnly: c.httpOnly || false,
  secure: c.secure || true,
  sameSite: normalizeSameSite(c.sameSite)
}));

const browser = await Camoufox({ headless: true, os: 'windows', humanize: 1.5 });
const page = await browser.newPage();
await page.context().addCookies(pwCookies);  // BEFORE navigation!
await page.goto('https://example.com', { waitUntil: 'load' });
```

### SameSite Normalization (Required)

Playwright expects `Strict | Lax | None`. Chrome export uses lowercase + custom values:

```javascript
function normalizeSameSite(val) {
  const v = (val || '').toLowerCase();
  if (!v || v === 'unspecified') return 'Lax';
  if (v === 'no_restriction') return 'None';
  if (v === 'lax') return 'Lax';
  if (v === 'strict') return 'Strict';
  if (v === 'none') return 'None';
  return 'Lax';
}
```

### ARM64 Compatibility

Camoufox runs on ARM64 (Oracle Cloud):
```bash
# Install
npx camoufox fetch
chmod +x ~/.cache/camoufox/camoufox-bin

# Binary is ARM64 native:
file ~/.cache/camoufox/camoufox-bin
# → ELF 64-bit, ARM aarch64
```

## When Cookie Export Isn't Possible

**Alternative: OAuth2 API Token** (requires Developer Portal setup)
1. Create OAuth2 project in the service's developer portal (callback: `http://localhost`)
2. User authorizes the app from their browser
3. Generate `client_id` + `client_secret`
4. Use these for server-side API access — no browser automation needed

## Research Results

### Tested Methods (all failed on form submit)

| Method | Page Load | Form Submit |
|--------|-----------|-------------|
| Puppeteer + Snap Chromium | ✅ | ❌ CF challenge |
| Puppeteer-extra + stealth-plugin | ✅ | ❌ "technical difficulties" |
| Playwright Chromium (CDP) | ✅ | ❌ CF block |
| Camoufox (Firefox fork) | ✅ | ❌ CF block |
| Camoufox + WARP proxy (proxychains) | ✅ | ❌ CF block |
| **Cookie injection (real browser export)** | ✅ | **✅ WORKS** |

### Key URLs (Upwork)
- Login: `https://www.upwork.com/ab/account-security/login`
- Freelancer profile: `https://www.upwork.com/freelancers/~`
- Profile setup: `https://www.upwork.com/nx/create-profile/general`
