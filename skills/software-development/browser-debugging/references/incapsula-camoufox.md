# Incapsula/Imperva Bypass Notes

## Identification

Incapsula (now Imperva WAF) is identified by:
- Body text: "Request unsuccessful. Incapsula incident ID: XXXXXXXXX..."
- Challenge script: `<script src="/levaine-I-safe-will-enox-My-wouldst-then-mosteed" async></script>`
- Cookies after passing: `visid_incap_XXXXXXXX`, `incap_ses_XXX_XXXXXXXX`
- HTTP 403 on direct `requests` calls (TLS fingerprint mismatch)

## Tested Sites

### APA (sso.apa.org) — May 2026
- Playwright Chromium headless → **BLOCKED** (Incapsula incident ID)
- Playwright Chromium + WARP proxy → **BLOCKED**
- Playwright Chromium + stealth init scripts → **BLOCKED**
- Camoufox (Firefox-based) headless → **PAGE LOAD PASSES**, form loads
  - But form submit silently blocked — no POST request fires
  - `visid_incap_2624412` and `incap_ses_692_2624412` cookies present
- `requests` with Camoufox cookies → **403** (TLS fingerprint differs)

## Strategy for Incapsula Login Forms

1. Try **Google/SSO login** button instead of password form (often bypasses WAF re-evaluation)
2. If password form required: Camoufox page-load → capture full cookie jar + CSRF → pass to `curl_cffi` (preserves TLS fingerprint)
3. Last resort: residential proxy + headed browser (human IP)
