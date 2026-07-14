# CDP + Bitwarden Python Auth Pattern

Lightweight alternative to Playwright — uses Python `websockets` library with Chrome DevTools Protocol directly, with credentials fetched from Bitwarden via BWS + bw CLI.

## Why This Pattern

- **No Playwright dependency** — works with just `pip install websockets`
- **Full CDP access** — DOM query, evaluate JS, input typing, network monitoring
- **Bitwarden integration** — credentials never stored in scripts, pulled live from BW
- **Good for:** simple form-filling, auth flows, cookie export after login

## Alternative: bw-serve REST API (Simpler Credential Retrieval)

Instead of `bws` + `bw unlock` + `bw get item`, use **bw-serve** — it runs on port 8087 and is often already unlocked (auto-started by Hermes entrypoint):

```bash
# Check if unlocked
curl -s http://127.0.0.1:8087/status
# Sync vault first
curl -s -X POST http://127.0.0.1:8087/sync
# List items and get item details (localhost only, no network egress)
curl -s "http://127.0.0.1:8087/list/object/items"
curl -s "http://127.0.0.1:8087/object/item/ITEM_ID"
```

**Advantages over bw CLI subprocess pattern:**
- No session token management (bw-serve remains unlocked via BWS `BW_MASTER_PASSWORD` secret)
- Single HTTP call instead of 3-step CLI (bws → bw unlock → bw get)
- No subprocess overhead
- Works even when `bws` CLI is not installed

**Pre-requisite:** Ensure `bw-serve` is running on localhost:8087. On Hermes container, it's auto-started by entrypoint.sh.

## Requirements

```bash
pip install websockets
# Chrome must be running with --remote-debugging-port
# bws + bw CLI must be configured
```

## Core Pattern: Credential Retrieval

```python
import json, subprocess, os

BWS_BIN = os.path.expanduser('~/.hermes/bin/bws')

def get_creds(item_name="google"):
    """Get username and password from Bitwarden."""
    # 1. Get master password from BWS
    bws = json.loads(subprocess.run([BWS_BIN, 'secret', 'list'],
        capture_output=True, text=True).stdout)
    master = next(s['value'] for s in bws if 'BW_MASTER_PASSWORD' in s['key'])

    # 2. Unlock BW with master password
    env = os.environ.copy()
    env['BW_MASTER'] = master
    unlock = subprocess.run(['bw', 'unlock', '--passwordenv', 'BW_MASTER', '--raw'],
        capture_output=True, text=True, env=env)
    session = unlock.stdout.strip()

    # 3. Get item
    env['BW_SESSION'] = session
    item = subprocess.run(['bw', 'get', 'item', item_name],
        capture_output=True, text=True, env=env)
    data = json.loads(item.stdout)
    return (data.get('login', {}).get('username', ''),
            data.get('login', {}).get('password', ''))
```

## Core Pattern: CDP WebSocket Connection

```python
import asyncio, json, http.client
from websockets import connect

async def cdp(ws, method, params=None, id=1):
    msg = {'id': id, 'method': method}
    if params: msg['params'] = params
    await ws.send(json.dumps(msg))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get('id') == id:
            return resp.get('result', {})

async def eval_js(ws, js):
    """Evaluate JavaScript in page context and return result."""
    result = await cdp(ws, 'Runtime.evaluate', {
        'expression': js,
        'returnByValue': True,
        'awaitPromise': True
    })
    return result.get('result', {}).get('value')

# Get the page WebSocket URL
conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
conn.request('GET', '/json/list')
resp = conn.getresponse()
pages = json.loads(resp.read())
conn.close()

# Find a page or create new
target = next((p for p in pages if 'accounts.google.com' in p.get('url','')), None)
if not target:
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('PUT', '/json/new?url=https://notebooklm.google.com')
    resp = conn.getresponse()
    target = json.loads(resp.read())
    conn.close()

async with connect(target['webSocketDebuggerUrl']) as ws:
    await cdp(ws, 'Page.enable')
    # ... work with page
```

## Google Login Flow via CDP

### Step 0: Handle Account Chooser

Google often shows an **account chooser** before the email input (especially after cookie-based session expiry). Multiple saved accounts are listed as buttons with `data-identifier` attribute:

```python
# Check if account chooser is showing
result = await eval_js(ws, '''
    (function() {
        var el = document.querySelector('[data-identifier="isimgorulsunn@gmail.com"]');
        if(el) { el.click(); return "clicked"; }
        return "not-found";
    })()
''')
if result == "clicked":
    await asyncio.sleep(4)  # wait for password/challenge page
```

Skip to Step 2 (password) after this, as Google goes directly from account chooser to password (or passkey challenge in modern flows).

### Step 1: Fill Email

```python
# Check if email field exists
has_email = await eval_js(ws, '!!document.querySelector("input[type=email]")')

if has_email:
    # Fill email
    await eval_js(ws, f'''
        (function() {{
            var el = document.querySelector("input[type=email]") 
                  || document.querySelector("input[name=identifier]");
            el.focus();
            el.value = {json.dumps(email)};
            el.dispatchEvent(new Event('input', {{bubbles: true}}));
            el.dispatchEvent(new Event('change', {{bubbles: true}}));
        }})()
    ''')
    await asyncio.sleep(1.5)
    
    # Click Next — try multiple selectors
    await eval_js(ws, '''
        (function() {
            var btn = document.querySelector("#identifierNext") 
                   || document.querySelector("button.VfPpkd-LgbsSe");
            if(btn) { btn.click(); return true; }
            return false;
        })()
    ''')
    await asyncio.sleep(4)  # wait for page transition
```

