# Auth Debugging History (Consolidated)

> Auth debugging archive. Actionable instructions are in SKILL.md; this file preserves the full troubleshooting history that led to current working methods.

## Root Cause (24 Haz 2026)

`undetected-chromedriver`'daki `excludeSwitches` parametresi Chrome'u CRASH ediyordu. Çözüm:
1. `client.py`: `uc.Chrome()` çağrısından `excludeSwitches` KALDIRILDI
2. `cli.py`: stdout swap ile banner çıktıları ayrıştırıldı
3. Symlink sağlam: `profiles/default/browser_profile` → `~/.hermes/chrome_profile_notebooklm`

## Full Post-Login Sequence (güncel)

1. VNC stack başlat: Xvfb :99 + x11vnc + noVNC + cloudflared
2. VNC'den Chrome aç: `DISPLAY=:99 chromium --user-data-dir=~/.hermes/chrome_profile_notebooklm ...`
3. Kullanıcı NotebookLM'a manuel login yapar
4. Kullanıcı "hazır" dediğinde:
   a. Playwright CDP ile Chrome'a bağlan
   b. storage_state.json export et
   c. **storage_state.json'ı SIFIRLA:** `echo '{"cookies":[],"origins":[]}' > .../storage_state.json`
   d. Zombie Chrome/undetected_chromedriver öldür
   e. MCP'yi başlat
5. Doğrula: `hermes mcp test notebooklm-mcp`

## Why Empty storage_state?

MCP'nin `_load_cookies()` Selenium `add_cookie()` kullanır. `__Secure-` ve cross-domain Google cookieleri sessizce başarısız olur. Boş storage_state ile MCP doğrudan profildeki `Default/Cookies` SQLite DB'sinden okur.

## Auth Strategies Tried

| Option | Method | Result | Date |
|--------|--------|--------|------|
| A | Cookie Import | ✅ Works (filtered) | 20 Haz |
| B | Manual Browser Login | ❌ signin/rejected | 20 Haz |
| C | VNC-assisted login | ✅ Works | 20-24 Haz |
| D | Xvfb + non-headless + CDP Bridge | ✅ Works w/ user | 20 Haz |
| F | Puppeteer MCP + Bitwarden | ✅ Works w/ 2FA | 23 Haz |
| G | Python CDP Websockets + Bitwarden | ✅ Works | 23 Haz |
| H | Chrome Direct Launch (VNC) | ✅ Works | 24 Haz |
| I | Clean Profile + Empty storage_state | ✅ **MOST RELIABLE** | 24 Haz |

## HTTP 413 Cookie Overflow (24 Haz 2026)

2000+ cookies from full browser export → HTTP 413. Fix: filter to Google-only:

```bash
python3 -c "
import json
with open('cookies.json') as f:
    raw = f.read()
if raw.startswith('1|'):
    raw = raw[2:]
cookies = json.loads(raw)
filtered = [c for c in cookies if 'google' in c.get('domain','').lower()]
with open('/tmp/nblm_cookies.json', 'w') as f:
    json.dump(filtered, f)
"
rm -rf ~/.notebooklm-mcp-cli/profiles/default
nlm login --manual -f /tmp/nblm_cookies.json
```

## MCP Crash-Loop + Zombie Cleanup

```bash
pkill -f undetected_chromedriver 2>/dev/null
pkill -f "chrome.*notebooklm" 2>/dev/null
pkill -f notebooklm-mcp 2>/dev/null
ps aux | grep -E "(undetected_chromedriver|chrome.*notebooklm)" | grep -v grep
```

## ChromeDriver Version Mismatch

Chromium 149, ChromeDriver 150 → `session not created`. Fix:
```bash
pip install --user undetected-chromedriver==3.5.4
# patch client.py: version_main=None → version_main=149
# add --remote-allow-origins=*
cp -r /usr/local/lib/.../notebooklm_mcp ~/.local/lib/.../
```

## Playwright → Selenium Cookie Format Mismatch (23 Haz)

MCP's `storage_state.json` is Playwright format, server uses Selenium. `_load_cookies()` silently drops cookies that fail `add_cookie()` — including critical Google auth cookies.

## URL Check Pitfall

`"notebook" in page.url` matches Google sign-in `continue` parameter. Always check `"accounts" not in page.url`.

## Rejected Detection

```python
if "signin/rejected" in page.url:
    print("Google bot protection active — switch to VNC")
    break
```

## Google React LI Click Pitfall

`<li>` elemanları `.click()` yanıt vermez. `Input.dispatchMouseEvent` ile fiziksel tıklama gerekir.

## Auth Read/Write Asymmetry

| Operation | Stale Auth |
|-----------|-----------|
| notebook_list, notebook_query, source_add(text/url) | ✅ Çalışır |
| studio_create (slide_deck/infographic/audio/video) | ❌ Bloke olur |
| CLI vs MCP | CLI farklı auth seviyesi kullanabilir |

## CDP Anti-Detection Script

```javascript
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
```
Eklendiğinde temel bot tespitini geçer ama fingerprint tabanlı tespiti geçemez.

## x11vnc MIT-SHM Crash

```bash
x11vnc -display :100 -forever -shared -nopw -noxdamage -nodpms
```
