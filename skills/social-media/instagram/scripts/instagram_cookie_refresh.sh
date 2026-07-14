#!/bin/bash
# Instagram Cookie Refresh — no_agent cron job
# Schedule: weekly (e.g. "0 3 * * 0" = Sunday 03:00)
# Uses Playwright + WARP to refresh cookies automatically

COOKIE_FILE="$HOME/.hermes/instagram_cookies.txt"
echo "=== Instagram Cookie Refresh $(date '+%Y-%m-%d %H:%M:%S') ==="

# Pre-flight checks
[ ! -f "$COOKIE_FILE" ] && { echo "❌ COOKIE YOK"; exit 1; }
CSRF=$(grep -c 'csrftoken' "$COOKIE_FILE"); SESSION=$(grep -c 'sessionid' "$COOKIE_FILE")
[ "$CSRF" -eq 0 ] || [ "$SESSION" -eq 0 ] && { echo "❌ EKSIK COOKIE"; exit 1; }

# WARP check
curl -s --socks5 warp:1080 --max-time 5 https://www.instagram.com/ > /dev/null 2>&1 || { echo "❌ WARP YOK"; exit 1; }
echo "✅ WARP çalışıyor"

# Playwright refresh
python3 -c "
import json, os, sys, time
from playwright.sync_api import sync_playwright

def parse_cookies(path):
    cookies = []
    with open(path) as f:
        for line in f:
            if line.startswith('#') or not line.strip(): continue
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                cookies.append({'name': parts[5], 'value': parts[6], 'domain': parts[0],
                    'path': parts[2], 'secure': parts[3] == 'TRUE', 'httpOnly': False})
    return cookies

def write_cookies(path, cookies):
    with open(path, 'w') as f:
        f.write('# Netscape HTTP Cookie File\n# Refreshed: ' + time.strftime('%Y-%m-%d %H:%M:%S') + '\n')
        for c in cookies:
            f.write(f\"{c['domain']}\t{'TRUE' if c['domain'].startswith('.') else 'FALSE'}\t{c['path']}\t{'TRUE' if c.get('secure') else 'FALSE'}\t{int(c.get('expires', 2147483647))}\t{c['name']}\t{c['value']}\n\")

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox'])
    ctx = b.new_context(proxy={'server': 'socks5://warp:1080'},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36')
    ctx.add_cookies(parse_cookies('$COOKIE_FILE'))
    page = ctx.new_page()
    page.goto('https://www.instagram.com/', wait_until='networkidle', timeout=30000)
    time.sleep(3)
    fresh = ctx.cookies()
    if not any(c['name'] == 'sessionid' for c in fresh):
        print('❌ sessionid KAYBOLDU! Manuel refresh gerekli.'); sys.exit(2)
    write_cookies('$COOKIE_FILE', fresh)
    os.chmod('$COOKIE_FILE', 0o600)
    for c in fresh:
        if c['name'] in ['sessionid', 'csrftoken', 'ds_user_id']:
            print(f\"✅ {c['name']} -> ok\")
    print(f'📊 {len(fresh)} cookie yenilendi')
    b.close()
" 2>&1 || { echo "❌ Playwright hatasi"; exit 2; }

# API verify
CSRF=$(grep 'csrftoken' "$COOKIE_FILE" | awk '{print $NF}')
RESULT=$(curl -s --socks5 warp:1080 --max-time 10 \
    "https://www.instagram.com/api/v1/users/web_profile_info/?username=bardopsikoloji" \
    -b "$COOKIE_FILE" -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)" \
    -H "X-CSRFToken: $CSRF" -H "X-IG-App-ID: 936619743392459" \
    -H "X-Requested-With: XMLHttpRequest" --compressed 2>&1)
echo "$RESULT" | grep -q 'status.*ok' && echo "✅ API test basarili" || echo "⚠️ API test hata"
echo "=== Done ==="