# Cloudflare Quick Tunnel — Voice Agent Deployment

> **Tarih:** 5 Temmuz 2026
> **İlgili:** v13.1, `~/vanitas-web/server.mjs` (port 3005)
> **Binary:** `~/.hermes/bin/cloudflared` (tam path background'da gerekli)

## Amaç

Voice Agent'a (127.0.0.1:3005) dışarıdan HTTPS ile erişmek için Cloudflare quick tunnel. Telefon/tabletten test için gerekli — Web Speech API (STT) HTTPS zorunluluğu, tunnel ile çözülür.

## Tunnel Başlatma

```bash
# Quick tunnel (en basit, auth gerekmez)
cloudflared tunnel --url http://127.0.0.1:3005 --no-autoupdate
```

**ÖNEMLİ — PATH sorunu:** Background process'te PATH inherit edilmez. `~/.hermes/bin/cloudflared` tam path'i kullan:

```bash
# Background (Hermes terminal background=true ile)
/home/ubuntu/.hermes/bin/cloudflared tunnel --url http://127.0.0.1:3005 --no-autoupdate
```

Tunnel oluşunca log'da `https://<random>.trycloudflare.com` URL'i görünür. Bu URL ephemeral'dir — cloudflared restart'ında değişir.

### Doğrulama

```bash
# Tunnel başarılı oldu mu?
curl -s -o /dev/null -w "HTTP %{http_code}, Time: %{time_total}s" https://<tunnel-url>/
# → HTTP 200, ~21KB HTML dönmeli

# Sağlık kontrolü — tüm endpoint'ler
curl -s -X POST https://<tunnel-url>/api/heartbeat \
  -H 'Content-Type: application/json' \
  -d '{"command":"summary"}' | python3 -m json.tool
```

## Uyumluluk Matrisi

| Özellik | Tunnel'den Geçer mi? | Açıklama |
|---------|---------------------|----------|
| **SSE Streaming** (POST /api/chat) | ✅ | Cloudflare QUIC/HTTP2 üzerinden sorunsuz |
| **Binary MP3** (POST /api/tts) | ✅ | Binary passthrough çalışır |
| **JSON API** (POST /api/heartbeat) | ✅ | Standart HTTP, problemsiz |
| **CORS** | ✅ | Server'daki `Access-Control-Allow-Origin: *` cloudflared'den geçer |
| **Web Speech API (STT)** | ✅ | Tarayıcıda local çalışır, tunnel sadece HTTPS sağlar |
| **MediaRecorder** | ✅ | HTTPS yeterli — tunnel sağlar |
| **Static dosyalar** (GET /) | ✅ | 21KB index.html, tüm asset'ler |
| **OPTIONS preflight** | ✅ | HTTP 204 döner |
| **Voiceprint proxy** | ⚠️ | 5050 portu çalışıyorsa geçer |

### Sınırlamalar

- **Ephemeral URL:** Her restart'ta URL değişir → production için named tunnel gerekir
- **Uptime garantisi yok:** Cloudflare "account-less" tunnel'ların garantisi yoktur
- **QUIC protocol:** Varsayılan `quic`, düşmezse `http2`'ye fallback yapar

### Otomatik Kurtarma (Watchdog)

Tunnel kapanırsa (process crash, container restart) otomatik başlaması için:

**No-agent cron watchdog:** `voice_watchdog.sh` (her 2 dk, job ID: 41d2e0671bd6)
- cloudflared process'ini kontrol eder, kapalıysa başlatır
- Yeni tunnel URL'ini `~/.hermes/data/voice_tunnel_url.txt`'ye kaydeder
- URL değiştiyse Telegram'dan bildirim gönderir

**Startup:** `~/.hermes/scripts/voice_startup.sh` → SSH login'de `~/.profile` ile çalışır

Detaylı watchdog dokümanı: `references/service-persistence.md`

## Test Protokolü (Deployment Sonrası)

Yeni tunnel açıldığında veya voice agent restart edildiğinde sırasıyla:

### Adım 1: Backend Endpoint'ler
```bash
T="https://<tunnel-url>"

# 1a. Heartbeat summary
curl -s -X POST $T/api/heartbeat -H 'Content-Type: application/json' \
  -d '{"command":"summary"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])"

# 1b. TTS binary output
curl -s -X POST $T/api/tts -H 'Content-Type: application/json' \
  -d '{"text":"test"}' -o /tmp/tts_test_tunnel.mp3 && stat -c%s /tmp/tts_test_tunnel.mp3

# 1c. Chat stream (SSE)
curl -s -X POST $T/api/chat -H 'Content-Type: application/json' \
  -d '{"message":"Merhaba"}' | head -3

# 1d. Voiceprint endpoint (ulaşılabilirlik)
curl -s -o /dev/null -w "%{http_code}" -X POST $T/api/voiceprint/verify \
  -H 'Content-Type: application/octet-stream' --data-binary @/dev/null
```

### Adım 2: Frontend Routing
Voice agent sayfasını aç, şu komutları dene:
1. "son task durumu" → heartbeat summary dönmeli
2. "hata raporu" → failures dönmeli
3. "poc-supervisor durumu" → query dönmeli
4. "merhaba" → normal Groq sohbet (heartbeat'e karışmamalı)

### Adım 3: CORS ve Header'lar
```bash
# CORS preflight
curl -s -D - -o /dev/null -X OPTIONS $T/api/heartbeat | grep -i access-control

# Content-Type
curl -s -D - -o /dev/null $T/ | grep -i content-type
```

## Pitfall: Background PATH Sorunu

`terminal(background=true)` ile cloudflared başlatırken PATH mekanizması devre dışıdır. `cloudflared` komutu bulunamaz (exit code 127).

**Çözüm:** Tam path kullan:
```bash
/home/ubuntu/.hermes/bin/cloudflared tunnel --url http://127.0.0.1:3005 --no-autoupdate
```

## Pitfall: Output Buffer

Cloudflared background'da çalışırken stdout buffered olur — tunnel URL'i `process(action='poll')` ile hemen görünmeyebilir. `process(action='log')` ile 5-10sn sonra tüm log'u oku.

Detaylı output buffer sorunu: `references/cloudflared-silent-failure.md`

## Alternatif: Named Tunnel (Production)

Quick tunnel yerine kalıcı URL için:
```bash
# Cloudflare Zero Trust hesabı gerekli
cloudflared tunnel login           # browser auth
cloudflared tunnel create vanitas-voice
cloudflared tunnel route dns vanitas-voice voice.vanitas.example.com
cloudflared tunnel run vanitas-voice
```

Named tunnel'da cert, domain ve DNS yapılandırması gerekir — quick tunnel test için yeterlidir.
