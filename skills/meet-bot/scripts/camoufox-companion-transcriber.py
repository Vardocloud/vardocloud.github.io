#!/usr/bin/env python3
"""
Google Meet Companion-mode transcriber using Camoufox (Firefox fork).
Captures captions only — no PulseAudio / audio recording needed.
Works in Docker/WSL where PulseAudio is not available.

Usage:
    python3 camoufox-companion-transcriber.py MEET_URL [GUEST_NAME]
    python3 camoufox-companion-transcriber.py MEET_URL GUEST_NAME --outdir /tmp/meet_out

Requires:
    pip install camoufox
    camoufox fetch                     # ~700MB Firefox binary

Flow:
    1. Camoufox (Firefox) — bypasses Chromium "browser unsupported" detection
    2. "Other ways to join" → "Use Companion mode" — bypasses host admission lobby
    3. Caption scraping — no PulseAudio/ffmpeg needed
    4. Periodically saves new captions to transcript file

Tested: 17 Temmuz 2026 — Docker/WSL, headless, 124 participants
"""
import sys, time, json, os

# --- Configuration ---
MEET_URL = sys.argv[1] if len(sys.argv) > 1 else "https://meet.google.com/..."
GUEST_NAME = sys.argv[2] if len(sys.argv) > 2 else "Berkcan"
OUT_DIR = "/home/ubuntu/.hermes/workspace/meetings/kuo-qepy-wsd"

# Override OUT_DIR via --outdir flag
for i, arg in enumerate(sys.argv):
    if arg == '--outdir' and i + 1 < len(sys.argv):
        OUT_DIR = sys.argv[i + 1]

TRANSCRIPT_PATH = f"{OUT_DIR}/transcript.txt"
LOG_PATH = f"{OUT_DIR}/camoufox_bot.log"
CAPTION_POLL_INTERVAL = 3  # seconds between caption polls
JOIN_TIMEOUT = 90  # max seconds to wait for join UI

os.makedirs(OUT_DIR, exist_ok=True)

FIREFOX_PREFS = {
    "permissions.default.microphone": 1,
    "permissions.default.camera": 1,
    "media.navigator.permission.disabled": True,
    "media.navigator.streams.fake": True,
}


def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[{ts}] {msg}\n")


