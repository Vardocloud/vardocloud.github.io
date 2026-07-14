# AuthHealthChecker Debugging — İç İşleyiş ve Teşhis

`nlm login --check` veya `server_info` "stale"/"expired" döndüğünde neyin yanlış gittiğini anlamak için AuthHealthChecker'ın içine nasıl bakılır.

## AuthHealthChecker Mimarisi (v0.7.1+)

İki aşamalı probe stratejisi:

### Phase 1: Homepage Probe
- **Endpoint:** `notebooklm.google.com/` (www.google.com DEĞİL)
- **Headers:** Browser-like (`_PAGE_FETCH_HEADERS`: Sec-Fetch-*, Chrome UA, Accept-Language)
- **Başarı şartı:** Final URL `accounts.google.com` içermemeli + HTTP 200
- **Başarısızlık:** "expired" (redirect to login) veya "http_XXX"

### Phase 2: API Fallback (sadece homepage "expired"/"http_401"/"http_403" ise)
- `NotebookLMClient(cookies, csrf_token).list_notebooks()` çağrılır
- **Başarı şartı:** API exception fırlatmaması
- **Başarı:** "configured" döner (false positive avoided)
- **Başarısızlık:** "stale" verdict

### Final Verdict Logic
```python
if all_network_errors:        → "unverified"  # timeout/connection, belirsiz
elif has_auth_failure:        → "stale"       # gerçek auth sorunu
elif mixed auth + network:    → "unverified"  # kararsız
```

**30 saniye TTL cache** vardır. `nlm login` sonrası cache bypass olur (mtime değişir).

## Debugging Prosedürü

### 1. AuthHealthChecker'ı Doğrudan Çalıştır

```python
import json, os
os.environ['ALL_PROXY'] = ''  # proxy varsa temizle

from notebooklm_tools.services.auth import get_auth_health_checker

checker = get_auth_health_checker()
checker.invalidate()  # cache bypass
report = checker.check(force=True, timeout=15.0)

for p in report.probes:
    print(f"{p.probe}: valid={p.valid}, code={p.status_code}, "
          f"latency={p.latency_ms:.0f}ms, error={p.error}")
print(f"Verdict: {report.status}")
```

### 2. Homepage Fetch'i Doğrudan Test Et

```python
from notebooklm_tools.core.auth import _fetch_notebooklm_homepage

cookies_path = "~/.notebooklm-mcp-cli/profiles/default/cookies.json"
with open(cookies_path) as f:
    cookies = json.load(f)

cookie_dict = {c["name"]: c["value"] for c in cookies if "name" in c and "value" in c}
resp = _fetch_notebooklm_homepage(cookie_dict, timeout=15.0)
print(f"Status: {resp.status_code}")
print(f"Final URL: {resp.url}")
print(f"Redirect to login: {'accounts.google.com' in str(resp.url)}")
```

### 3. API Probe'u Doğrudan Test Et

```python
from notebooklm_tools.core.client import NotebookLMClient

client = NotebookLMClient(cookies=cookie_dict, csrf_token="")
try:
    notebooks = client.list_notebooks()
    print(f"Success: {len(notebooks)} notebooks")
except Exception as e:
    print(f"API failed: {type(e).__name__}: {e}")
```

### 4. CLI'da check_auth'u live=True İle Test Et

```bash
python3 -c "
from notebooklm_tools.core.auth import check_auth
r = check_auth(live=True, timeout=15.0)
print(f'valid={r.valid}, reason={r.reason}')
"
```

## Versiyon Farkı: v0.6.15 vs v0.7.1

| Özellik | v0.6.15 | v0.7.1 |
|---------|---------|--------|
| Probe endpoint | www.google.com (bot detection) | notebooklm.google.com ✅ |
| API fallback | Yok ❌ | Var (Phase 2) ✅ |
| Sec-Fetch-* headers | Eksik | Var ✅ |
| MCP read ops | Cookie valid ise çalışır | Aynı |
| MCP write ops | Auth check bloke eder | Auth check bloke eder | 

**Kritik:** v0.6.15'te Hermes venv'inde olabilir ama pipx'te v0.7.1 yüklü. MCP server hangi venv'den çalışıyorsa o versiyon geçerlidir.

Versiyon kontrolü:
```bash
# MCP server'ın kullandığı versiyon
mcp_notebooklm_mcp_server_info → "version" alanı

# Hermes venv
~/.hermes/hermes-agent/venv/bin/pip show notebooklm-mcp-cli | grep Version

# Pipx
nlm --version
```

## Cookie'lerin Gerçek Durumu

**Cookie expiry timestamps yanıltıcı olabilir.** Bir cookie'nin `expiry` alanı gelecekte olsa bile Google oturumu şu sebeplerle geçersiz olabilir:

1. Şifre değişikliği (tüm session'ları geçersiz kılar)
2. Google hesabından "tüm oturumları kapat"
3. Güvenlik sebebiyle Google'ın token'ı iptal etmesi
4. Cookie'lerin başka bir cihazdan export edilip burada import edilmesi (Google cihaz fingerprint'i değişince şüphelenebilir)

**Doğrulama:** Cookie'lerin expiry'si 9000+ saat olsa bile `_fetch_notebooklm_homepage` hala `accounts.google.com`'a redirect oluyorsa → cookie'ler görünüşte geçerli ama oturum ölü.

## Session ID Debugging

Auth profildeki `session_id` boş olabilir. Önemli cookie'ler:
- `__Secure-3PSID` — ana session token
- `__Secure-3PSIDCC` — session state
- `SID`, `HSID`, `SSID`, `APISID`, `SAPISID` — Google auth cookies

**Duplicate cookie uyarısı:** `cookies.json`'da aynı isimde birden fazla cookie olabilir (farklı domain/path). `_fetch_notebooklm_homepage` bunların hepsini HTTP header olarak gönderir. Bu genelde sorun değildir.

## Kesin Çözüm: Manuel Cookie Export

Auth checker'ı bypass etmenin en güvenilir yolu:

1. **Edel kendi bilgisayarında Chrome'dan cookie export yapar** (EditThisCookie ile)
2. `nlm login --manual -f cookies.json` ile import edilir
3. Eğer bu da çalışmazsa → cookie'ler gerçekten geçersizdir, Google hesabında manuel login gerekir

```bash
# Import
nlm login --manual -f /path/to/cookies.json

# Doğrula
nlm login --check
# → Hala "expired" diyorsa cookie'ler gerçekten ölü
```

## Yaygın Yanılgılar

| Yanılgı | Gerçek |
|---------|--------|
| "Probe www.google.com'a gidiyor, bot detection" | v0.7.1'de notebooklm.google.com'a gider |
| "MCP cache sorunu, refresh_auth çözer" | refresh_auth diskten yeniden yükler, ama cookie ölüyse yine "expired" döner |
| "nlm login --check valid → her şey çalışır" | CLI read testi geçse de yazma ayrı bir token gerektirir |
| "Cookie expiry gelecekte → cookie geçerli" | Google oturumu cookie timestamps'inden bağımsız iptal edilebilir |
