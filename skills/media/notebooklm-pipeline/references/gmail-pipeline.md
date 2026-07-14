# Gmail → Bilgi Çıkarma Pipeline v2.2

## Overview

Cron job that scans Gmail for unread emails and processes them with three-tier categorization.

**Cron job ID:** `f4ea19bb906a`  
**Schedule:** Daily at 09:00, 15:00, 21:00 (UTC+3)  
**Skills:** google-workspace, llm-wiki  
**Model:** gpt-5.4-mini (Pollinations) — switched from DeepSeek V4 Pro on 4 Haz 2026 (~$12/mo → $0)

## Three Categories (v2.2 — 4 Haz 2026)

### 🔴 TİER A: APA & Skool (Full Processing)
- **Domains:** apa.org, skool.com
- **Process:** Extract links → web_extract content → NotebookLM + Wiki
- **APA →** NotebookLM APA Bilgi (`c44469fe`)
- **Skool →** Wiki (`~/wiki/experiences/skool/`)
- **⚠️ ALL_PROXY=""** required for Gmail API (Google blocks WARP)

### 🟡 TİER B: Fırsat Taraması (Light Processing)
- **Keywords:** "indirim", "discount", "promo", "free", "ücretsiz", "deneme", "trial", "opencode", "kredi", "credit"
- **Security check:** Verify domain before visiting (opencode.ai, github.com, producthunt.com are trusted)
- **No shortened URLs:** bit.ly, t.co, ow.ly → SKIP
- **Output:** Wiki (`~/wiki/experiences/firsatlar/`)
- **Format:** `[Tarih] [Kaynak] [Fırsat] [Link] [Son kullanma]`

### ⚫ TİER C: Diğer (Skip)
- Ads, newsletters, social notifications, password changes
- Julian Goldie, Nate Herk, AI Automation Society → SKIP

## Security Rules

| Rule | Description |
|------|-------------|
| Domain whitelist | Only visit apa.org and skool.com for full processing |
| No shortened URLs | Never follow bit.ly, t.co, ow.ly etc. |
| Hermes blocklist | Active — malicious TLDs auto-blocked |
| Text only | web_extract only, no JS execution, no file downloads |
| No forms | Never fill forms on visited sites |
| WARP proxy | All external visits through SOCKS5 for IP privacy |
| Logging | All visits logged to `~/wiki/logs/link-tarama.md` |

## Read Marking (⚠️ MANDATORY)

Every processed email MUST be marked as READ via Gmail API. This prevents duplicate processing across cron runs.

```bash
ALL_PROXY="" python3 ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py gmail modify <message_id> --remove-label UNREAD
```

## Gmail Search Command

```bash
ALL_PROXY="" python3 ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py gmail search "is:unread" --max 15
```

Then filter in-app: only from:apa.org and from:skool.com get Tier A processing.

## Report Format

Only send report if new emails were processed. Otherwise [SILENT].

```
📧 Gmail — [TARİH SAAT]

🔴 APA/Skool: N mail processed
🟡 Fırsat: N opportunities found
[If any: brief opportunity summary]

📥 Saved: NotebookLM / Wiki
```

## Changelog

| Date | Change |
|------|--------|
| 4 Haz 2026 | 3-category system (APA/Skool + Fırsat + Skip), read marking, security rules |
| 4 Haz 2026 | Model: DeepSeek V4 Pro → GPT-5.4-mini (Pollinations) |
| 4 Haz 2026 | Focus narrowed to APA + Skool only (removed Firecrawl/CF/DeepSeek) |