def main():
    from camoufox import Camoufox

    log(f"Starting Camoufox Companion transcriber")
    log(f"  URL: {MEET_URL}")
    log(f"  Name: {GUEST_NAME}")
    log(f"  Output: {TRANSCRIPT_PATH}")

    with Camoufox(headless=True, firefox_user_prefs=FIREFOX_PREFS) as browser:
        page = browser.new_page()

        # --- Step 1: Navigate ---
        log("Navigating to meeting...")
        page.goto(MEET_URL, wait_until="domcontentloaded", timeout=30000)

        # --- Step 2: Wait for pre-join UI ---
        pre_join_ready = False
        for i in range(JOIN_TIMEOUT):
            txt = page.evaluate("document.body.innerText")
            if "Your name" in txt or "What's your name" in txt:
                log(f"Pre-join UI ready after {i}s")
                pre_join_ready = True
                break
            if "can't join" in txt.lower():
                log(f"DENIED — meeting not accessible (page says: can't join)")
                page.screenshot(path=f"{OUT_DIR}/denied.png")
                browser.close()
                return 1
            time.sleep(1)

        if not pre_join_ready:
            log("Timed out waiting for pre-join UI — dumping page text")
            txt = page.evaluate("document.body.innerText")
            log(f"Page text (first 500): {txt[:500]}")
            page.screenshot(path=f"{OUT_DIR}/timeout.png")
            browser.close()
            return 1

        # --- Step 3: Enter name (React-compatible value setter) ---
        page.evaluate("""(name) => {
            const inp = document.querySelector('input[type="text"]');
            if (inp) {
                const ns = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                ns.call(inp, name);
                inp.dispatchEvent(new Event('input', {bubbles: true}));
                inp.dispatchEvent(new Event('change', {bubbles: true}));
            }
        }""", GUEST_NAME)
        log(f"Name entered: {GUEST_NAME}")
        time.sleep(1)

        # --- Step 4: Try Companion mode (preferred) ---
        companion_clicked = page.evaluate("""() => {
            const btns = [...document.querySelectorAll('button, [role="button"]')];
            // First expand "Other ways to join"
            for (const b of btns) {
                const t = (b.textContent || '').toLowerCase().trim();
                if (t.includes('other ways')) { b.click(); return 'clicked other ways'; }
            }
            return 'other ways not found';
        }""")
        log(f"Other ways: {companion_clicked}")
        time.sleep(1)

        companion_mode = page.evaluate("""() => {
            const btns = [...document.querySelectorAll('button, [role="button"]')];
            for (const b of btns) {
                const t = (b.textContent || '').toLowerCase().trim();
                if (t.includes('companion')) { b.click(); return 'clicked companion'; }
            }
            return 'companion not found';
        }""")
        log(f"Companion mode: {companion_mode}")

        # --- Step 5: Fallback to "Join now" if Companion mode unavailable ---
        if 'not found' in companion_mode:
            join_now = page.evaluate("""() => {
                const btns = [...document.querySelectorAll('button, [role="button"]')];
                for (const b of btns) {
                    const t = (b.textContent || '').toLowerCase().trim();
                    if (t.includes('join now')) {
                        if (!b.disabled) { b.click(); return 'clicked join now'; }
                        return 'join now disabled';
                    }
                }
                return 'join now not found';
            }""")
            log(f"Join now fallback: {join_now}")

        time.sleep(5)

        # --- Step 6: Verify we're inside ---
        page_text = page.evaluate("document.body.innerText")

        if "can't join" in page_text.lower():
            log("DENIED after join attempt")
            with open(f"{OUT_DIR}/denied_page.html", "w") as f:
                f.write(page.evaluate("document.body.innerHTML"))
            browser.close()
            return 1

        if "Leave call" in page_text or "Turn on captions" in page_text:
            log("✅ SUCCESSFULLY IN THE MEETING!")
        else:
            log(f"⚠️ Unknown state — 'Leave call' not found, trying captions anyway")
            log(f"Page sample: {page_text[:200]}")

        # --- Step 7: Turn on captions ---
        page.evaluate("""() => {
            const btns = [...document.querySelectorAll('button, [role="button"]')];
            for (const b of btns) {
                if ((b.textContent || '').includes('Turn on captions')) {
                    b.click(); return;
                }
            }
        }""")
        log("Captions turned on")

        # Detect caption language — switch to Turkish if English
        lang_text = page.evaluate("""() => {
            const combo = document.querySelector('[aria-label*="anguage" i]');
            return combo ? combo.textContent : '';
        }""")
        log(f"Caption language: {lang_text}")

        if 'English' in lang_text:
            log("Switching caption language to Turkish...")
            page.evaluate("""() => {
                const combo = document.querySelector('[aria-label*="anguage" i]');
                if (combo) { combo.click(); }
            }""")
            time.sleep(0.5)
            page.evaluate("""() => {
                const options = [...document.querySelectorAll('[role="option"]')];
                const tr = options.find(o => o.textContent.includes('Turkish'));
                if (tr) { tr.click(); }
            }""")
            log("Language switched to Turkish (Turkey)")

        # --- Step 8: Main caption poll loop ---
        log("Starting caption poll loop...")
        seen = set()

        try:
            while True:
                texts = page.evaluate("""() => {
                    const cr = document.querySelector(
                        '[role="region"][aria-label*="aption" i]');
                    if (!cr) return [];
                    const results = [];
                    const walker = document.createTreeWalker(
                        cr, NodeFilter.SHOW_TEXT, null, false);
                    let node;
                    while (node = walker.nextNode()) {
                        const t = (node.textContent || '').trim();
                        if (t.length > 2) results.push(t);
                    }
                    return results;
                }""")

                for t in texts:
                    if t not in seen:
                        seen.add(t)
                        line = f"[{time.strftime('%H:%M:%S')}] {t}\n"
                        with open(TRANSCRIPT_PATH, "a") as f:
                            f.write(line)
                        print(f"[CAPTION] {t}", flush=True)

                time.sleep(CAPTION_POLL_INTERVAL)

        except KeyboardInterrupt:
            log("Stopped by user")
        except Exception as e:
            log(f"Fatal poll error: {e}")
            raise

    log(f"Done. {len(seen)} caption lines saved to {TRANSCRIPT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
