# Provider Fallback Testing — 3 Kademeli Yapı (2 Temmuz 2026)

## Mimari

```
Ana: opencode-go (deepseek-v4-flash) → rate limit/bayat model
  ├─ 1. opencode-zen (deepseek-v4-flash-free) — ücretsiz, hızlı
  ├─ 2. Pollinations (deepseek) — ücretsiz proxy, stabil
  └─ 3. openrouter/free — son çare
```

## Kurulum

```bash
hermes config set fallback_providers '[
  {"model":"deepseek-v4-flash-free","provider":"opencode-zen"},
  {"model":"deepseek","provider":"Pollinations"},
  {"model":"openrouter/free","provider":"openrouter"}
]'
```

Config'de şu provider'ların tanımlı olması gerekir:
- `opencode-go` — base_url: http://127.0.0.1:19998/v1, model: deepseek-v4-flash
- `Pollinations` — base_url: http://127.0.0.1:19999/v1, model: deepseek
- `opencode-zen` — base_url: https://opencode.ai/zen/v1, model: deepseek-v4-flash-free
- `openrouter` — built-in (özel config gerekmez)

## Test Metodolojisi

Her fallback provider'a chat completion isteği atarak cevap ürettiğini doğrula:

```python
import urllib.request, json

def test_provider(url, model, api_key=None, prompt="Sadece Evet yaz"):
    data = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 10
    }).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return ("✅", content)
    except Exception as e:
        return ("❌", str(e)[:150])
```

### BWS Environment ile Test

```bash
# Script yaz, bws run ile çalıştır (env var'ları otomatik set edilir)
bws run -- python3 /tmp/test_provider.py
```

## Test Results (2 Temmuz 2026)

| Provider | Endpoint | Model | Sonuç |
|----------|----------|-------|-------|
| Pollinations | http://127.0.0.1:19999/v1 | deepseek | ✅ Çalışıyor, cevap üretiyor |
| opencode-zen | https://opencode.ai/zen/v1 | deepseek-v4-flash-free | ⚠️ Dışarıdan 403 (error 1010), Hermes üzerinden çalışıyor |
| openrouter/free | https://openrouter.ai/api/v1 | openrouter/free | ⚠️ OPENROUTER_API_KEY env'de yok (LITEROUTER_API_KEY var) |

### Bilinen Sorunlar

**opencode-zen 403 (error code: 1010):**
- OpenAI uyumlu endpoint'ten direkt test edince 403 dönüyor (OpenRouter error 1010 = "No available model provider" veya IP kısıtlaması)
- Hermes container'ı üzerinden (cron job'larında) başarıyla çalışıyor — muhtemelen farklı network katmanı veya User-Agent farkı
- Cron job'larında kullanımı güvenli: Ekonomi Zekası, Skool, LinkedIn job'ları opencode-zen ile sorunsuz çalışıyor
- **Aksiyon gerekmez** — dışarıdan test edilemez ama Hermes içinde çalışır

**openrouter/free — OPENROUTER_API_KEY eksik:**
- BWS'de `OPENROUTER_API_KEY` diye bir secret yok, sadece `LITEROUTER_API_KEY` var (64 char hex)
- `LITEROUTER_API_KEY` Hermes tarafından environment'a ekleniyor ama `OPENROUTER_API_KEY` olarak değil
- Eğer Hermes openrouter provider'ı için `OPENROUTER_API_KEY` arıyorsa, LITEROUTER_API_KEY map edilmiyor olabilir
- **Aksiyon:** openrouter/free fallback'te kalabilir ama çalışıp çalışmadığı şüpheli. Gerekirse BWS'e OPENROUTER_API_KEY ekle veya fallback'ten çıkar

## Provider Sağlığı Periyodik Kontrol

Provider'ların ayakta olduğunu doğrulamak için models endpoint'ini sorgula:

```bash
# opencode-go
curl -s -w "\nHTTP %{http_code}" http://127.0.0.1:19998/v1/models -m 5

# opencode-zen
curl -s -w "\nHTTP %{http_code}" https://opencode.ai/zen/v1/models -m 5

# Pollinations
curl -s -w "\nHTTP %{http_code}" http://127.0.0.1:19999/v1/models -m 5
```

Tümü 200 dönmelidir. Models listesi 200 dönüyorsa provider ayaktadır, chat completion'daki hata başka bir sebeptendir (API key, model adı, rate limit).

## Fallback Davranışı

Hermes fallback mekanizması:
1. Ana provider (`opencode-go`) istek gönderemezse (rate limit, timeout, 5xx) → sıradaki fallback'e geçer
2. Her fallback sırayla denenir
3. Biri başarılı olursa onunla devam eder
4. Hiçbiri çalışmazsa hata döner

Fallback **otomatiktir** — manuel müdahale gerekmez. Ancak cron job'larında:
- Her cron job'ı bağımsız bir oturum açar
- Her oturum ana provider'ı dener, fallback'e düşerse o oturum için fallback kullanılır
- Sonraki cron job'ı yine ana provider'ı dener
