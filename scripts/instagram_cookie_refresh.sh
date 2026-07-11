#!/bin/bash
# Instagram Cookie Refresh Script
# Runs via Playwright to refresh Instagram cookies before they expire
# Designed as no_agent cron script - outputs status for delivery
# Schedule: weekly (every Sunday at 03:00)

COOKIE_FILE="$HOME/.hermes/instagram_cookies.txt"
LOG_FILE="$HOME/.hermes/logs/instagram_cookie_refresh.log"

echo "=== Instagram Cookie Refresh $(date '+%Y-%m-%d %H:%M:%S') ==="

# 1. Check if cookie file exists
if [ ! -f "$COOKIE_FILE" ]; then
    echo "❌ COOKIE YOK: $COOKIE_FILE"
    exit 1
fi

# 2. Pre-flight: check required cookies
CSRF=$(grep -c 'csrftoken' "$COOKIE_FILE" 2>/dev/null)
SESSION=$(grep -c 'sessionid' "$COOKIE_FILE" 2>/dev/null)
DSID=$(grep -c 'ds_user_id' "$COOKIE_FILE" 2>/dev/null)

echo "📋 Pre-flight: csrftoken=$CSRF sessionid=$SESSION ds_user_id=$DSID"

if [ "$CSRF" -eq 0 ] || [ "$SESSION" -eq 0 ] || [ "$DSID" -eq 0 ]; then
    echo "❌ EKSIK COOKIE: Manuel refresh gerekli (Chrome'dan EditThisCookie ile export)"
    exit 1
fi

# 3. Check WARP proxy
if ! curl -s --socks5 warp:1080 --max-time 5 https://www.instagram.com/ > /dev/null 2>&1; then
    echo "❌ WARP PROXY CALISMIYOR"
    exit 1
fi
echo "✅ WARP proxy çalışıyor"

# 4. Refresh cookies via Playwright
# Uses current cookies to open Instagram, lets page load, exports fresh cookies
python3 << 'PYEOF' 2>> "$LOG_FILE"
import json, os, sys, time

cookie_path = os.path.expanduser("~/.hermes/instagram_cookies.txt")

# Parse Netscape cookies
def parse_netscape_cookies(path):
    cookies = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 7:
                cookies.append({
                    "name": parts[5],
                    "value": parts[6],
                    "domain": parts[0],
                    "path": parts[2],
                    "secure": parts[3] == "TRUE",
                    "httpOnly": False,
                })
    return cookies

# Write Netscape cookies
def write_netscape_cookies(path, cookies):
    with open(path, "w") as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n")
        f.write(f"# Refreshed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        for c in cookies:
            domain = c["domain"]
            domain_flag = "TRUE" if domain.startswith(".") else "FALSE"
            path_val = c["path"]
            secure = "TRUE" if c.get("secure") else "FALSE"
            expires = int(c.get("expires", 2147483647))
            name = c["name"]
            value = c["value"]
            f.write(f"{domain}\t{domain_flag}\t{path_val}\t{secure}\t{expires}\t{name}\t{value}\n")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright yok: pip install playwright")
    sys.exit(1)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        ctx = browser.new_context(
            proxy={"server": "socks5://warp:1080"},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        # Load existing cookies
        existing = parse_netscape_cookies(cookie_path)
        ctx.add_cookies(existing)
        print(f"✅ {len(existing)} cookie yüklendi")
        
        page = ctx.new_page()
        page.goto("https://www.instagram.com/", wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        # Get fresh cookies
        fresh_cookies = ctx.cookies()
        
        # Check if sessionid survived
        has_session = any(c["name"] == "sessionid" for c in fresh_cookies)
        has_csrf = any(c["name"] == "csrftoken" for c in fresh_cookies)
        
        if not has_session:
            print("❌ sessionid KAYBOLDU! Instagram login sayfasına düştü. Manuel refresh gerekli.")
            print("ℹ️  Chrome'dan EditThisCookie ile yeni cookie export et ve ~/.hermes/instagram_cookies.txt'e yaz.")
            browser.close()
            sys.exit(1)
        
        # Write fresh cookies
        write_netscape_cookies(cookie_path, fresh_cookies)
        os.chmod(cookie_path, 0o600)
        
        # Report key cookies
        for c in fresh_cookies:
            if c["name"] in ["sessionid", "csrftoken", "ds_user_id", "rur"]:
                exp_ts = c.get("expires", 0)
                if exp_ts and exp_ts > 0:
                    exp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp_ts))
                else:
                    exp = "session (no expiry)"
                print(f"✅ {c['name']} -> expires: {exp}")
        
        print(f"\n📊 Toplam {len(fresh_cookies)} cookie yenilendi")
        
        browser.close()
        
except Exception as e:
    print(f"❌ HATA: {e}")
    sys.exit(1)
PYEOF

EXIT_CODE=$?

# 5. Verify after refresh
if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=== Post-refresh verification ==="
    grep -q 'sessionid' "$COOKIE_FILE" && echo "✅ sessionid: var" || echo "❌ sessionid: yok"
    grep -q 'csrftoken' "$COOKIE_FILE" && echo "✅ csrftoken: var" || echo "❌ csrftoken: yok"
    
    # Test API call
    CSRF_TOKEN=$(grep 'csrftoken' "$COOKIE_FILE" | awk '{print $NF}')
    echo ""
    echo "🔍 API test yapılıyor..."
    RESULT=$(curl -s --socks5 warp:1080 --max-time 10 \
        "https://www.instagram.com/api/v1/users/web_profile_info/?username=bardopsikoloji" \
        -b "$COOKIE_FILE" \
        -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" \
        -H "X-CSRFToken: $CSRF_TOKEN" \
        -H "X-IG-App-ID: 936619743392459" \
        -H "X-Requested-With: XMLHttpRequest" \
        --compressed 2>&1)
    
    if echo "$RESULT" | grep -q '"status":"ok"'; then
        echo "✅ API test: BAŞARILI (status: ok)"
        echo "✅ Cookie refresh tamamlandı!"
    else
        echo "⚠️  API test: hata"
        echo "--- İlk 500 karakter ---"
        echo "$RESULT" | head -c 500
    fi
else
    echo "❌ Cookie refresh BASARISIZ (exit: $EXIT_CODE)"
fi

echo "=== Done: $(date '+%Y-%m-%d %H:%M:%S') ==="
exit $EXIT_CODE
