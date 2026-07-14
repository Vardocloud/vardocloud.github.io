# Service Persistence — Voice Watchdog & Startup

> **Tarih:** 5 Temmuz 2026
> **İlgili:** v13.1, container ortamı (WSL/Docker)
> **Cron Job ID:** 41d2e0671bd6
> **Scripts:** `~/.hermes/scripts/voice_watchdog.sh`, `voice_startup.sh`

## Amaç

Voice agent (port 3005), voiceprint (port 5050) ve cloudflare tunnel'in container restart veya process crash sonrası otomatik olarak ayağa kalkmasını sağlamak. Edel'in "tünel uyumluluğa dikkat et" talebi üzerine geliştirildi.

## Mimari

```
┌──────────────────────────────────────────────────────────┐
│                    Docker Container                       │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Voice Agent  │  │  Voiceprint  │  │ Cloudflare     │ │
│  │ :3005        │  │  :5050       │  │ Tunnel         │ │
│  │ server.mjs   │  │  voiceprint_ │  │ (trycloudflare)│ │
│  │              │  │  service.py  │  │                │ │
│  └──────┬───────┘  └──────┬───────┘  └───────┬────────┘ │
│         │                 │                   │          │
│         └────────────┬────┴───────────────────┘          │
│                      │                                   │
│              ┌───────┴────────┐                          │
│              │  Watchdog      │  ← cron (her 2 dk)       │
│              │  voice_watch-  │  ← ~/.profile (SSH)      │
│              │  dog.sh        │                          │
│              └────────────────┘                          │
└──────────────────────────────────────────────────────────┘
```

## Script: `voice_watchdog.sh`

**Konum:** `~/.hermes/scripts/voice_watchdog.sh`
**Trigger:** Cron job ID `41d2e0671bd6`, schedule `*/2 * * * *` (her 2 dk)
**Tür:** no-agent cron (çıktısı boşsa sessiz, doluysa Telegram'a bildirim)

### Kontrol Ettiği Servisler

| Servis | Port | Kontrol Yöntemi |
|--------|------|----------------|
| Voice Agent | 3005 | `curl -sf http://127.0.0.1:3005/` |
| Voiceprint | 5050 | `curl -sf http://127.0.0.1:5050/health` |
| Cloudflare Tunnel | — | `pgrep -f "cloudflared tunnel --url http://127.0.0.1:3005"` |

### Davranış

- **Her şey çalışıyorken:** stdout boş → cron sessiz geçer, bildirim GİTMEZ
- **Bir servis kapalıysa:** Başlatır, stdout'a yazar → Telegram'a bildirim düşer
- **Tunnel URL değiştiyse:** Yeni URL'i `~/.hermes/data/voice_tunnel_url.txt`'ye kaydeder

### Çıktı Formatı

```
🔊 Voice Watchdog: Voice Agent yeniden başlatıldı. Tunnel yeniden başlatıldı: https://xxx.trycloudflare.com
```

## Script: `voice_startup.sh`

**Konum:** `~/.hermes/scripts/voice_startup.sh`
**Trigger:** `~/.profile` (SSH login), ayrıca manuel de çağrılabilir
**Log:** `~/.hermes/logs/voice_startup.log`

### Yaptıkları (sırayla)

1. Voice Agent (server.mjs) — port 3005 kontrol, yoksa nohup ile başlat
2. Voiceprint (voiceprint_service.py) — port 5050 kontrol, yoksa başlat
3. Cloudflare tunnel — process kontrol, yoksa `cloudflared tunnel --url` ile başlat

### Akış

```
voice_startup.sh → servisleri sırayla kontrol et
  ├── Voice Agent çalışıyor mu? → hayır → nohup node server.mjs
  ├── Voiceprint çalışıyor mu? → hayır → nohup python3 voiceprint_service.py
  └── Tunnel çalışıyor mu? → hayır → nohup cloudflared tunnel --url ...
```

## Cron Job Detayları

- **Job ID:** `41d2e0671bd6`
- **İsim:** 🎙️ Voice Servis Watchdog
- **Schedule:** `*/2 * * * *` (her 2 dakikada bir)
- **Tip:** no_agent=true (sadece script çalıştırır, LLM çağrısı yok)
- **Script:** `voice_watchdog.sh`
- **Deliver:** `origin` (Telegram'a bildirim)
- **Kalıcılık:** Hermes cron DB'si Windows diskinde (C:\) — container restart'ında kaybolmaz

### No-Agent Cron Davranışı

- Non-empty stdout → mesaj olarak Telegram'a iletilir
- Empty stdout → SESSİZ geçer (hiçbir şey gönderilmez, bildirim yok)
- Non-zero exit → hata bildirimi
- Timeout → hata bildirimi

## Container Restart Akışı (Uçtan Uca)

```
Container Start
  ↓
entrypoint.sh (read-only host mount)
  ├── Xvfb, SSH, BW, Chrome, proxies, dashboard...
  └── Hermes Gateway (foreground)
        ↓
Gateway → cron scheduler → watchdog job aktif
  ↓ (max 2 dk içinde)
voice_watchdog.sh çalışır
  ├── Voice Agent kapalı → başlatır
  ├── Voiceprint kapalı → başlatır
  └── Tunnel kapalı → başlatır + URL kaydeder
  ↓
Eğer SSH ile girilirse → ~/.profile → voice_startup.sh anında çalışır
```

## Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `~/.hermes/scripts/voice_watchdog.sh` | Cron watchdog script (3433 bytes) |
| `~/.hermes/scripts/voice_startup.sh` | Startup script (2301 bytes) |
| `~/.hermes/logs/voice_watchdog.log` | Watchdog logları |
| `~/.hermes/logs/voice_startup.log` | Startup logları |
| `~/.hermes/data/voice_tunnel_url.txt` | Son tunnel URL (kalıcı) |
| `~/.hermes/data/voice_last_tunnel.txt` | Önceki tunnel URL (değişim tespiti) |

## Pitfall: Background PATH Sorunu

`terminal(background=true)` ile cloudflared başlatırken PATH inherit edilmez:
```bash
# ÇALIŞMAZ — cloudflared not found (exit 127)
cloudflared tunnel --url http://127.0.0.1:3005

# ÇALIŞIR — tam path
/home/ubuntu/.hermes/bin/cloudflared tunnel --url http://127.0.0.1:3005
```

Watchdog script'i bu sorunu çözer: `CLOUDFLARED="/home/ubuntu/.hermes/bin/cloudflared"` ile tam path kullanır.

## Pitfall: Entrypoint Read-Only

`/usr/local/bin/entrypoint.sh` Windows host'tan read-only mount edilmiştir (C:\ üzerinden 9p). Container içinden DEĞİŞTİRİLEMEZ. Bu yüzden watchdog + ~/.profile yaklaşımı kullanılır.
