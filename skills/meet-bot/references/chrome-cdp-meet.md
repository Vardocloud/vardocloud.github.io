---
title: Chrome CDP — Meet Join + Caption Capture
date: 2026-07-17
---

# Chrome CDP — Google Meet Join + Caption Capture (Port 18800)

## Ne Zaman Kullanılır

- `meet_join` → "host denied admission" (false positive — Chromium browser detection)
- Camoufox/Firefox → join yapar ama **captions çalışmaz** (Firefox headless'ta captions DOM'a gelmez)
- Hermes browser tools → browser_navigate shows pre-join UI but join fails

Chrome CDP **en güvenilir caption yöntemidir**: NotebookLM Chrome (port 18800) Edel'in hesabına login, 2FA gerekmez.

## Flow (Adım Adım)

```python
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
    context = browser.contexts[0]
    page = context.new_page()
    page.goto(meet_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    # 1. Dismiss dialogs (TR/EN)
    for label in ["continue without microphone", "got it", "devam et", "anladim", "tamam"]:
        for b in page.query_selector_all('button'):
            t = (b.text_content() or '').lower()
            aria = (b.get_attribute('aria-label') or '').lower()
            if label in t or label in aria:
                if b.is_visible(): b.click(); time.sleep(0.5); break

    # 2. Fill name if empty
    inp = page.query_selector('input[type="text"]')
    if inp: inp.fill(guest_name); time.sleep(0.5)

    # 3. Companion mode join
    for label in ["other ways", "diger", "diğer"]:
        for b in page.query_selector_all('button'):
            if label in (b.text_content() or '').lower(): b.click(); time.sleep(1); break
    for label in ["companion", "eslik", "eşlik"]:
        for b in page.query_selector_all('button'):
            if label in (b.text_content() or '').lower(): b.click(); time.sleep(3); break

    # 4. Verify in meeting
    assert "can't join" not in page.evaluate("document.body.innerText").lower()

    # 5. Turn on captions (TR/EN labels)
    page.evaluate("""() => {
        for (const b of document.querySelectorAll('button')) {
            const aria = (b.getAttribute('aria-label') || '').toLowerCase();
            const text = (b.textContent || '').toLowerCase();
            if ((aria.includes('altyaz') && aria.includes('aç')) or 
                (aria.includes('turn on captions')) or
                (text.includes('closed_caption_off'))) {
                b.click(); return;
            }
        }
    }""")

    # 6. Switch caption language to Turkish (CRITICAL)
    page.evaluate("""() => {
        const combo = document.querySelector(
            '[role="combobox"][aria-label*="language" i],' +
            '[role="combobox"][aria-label*="dil" i]');
        if (combo) {
            combo.click();
            setTimeout(() => {
                for (const opt of document.querySelectorAll('[role="option"]')) {
                    if (opt.textContent.includes('Turkish')) { opt.click(); break; }
                }
            }, 500);
        }
    }""")
    time.sleep(3)

    # 7. Poll captions loop
    while True:
        caps = page.evaluate("""() => {
            const found = [];
            const cr = document.querySelector(
                '[role="region"][aria-label*="aption" i]');
            if (cr) cr.querySelectorAll(':scope span').forEach(s => {
                const t = (s.textContent||'').trim();
                if (t.length > 3) found.push(t);
            });
            document.querySelectorAll('[aria-live="polite"]').forEach(el => {
                const t = (el.textContent||'').trim();
                if (t.length > 5) found.push(t);
            });
            return [...new Set(found)];
        }""")
        time.sleep(3)
```

## Caption Button Labels (TR/EN)

- OFF: `Turn on captions` / `Altyazilari aç`
- ON: `Turn off captions` / `Altyazilari kapat`

## Turkish Language Switch

Selector: `[role="combobox"][aria-label*="language" i]`

Adımlar: click combobox → "Turkish (Turkey)" seç → captions Türkçe gelir.  
Dil değiştirilmezse İngilizce çeviri Türkçe'yi anlamsız karakterlere dönüştürür.  
**17 Tem 2026: 259 satırın tamamı kullanılamaz hale geldi.**

## NotebookLM Auth Fix

Chrome CDP'den alınan cookies **flat list** formatında kaydedilmeli (Playwright `context.cookies()` çıktısı).  
Dict with `"cookies"` key formatı `TypeError: expected string, got 'list'` hatası verir.

```bash
# Dogru format:
cookies = context.cookies()  # list of dicts
json.dump(cookies, f)        # flat list

# Upload:
nlm source add <NOTEBOOK_ID> --file <wiki_md_path> --title "Baslik" --wait --wait-timeout 120 --profile legacy
```

## Pitfalls

- Caption region empty → captions not ON → check button aria-label (TR/EN)
- Garbled text → language = English → switch to Turkish
- nlm login --cdp-url hangs → using --manual with exported cookies instead
- cookies.json "expected string, got list" → flat list required, not dict with cookies key
- Firefox captions silent → captions DOM never appears in Firefox headless → use Chrome CDP

Full implementation: `scripts/meet_autojoin.py`
