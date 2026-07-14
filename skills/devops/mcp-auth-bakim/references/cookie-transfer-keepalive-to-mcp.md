# Cookie Transfer: Keepalive → MCP Profili

Her iki Chrome aynı binary'yi (sistem Chromium — `executablePath` patch ile sağlanır) kullandığında, cookie'ler SQLite seviyesinde kopyalanabilir.

## SQLite Seviyesinde Kopyalama

```python
import sqlite3, os, time

src_db = os.path.expanduser('~/.hermes/chrome_profile_notebooklm/Default/Cookies')
dst_db = os.path.expanduser('~/.local/share/notebooklm-mcp/chrome_profile/Default/Cookies')

src = sqlite3.connect(src_db)
dst = sqlite3.connect(dst_db)

# Kolonları al
cols = [d[1] for d in src.execute('PRAGMA table_info(cookies)').fetchall()]
col_names = ','.join(cols)
placeholders = ','.join(['?']*len(cols))

# Google cookie'lerini al
rows = src.execute('''
    SELECT * FROM cookies 
    WHERE host_key LIKE '%google%' 
       OR host_key LIKE '%notebooklm%'
       OR host_key LIKE '%accounts.google%'
       OR host_key LIKE '%youtube%'
''').fetchall()

# Hedefteki eski Google cookie'lerini sil
dst.execute('''
    DELETE FROM cookies 
    WHERE host_key LIKE '%google%' 
       OR host_key LIKE '%notebooklm%'
       OR host_key LIKE '%accounts.google%'
       OR host_key LIKE '%youtube%'
''')

# Kopyala
for row in rows:
    str_row = [str(x) if x is not None else None for x in row]
    dst.execute(f'INSERT OR REPLACE INTO cookies ({col_names}) VALUES ({placeholders})', str_row)

dst.commit()
src.close()
dst.close()
```

## storageState.json Formatı

MCP launch sırasında `browser_state/state.json` dosyasını arar. Chrome cookie'lerinden Playwright formatına dönüştürmek için:

```python
WEBKIT_EPOCH = 11644473600

cookies_json = []
for row in rows:
    row_dict = dict(zip(cols, row))
    expires_utc = row_dict.get('expires_utc', 0)
    if expires_utc and expires_utc > 0:
        expires_unix = (expires_utc / 1000000) - WEBKIT_EPOCH
    else:
        expires_unix = -1
    
    cookies_json.append({
        'name': row_dict.get('name', ''),
        'value': row_dict.get('value', ''),
        'domain': row_dict.get('host_key', '').lstrip('.'),
        'path': row_dict.get('path', '/'),
        'expires': expires_unix if expires_unix > 0 else -1,
        'httpOnly': bool(row_dict.get('is_httponly', 0)),
        'secure': bool(row_dict.get('is_secure', 0)),
        'sameSite': {0: 'Strict', 1: 'No_Restriction', 2: 'Lax', 3: 'Strict'}.get(
            row_dict.get('samesite', 0), 'Lax'
        ).capitalize(),
    })

state = {'cookies': cookies_json, 'origins': []}
state_dir = '~/.local/share/notebooklm-mcp/browser_state'
with open(f'{state_dir}/state.json', 'w') as f:
    json.dump(state, f)
```

## Neden symlink çalışmaz?

- ❌ **Cookie çakışması:** İki process aynı profili aynı anda kullanırsa cookie'ler karışır (OpenCode Windows deneyimi)
- ❌ **Singleton lock:** Chrome profili kilitlenir, ikinci process açamaz
- ❌ **encrypted_value:** Bundled Chromium farklı anahtarla şifrelediği için, sistem Chromium'unun cookie'lerini çözemez (executablePath patch'i olmadan)

## Süreç

1. executablePath patch uygula → ikisi aynı binary
2. Keepalive'de auth sağla (VNC/manuel giriş)
3. Cookie'leri SQLite ile MCP profiline kopyala
4. storageState.json da oluştur (MCP lazy init için)
5. MCP `ask_question` test et
