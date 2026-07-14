# Instagram DM Automation — Working Playwright Pattern

## Two-Stage DM Send (API Thread + Playwright Message)

Instagram's `direct_v2/create_group_thread` API creates a thread but does NOT deliver the message.
The `broadcast/text` endpoint fails with `useragent mismatch` when called from curl.
**Solution:** Create thread via API, send the actual message via Playwright browser.

### Stage 1: Create thread via API (curl + WARP)

```bash
CSRF=$(grep csrftoken ~/.hermes/instagram_cookies.txt | head -1 | awk '{print $NF}')
UUID=$(python3 -c 'import uuid; print(uuid.uuid4())')

ALL_PROXY=socks5://127.0.0.1:1080 curl -s --max-time 20 \
  -b ~/.hermes/instagram_cookies.txt \
  -H 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)' \
  -H "X-CSRFToken: $CSRF" \
  -H 'X-IG-App-ID: 936619743392459' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
  -d "recipient_users=[\"TARGET_USER_ID\"]&text=test&_csrftoken=${CSRF}&_uuid=${UUID}" \
  'https://www.instagram.com/api/v1/direct_v2/create_group_thread/'
```

Response contains `thread_id`. Extract it with: `python3 -c "import sys,json; print(json.load(sys.stdin)['thread_id'])"`

### Stage 2: Send message via Playwright

```python
import builtins, time, os
from playwright.sync_api import sync_playwright

# Parse Netscape cookies
cookie_path = os.path.expanduser("~/.hermes/instagram_cookies.txt")
cookies = []
with builtins.open(cookie_path) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.strip().split("\t")
        if len(parts) >= 7:
            cookies.append({
                "name": parts[5], "value": parts[6],
                "domain": parts[0], "path": parts[2],
                "secure": parts[3] == "TRUE", "httpOnly": False,
            })

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        proxy={"server": "socks5://127.0.0.1:1080"},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    )
    ctx.add_cookies(cookies)
    page = ctx.new_page()

    thread_id = "340282366841710301244259173000696496060"  # from Stage 1
    page.goto(f"https://www.instagram.com/direct/t/{thread_id}/", wait_until="networkidle", timeout=25000)
    time.sleep(3)

    # Type message
    msg_area = page.locator('[contenteditable="true"], [role="textbox"], textarea').first
    if msg_area.is_visible(timeout=3000):
        msg_area.click()
        time.sleep(0.5)
        msg_area.fill("YOUR MESSAGE HERE")
        time.sleep(1)

        # Click Send
        send_btn = page.locator('button:has-text("Send"), button:has-text("Gonder"), [role="button"]:has-text("Send")').first
        if send_btn.is_visible(timeout=2000):
            send_btn.click()
        else:
            msg_area.press("Enter")

    time.sleep(2)
    page.screenshot(path="/tmp/ig_sent.png")
    browser.close()
```

### Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| `broadcast/text` → `useragent mismatch` | Instagram API UA consistency check | Don't use API for sending — use Playwright |
| `create_group_thread` → empty items | `text` param doesn't deliver message | Separate message send via Playwright |
| Message not delivered to recipient | Thread exists but message wasn't pushed | Check screenshot for sent bubble (blue, right-aligned) |
| `friendships/{id}/following/` → empty | Mutual follow required for private accounts | Must have follow relationship first |

### Getting Target User ID

```bash
ALL_PROXY=socks5://127.0.0.1:1080 curl -s --max-time 15 \
  -b ~/.hermes/instagram_cookies.txt \
  -H 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)' \
  -H 'X-IG-App-ID: 936619743392459' \
  -H 'X-Requested-With: XMLHttpRequest' \
  'https://www.instagram.com/api/v1/users/web_profile_info/?username=TARGET_USERNAME' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['user']['id'])"
```

### Burner Account Detection (Quick Check)

5 signals of a burner account:
- `is_private: true`
- `edge_followed_by.count: 0` (zero followers)
- `edge_follow.count: >= 25` (follows many, followed by none)
- `full_name: ""` (empty display name)
- `biography: ""` (empty bio)
- `edge_owner_to_timeline_media.count: 0` (zero posts)

Confidence: 95% burner if all 6 match.
