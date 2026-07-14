# Cookie Restore Procedure
> storage_state.json → SQLite Cookie DB restore

## When to Use

When the Chrome profile's `Default/Cookies` SQLite database becomes empty or corrupted (Chrome force-kill, multiple MCP crash cycles), but the Playwright `storage_state.json` export still has valid cookies.

## Check Cookie Health

```bash
# Check storage_state.json cookies
python3 -c "
import json
with open('/home/ubuntu/.notebooklm/profiles/default/storage_state.json') as f:
    d = json.load(f)
print(f'storage_state: {len(d.get(\"cookies\",[]))} cookies')
"

# Check SQLite DB cookies
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/ubuntu/.hermes/chrome_profile_notebooklm/Default/Cookies')
rows = conn.execute('SELECT COUNT(*) FROM cookies').fetchone()
non_empty = conn.execute('SELECT COUNT(*) FROM cookies WHERE value != \"\"').fetchone()
print(f'SQLite DB: {rows[0]} rows, {non_empty[0]} non-empty')
conn.close()
"
```

If SQLite has 0 non-empty cookies but storage_state has 49+ → restore needed.

## Restore

```python
import json, sqlite3

# Read storage state
with open('/home/ubuntu/.notebooklm/profiles/default/storage_state.json') as f:
    state = json.load(f)

cookies = state.get('cookies', [])
db_path = '/home/ubuntu/.hermes/chrome_profile_notebooklm/Default/Cookies'

conn = sqlite3.connect(db_path)
conn.execute('DELETE FROM cookies')  # Clear stale cookies

count = 0
for c in cookies:
    host_key = c.get('domain', '').lstrip('.')
    name = c.get('name', '')
    value = c.get('value', '')
    if not value:
        continue
    path = c.get('path', '/')
    secure = 1 if c.get('secure') else 0
    httponly = 1 if c.get('httpOnly') else 0
    expires = int(c.get('expires', 0))
    same_site = {'Lax': 1, 'Strict': 2, 'None': 3}.get(c.get('sameSite', 'Lax'), 0)
    
    conn.execute('''
        INSERT OR REPLACE INTO cookies 
        (host_key, name, value, path, expires_utc, is_secure, is_httponly, same_site, has_expires)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    ''', (host_key, name, value, path, expires, secure, httponly, same_site))
    count += 1

conn.commit()
conn.close()
print(f'{count} cookies restored to SQLite DB')
```

## Verify

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/ubuntu/.hermes/chrome_profile_notebooklm/Default/Cookies')
non_empty = conn.execute('SELECT COUNT(*) FROM cookies WHERE value != \"\"').fetchone()
print(f'{non_empty[0]} non-empty cookies in DB')
# Check key cookies
for name in ['OSID', '__Secure-OSID', 'SAPISID']:
    val = conn.execute('SELECT value FROM cookies WHERE name=?', (name,)).fetchone()
    print(f'  {name}: {\"...\" if val and val[0] else \"EMPTY\"}')
conn.close()
"
```

## Then Import to nlm

After restoring SQLite DB, export to nlm format and import:

```bash
python3 -c "
import sqlite3, json
conn = sqlite3.connect('/home/ubuntu/.hermes/chrome_profile_notebooklm/Default/Cookies')
rows = conn.execute('SELECT name, value FROM cookies WHERE value != \"\"').fetchall()
cookie_dict = {r[0]: r[1] for r in rows}
with open('/tmp/nlm_cookies.json', 'w') as f:
    json.dump(cookie_dict, f)
print(f'{len(cookie_dict)} cookies exported for nlm')
conn.close()
"

nlm login --manual -f /tmp/nlm_cookies.json
nlm login --check
```

## Pitfalls

- **Chrome must be dead** before modifying SQLite DB - close all Chromium processes first
- **SingletonLock** files prevent SQLite access - delete them: `rm -f ~/.hermes/chrome_profile_notebooklm/Singleton*`
- **expires_utc format** differs between Playwright and Chrome: Playwright uses Unix timestamp (seconds), Chrome uses microseconds since 1601-01-01. The formula: `chrome_expires = (unix_timestamp + 11644473600) * 1000000`. The INSERT above uses the Playwright timestamp directly - Chrome handles the conversion.
- **host_key vs domain**: Playwright's `domain` often starts with `.` (e.g. `.google.com`). Chrome's `host_key` does NOT have a leading dot. Strip it with `.lstrip('.')`.
