# Cookie Import Procedure (Option A)

En güvenilir auth yöntemi. Kullanıcı kendi tarayıcısından cookie export eder.

## Adımlar

1. Kullanıcı Chrome'da EditThisCookie veya benzeri extension ile cookie export eder
2. Cookies.json dosyasını gönderir
3. Filtrele (HTTP 413 önleme):
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
print(f'{len(cookies)} → {len(filtered)} cookies')
"
```
4. Import et:
```bash
rm -rf ~/.notebooklm-mcp-cli/profiles/default
nlm login --manual -f /tmp/nblm_cookies.json
```

## CookieMismatch Fallback

Cookie import başarısız olursa: Option F (Puppeteer + Bitwarden 2FA) dene.

## Neden Filter?

Full browser export (2000+ cookies, 870KB) HTTP 413 hatası verir. Google domain'lerine filtre (~88KB) sorunu çözer.