### Step 2: Fill Password

```python
# Wait for password field
await asyncio.sleep(2)
has_pwd = await eval_js(ws, '!!document.querySelector("input[type=password]")')

if has_pwd:
    # Fill using Input.insertText for reliability
    await cdp(ws, 'Runtime.evaluate', {
        'expression': '''
            var pwd = document.querySelector("input[type=password]");
            pwd.focus();
        '''
    })
    await cdp(ws, 'Input.insertText', {'text': password})
    await asyncio.sleep(1)
    
    # Click Next
    await eval_js(ws, '''
        document.querySelector("#passwordNext")?.click();
    ''')
```

**⚠️ CRITICAL:** Use `Input.insertText` (not `value=` assignment) for password fields. Google detects programmatic value assignment and blocks it. `Input.insertText` simulates real keystrokes.

### Step 3: Handle Passkey Challenge

When Google shows "Use your passkey to confirm it's you" (especially after "Too many failed attempts"):

```python
# Check if passkey challenge appeared
url = await eval_js(ws, 'window.location.href')
if 'challenge/pk' in url:
    # Click "Try another way"
    await eval_js(ws, '''
        (function() {
            var btns = document.querySelectorAll('[role="button"], button');
            for(var b of btns) {
                if(b.innerText.includes('Try another way') 
                || b.innerText.includes('Farklı bir yol')) {
                    b.click(); return true;
                }
            }
            return false;
        })()
    ''')
    await asyncio.sleep(2)
    
    # Select "Enter your password"
    await eval_js(ws, '''
        var xpath = "//*[text()='Enter your password']";
        var el = document.evaluate(xpath, document, null, 
            XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        el?.click();
    ''')
    await asyncio.sleep(2)
    
    # Now fill password again
    # ... (same as Step 2)
```

**If passkey challenge persists and user has phone:** The simplest solution is asking the user to approve the passkey prompt on their phone — "Your device will ask for your fingerprint, face, or screen lock". No automation needed.

### Step 4: Handle 2-Step Verification (if user has 2FA enabled)

After the password is accepted, Google may show a **2-Step Verification** page (`/challenge/selection` or `/challenge/dp`) with multiple options:

- **"Tap Yes on your phone or tablet"** — Sends a push notification to the user's phone. **This is the simplest option.** The user receives a notification on their phone, approves it, and the browser automatically proceeds.
- **"Get a verification code from the Google Authenticator app"** — Requires the user to open Google Authenticator.
- **"Try another way"** — Shows additional options (SMS, backup codes, etc.).

**CDP automation for "Tap Yes on your phone or tablet":**

```python
# After password accepted and 2-Step Verification page appears
await asyncio.sleep(2)

# Click "Tap Yes on your phone or tablet"
result = await eval_js(ws, '''
    (function() {
        var all = document.querySelectorAll('[role=link]');
        for(var el of all) {
            var txt = (el.innerText || el.textContent || '').trim();
            if(txt.includes('Tap Yes') || txt === 'Yes on your phone') {
                el.click();
                return "clicked: " + txt;
            }
        }
        return "not-found";
    })()
''')

# Wait for user to approve on phone
await asyncio.sleep(8)

# Check if redirected to destination
final_url = await eval_js(ws, 'window.location.href')
if 'notebooklm' in final_url and 'accounts' not in final_url:
    print("Login successful via phone approval!")
```

The page typically shows a loading state while waiting for the user to approve on their phone. After approval, it redirects to the destination (e.g., notebooklm.google.com).

## Complete Session Cookie Export

After successful login redirects to notebooklm.google.com:

```python
result = await cdp(ws, 'Network.getAllCookies', {})
cookies = result.get('cookies', [])
state_path = os.path.expanduser('~/.hermes/notebooklm_storage_state.json')
with open(state_path, 'w') as f:
    json.dump({'cookies': cookies, 'origins': []}, f, indent=2)
print(f"Saved {len(cookies)} cookies")
```

## Pitfalls

- **`Runtime.evaluate` with `value=` assignment** — Google detects this on password fields. Use `Input.insertText` instead.
- **Page transition delays** — Google's SPA-style login has unpredictable transition times. Use generous `asyncio.sleep()` (3-5s) between steps, not just `waitForSelector`.
- **"Too many failed attempts"** — triggers aggressive passkey prompt. User must either approve on phone or click through "Try another way" → "Enter your password".
- **Continue URL in query params** — `accounts.google.com` URLs often contain `?continue=https://notebooklm.google.com/...` in query params. `if 'notebooklm' in url` will falsely match the continue URL. Check `url.path` or verify absence of `accounts.google.com` in hostname.
- **Page recycling** — if Chrome was used for previous auth attempts, the page may be in a stale state (half-filled forms, expired tokens). Create a new tab with `/json/new` rather than reusing existing pages.
- **No `websockets` in venv** — script must run in an environment with `websockets` installed. Use system Python or ensure venv is active.
