# Cookie-Only Auth Blocked from Server IP

## Gözlem (24 Haz 2026)

Google NotebookLM'e cookie-only auth (HTTP client ile) **server IP'sinden çalışmaz**.

## Kanıt

1. `nlm login --manual -f cookies.json` → "Successfully authenticated!" (profil kaydedilir)
2. `nlm list notebooks` → "Authentication expired" / HTTP 413
3. Manuel HTTP test: requests ile aynı cookie'ler gönderilir → `accounts.google.com`'a redirect
4. Chrome CDP'den export edilmiş canlı cookie'ler → yine redirect
5. **Aynı cookie'ler Chrome browser'da çalışır** (VNC'de açık)

## Sebep

Google'ın auth sistemi sadece cookie değerlerini değil, şunları da kontrol eder:
- TLS fingerprint (JA3/JA3S)
- IP address consistency (session IP = request IP olmalı)
- Browser fingerprint (User-Agent, WebGL, fonts, vs.)
- Origin/Referer headers
- Full cookie jar (tüm domain'lerdeki cookie'ler birlikte gönderilmeli)

`__Secure-OSID` ve `__Secure-3PSID` cookie'leri bu fingerprint'e bağlıdır.

## Çalışan Yöntemler

| Yöntem | Nasıl Çalışır | 
|--------|--------------|
| undetected-chromedriver (Selenium) | Real Chrome process, Google kabul eder |
| MCP v2.0.11 + NOTEBOOKLM_PROFILE_DIR | Aynı IP'de Chrome profili kullanılır |
| VNC login → MCP | Aynı IP'de manuel login |
| nlm login (browser açar) | Real Chrome açar, Google kabul eder |

## Çalışmayan Yöntemler

| Yöntem | Neden |
|--------|-------|
| nlm login --manual -f server'dan export | HTTP client, fingerprint yok |
| nlm login --manual -f kullanıcının export'u | Farklı IP + farklı fingerprint |
| CDP export → nlm import | Aynı IP ama farklı HTTP client fingerprint |

## Workaround (Acil Durum)

CDP export → nlm import, Chrome açıkken geçici olarak çalışabilir:

```python
# Chrome CDP'den export
async with websockets.connect(ws_url) as ws:
    await ws.send(json.dumps({"id": 1, "method": "Page.navigate",
        "params": {"url": "https://notebooklm.google.com"}}))
    await asyncio.sleep(3)
    await ws.send(json.dumps({"id": 2, "method": "Network.getAllCookies"}))
    data = json.loads(await ws.recv())
    flat = {c['name']: c['value'] for c in data['result']['cookies']}
    json.dump(flat, open('/tmp/nlm_fresh.json', 'w'))

# nlm import
nlm login --manual -f /tmp/nlm_fresh.json
```

**⚠️ Geçici:** Google session'ı kısa sürede (dakikalar-saatler) geçersiz kılar.
