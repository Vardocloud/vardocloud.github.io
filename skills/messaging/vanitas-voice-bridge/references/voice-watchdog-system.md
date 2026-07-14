# Voice Service Watchdog & Kalıcı Servis Sistemi

Kurulum: 5 Temmuz 2026. Tüm servisler container restart'ında otomatik başlar.

## Bileşenler

### 1. Voice Watchdog Script
Path: `~/.hermes/scripts/voice_watchdog.sh`
Tip: no-agent cron script (her 2 dk'da bir çalışır)
Davranış: Her şey çalışıyorsa sessiz (çıktı yok). Sorun varsa Telegram'a bildirim.

Kontrol ettiği servisler:
- Voice Agent (port 3005) — `curl -sf --max-time 5 http://127.0.0.1:3005/`
- Voiceprint Service (port 5050) — `curl -sf http://127.0.0.1:5050/health`
- Cloudflare Tunnel — `pgrep -f "cloudflared tunnel --url http://127.0.0.1:3005"`

### 2. Voice Startup Script
Path: `~/.hermes/scripts/voice_startup.sh`
Tetikleyici: `~/.profile` (login shell) ve watchdog cron (container restart)
Sıra: Voice Agent check → Voiceprint → Cloudflare Tunnel
Log: `~/.hermes/logs/voice_startup.log`

**⚠️ Startup Race Condition Fix (5 Tem 2026):** `~/.profile` her bash login'de çalışır. Eğer bir background process `node server.mjs` komutuyla başlatılırsa, önce `~/.profile` → `voice_startup.sh` çalışır, sonra asıl `node server.mjs` çalışır → **EADDRINUSE**. Çözüm:

- `voice_startup.sh` artık **node server'ı arkaplanda başlatmaz** — sadece port kontrolü yapar, watchdog 2dk içinde başlatır
- `/tmp/voice_startup.lock` dosya kilidi eklendi: aynı anda iki kere çalışmasını engeller
- `~/.profile`'da `[[ $- == *i* ]]` kontrolü olmalı (sadece interaktif shell'de çalıştırır) — ancak `.profile` korumalı dosya olduğu için manuel güncellenemedi

**Etki:** EADDRINUSE hataları artık oluşmaz. Container restart'ında ilk 2 dakika boyunca voice agent kapalı kalabilir, watchdog başlatır.

### 3. Cron Job
Job ID: `41d2e0671bd6`
İsim: "🎙️ Voice Servis Watchdog"
Schedule: `*/2 * * * *` (every 2 minutes)
Script: `voice_watchdog.sh`
Tip: `no_agent=true` (LLM çağrısı yok, direkt script çıktısı)
Kalıcılık: `.hermes` Windows diskinde (`C:\` mount), container restart'ında kaybolmaz.

### 4. Tunnel URL Tracking
- Güncel URL: `~/.hermes/data/voice_tunnel_url.txt`
- Önceki URL: `~/.hermes/data/voice_last_tunnel.txt` (değişiklik tespiti için)
- Watchdog URL değişirse bildirim gönderir.

## Container Restart Davranışı
1. Container başlar → entrypoint.sh Hermes gateway'i başlatır
2. Cron scheduler yüklenir → Voice Watchdog 2dk içinde çalışır
3. Watchdog tüm servisleri sırayla başlatır
4. `~/.profile` login shell'lerde startup'ı hemen tetikler

## Manuel Kullanım
```bash
# Tüm servisleri başlat
bash ~/.hermes/scripts/voice_startup.sh

# Güncel tunnel URL
cat ~/.hermes/data/voice_tunnel_url.txt
```
