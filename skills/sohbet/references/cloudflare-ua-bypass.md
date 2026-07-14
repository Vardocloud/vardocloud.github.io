# Cloudflare UA Bypass — Pollinations 403 Çözümü

## Kök Neden
Cloudflare browser signature ban (error 1010). Python'un varsayılan User-Agent'ı (`Python-urllib/3.x`) bloklanıyor.

## Yanlış Teşhis Zinciri (30 Mayıs 2026 — 3 saat)
İçerik filtresi → Pollinations-Safe header → system prompt kısaltma → tool sayısı düşürme → model değiştirme.
**Hiçbiri gerekli değildi.** Tek sorun User-Agent'tı.

## Çözüm
Basit HTTP proxy (systemd servis). Sadece browser UA header'ı ekler, başka manipülasyon yapmaz.

### Proxy: `~/.hermes/scripts/pollinations-proxy.py`
```python
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36..."
req.add_header("User-Agent", UA)
```

### Systemd: `~/.config/systemd/user/pollinations-proxy.service`
```ini
ExecStart=/path/to/venv/bin/python3 ~/.hermes/scripts/pollinations-proxy.py
Restart=always
```

### Config yönlendirmeleri
```bash
hermes config set delegation.base_url "http://127.0.0.1:19999/v1"
hermes config set auxiliary.vision.base_url "http://127.0.0.1:19999/v1"
hermes config set auxiliary.web_extract.base_url "http://127.0.0.1:19999/v1"
hermes config set auxiliary.compression.base_url "http://127.0.0.1:19999/v1"
hermes config set auxiliary.approval.base_url "http://127.0.0.1:19999/v1"
hermes config set auxiliary.session_search.base_url "http://127.0.0.1:19999/v1"
hermes config set tts.openai.base_url "http://127.0.0.1:19999/v1"
```

## Debugging Dersi
403/block alınınca → ÖNCE HTTP katmanını kontrol et (UA, Cloudflare, IP, rate-limit).
SONRA içerik/prompt'a bak. En basit açıklama genellikle doğrudur (Occam's razor).

## Proxy Auth Injection (30 Mayıs 2026)

`hermes -z` modu Pollinations provider'ında **sessizce başarısız oluyor** — API key göndermiyor.
Çözüm: Proxy artık gelen isteklerde Authorization header'ı yoksa **.env'den okuduğu API key'i otomatik ekler.**

```python
if API_KEY and 'authorization' not in [h.lower() for h, _ in s.headers.items()]:
    req.add_header('Authorization', f'Bearer {API_KEY}')
```

Bu sayede `light_agent.py` gibi direkt API çağıran araçlar auth'suz çalışabilir.
**Not:** `hermes -z` yine de Pollinations ile çalışmaz — `hermes chat` çalışır ama `-z` sessiz kalır.
Sebebi bulunamadı. DeepSeek provider ile `hermes -z` çalışıyor.
