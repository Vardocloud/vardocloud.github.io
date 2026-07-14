# Cookie Import via Playwright Storage State (Simpler Method)

## Why This Method?

The SQLite cookie import method (`references/cookie-import-procedure.md`) requires writing directly to Chrome's SQLite Cookies database with the correct schema. The **Playwright storage_state** method is simpler: it's a plain JSON file that Playwright-based tools (including notebooklm-mcp) natively understand.

## Workflow

```
User exports cookies (Cookie-Editor) → JSON → Convert to storage_state.json
→ Save to profile directory → Restart MCP server → Auth OK
```

## Step 1: User Exports Cookies

User opens `notebooklm.google.com` in their own Chrome:

1. Install [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) extension
2. Go to notebooklm.google.com (must be logged in)
3. Click Cookie-Editor icon → "Export" (bottom) → copies JSON to clipboard
4. Sends the JSON to Vanitas

## Step 2: Convert to Playwright Storage State

```python
import json

# Read Cookie-Editor export (may have "1|" prefix)
with open('cookies.json') as f:
    raw = f.read()
if raw[0].isdigit() and raw[1] == '|':
    raw = raw[2:]
source_cookies = json.loads(raw)

# Convert to Playwright storage_state format
playwright_cookies = []
for c in source_cookies:
    domain = c.get('domain', '')
    # Filter: only Google/NotebookLM domains
    if not any(d in domain for d in [
        'notebooklm.google.com', '.google.com', 'accounts.google.com', 'google.com'
    ]):
        continue

    expires = c.get('expirationDate', 1815554133) or 1815554133
    ss = c.get('sameSite', 'unspecified')
    if ss in ('unspecified', 'no_restriction'):
        ss = 'None'

    playwright_cookies.append({
        'name': c['name'],
        'value': c['value'],
        'domain': domain,
        'path': c.get('path', '/'),
        'expires': int(expires),
        'httpOnly': c.get('httpOnly', False),
        'secure': c.get('secure', False) or domain.startswith('.'),
        'sameSite': ss
    })

storage_state = {'cookies': playwright_cookies, 'origins': []}

# Save to the MCP server's profile directory
output_path = '/home/ubuntu/.notebooklm/profiles/default/storage_state.json'
with open(output_path, 'w') as f:
    json.dump(storage_state, f, indent=2)
```

Key details:
- Total cookies → ~200 Google cookies, including ~4 notebooklm-specific
- The `expires` field must be an integer Unix timestamp, not Chrome format
- `sameSite` values: Cookie-Editor uses `no_restriction`/`unspecified`, convert to Playwright's `None`
- `secure` should be `true` for domain cookies starting with `.`

## Step 3: Save to Profile

The storage_state.json goes in the notebooklm-mcp profile directory:

```bash
~/.notebooklm/profiles/default/storage_state.json
```

Also save a backup:
```bash
~/.notebooklm/profiles/default/backups/storage_state_manual_import.json
```

## Step 4: Restart and Verify

1. **Kill old process:**
   ```bash
   kill <notebooklm-mcp PID>
   ```

2. **Restart server:**
   ```bash
   notebooklm-mcp server --headless -n <NOTEBOOK_ID> &
   ```

3. **Test auth:**
   ```bash
   notebooklm-mcp test -n <NOTEBOOK_ID>
   ```
   Expected output:
   ```
   ✅ Browser started successfully
   ✅ Loaded N cookies from storage_state
   ✅ Already authenticated via persistent session!
   ✅ Authentication successful
   ✅ Navigated to: https://notebooklm.google.com/notebook/<NOTEBOOK_ID>
   All tests passed!
   ```

4. **MCP healthcheck should return:**
   ```json
   {"status": "healthy", "authenticated": true}
   ```

## Comparison: SQLite vs Storage State

| Aspect | SQLite Method | Storage State Method (✅ Simpler) |
|--------|--------------|----------------------------------|
| Complexity | Need Chrome schema, column mapping, Chrome timestamps | Plain JSON, direct field mapping |
| Error prone | Schema changes between Chrome versions, INSERT failures | Schema-independent |
| Speed | ~3-5 minutes | ~30 seconds |
| Readability | Binary SQLite, can't inspect | Plain JSON, human-readable |
| Persistence | Survives any server restart | Survives any server restart |
| Tooling | Requires `sqlite3` Python package | No special tools |

## When to Use Each

- **Storage State method (PREFERRED):** When the notebooklm-mcp server reads from `~/.notebooklm/profiles/default/` (Playwright-based storage). This is the current setup.
- **SQLite method:** Only if the MCP server uses a raw Chrome profile (`/tmp/chrome_profile_*`) and doesn't support storage_state. Unlikely with current notebooklm-mcp versions.
