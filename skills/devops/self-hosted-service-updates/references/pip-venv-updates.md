# Pip Paket Güncelleme Stratejisi (Hermes Venv)

Hermes venv'indeki pip paketlerini güncellerken izlenecek güvenli strateji.

## Neden Tek Tek?

Toplu `pip install --upgrade` ile güncellemek bağımlılık çakışmalarına yol açabilir ve gateway'in çalışmaz hale gelmesine neden olabilir. Her paket sonrası gateway kontrolü ile sorun anında tespit edilir.

## Adımlar

### 1. Venv Python'unu Kullan

```bash
# DOĞRU:
~/.hermes/hermes-agent/venv/bin/python -m pip install --upgrade --no-cache-dir <paket>

# YANLIŞ (sistem python'ı):
pip install --upgrade <paket>
source activate && pip install  # PEP 668 nedeniyle çalışmayabilir
```

Venv yolu: `~/.hermes/hermes-agent/venv/` (`.venv` değil!)

### 2. Öncelik Sırası

1. **Güvenlik kritik:** cryptography, certifi, urllib3, idna
2. **Core/Web:** aiohttp, starlette, fastapi, uvicorn, httptools, click
3. **AI/ML:** huggingface_hub, tokenizers, anthropic, ctranslate2
4. **Servis:** boto3, google-auth, google-api-python-client
5. **Diğer:** websockets, yarl, zipp, wrapt, typer, vs.

### 3. ASLA Güncelleme

- `hermes-agent` — kesinlikle dokunma, gateway'i kırar

### 4. Her Parti Sonrası Gateway Kontrolü

```bash
systemctl --user is-active hermes-gateway
```

Gateway çalışıyorsa devam et. Eğer restart gerekirse:

```bash
systemctl --user reset-failed hermes-gateway
systemctl --user start hermes-gateway
sleep 3
systemctl --user is-active hermes-gateway
```

**Pitfall:** `systemctl restart` bazen timeout olur (30s+). `reset-failed` + `start` daha güvenilir.

### 5. Conflict'leri Görmezden Gel

Şu paketlerden gelen conflict uyarıları normaldir, kullanılmıyorlarsa sorun değil:
- `daytona` → aiofiles, websockets
- `alibabacloud-*` → cryptography, aiofiles
- `modal` → synchronicity
- `opentelemetry` → wrapt

### 6. Gateway Restart Stratejisi

Gateway bir kere timeout verirse:
1. `reset-failed` yap
2. `start` yap
3. 3 saniye bekle
4. `is-active` kontrol et

Gateway drain timeout (60s) normaldir — eski process temizlenene kadar bekle.

## Örnek: Tam Güncelleme Akışı

```bash
# 1. Liste al
~/.hermes/hermes-agent/venv/bin/python -m pip list --outdated --no-cache-dir

# 2. Parti 1: Güvenlik
~/.hermes/hermes-agent/venv/bin/python -m pip install --upgrade --no-cache-dir cryptography certifi urllib3 idna

# 3. Gateway kontrol
systemctl --user is-active hermes-gateway

# 4. Parti 2: Core
~/.hermes/hermes-agent/venv/bin/python -m pip install --upgrade --no-cache-dir aiohttp starlette fastapi uvicorn

# 5. Gateway restart (gerekirse)
systemctl --user reset-failed hermes-gateway
systemctl --user start hermes-gateway
sleep 3
systemctl --user is-active hermes-gateway

# ... devam
```
