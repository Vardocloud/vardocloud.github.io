# Per-Hour Split Recording v2 (3 Tem 2026 — 20:00 Kesintisi Düzeltmesi)

## ⚠️ KRİTİK: 20:00 Geçişinde Yaşanan Sorun (2 Tem 2026)

**Olay:** 4 seminerlik etkinlikte 19:00-20:00 geçişinde Chrome crash, 20:00'de ffmpeg kill edilemedi, Vimeo kaydı hiç başlamadı.

**Alınan dersler:**
- **Her saatlik geçiş ÖNCESİ Chrome kontrol et:** `curl -sf localhost:9333/json/version` yanıt vermiyorsa Chrome'u restart et
- **Her saatlik geçiş için no-agent cron yedek kur:** Birincil LLM cron'u + no-agent yedek. Hangisi önce çalışırsa
- **ffmpeg kill ederken `pgrep -f` kullanma** — spesifik PID ile kill et veya ffmpeg'i `-t` ile sınırla
- **20:00 gibi kritik geçişlerde Chrome heartbeat ekle:** Her 5dk'da bir kontrol

## No-Agent Provider Resilience (2 Tem 2026, güncelleme: 3 Tem 2026)

Provider limiti bittiğinde (rate limit, bakiye, model kapalı) LLM çağrısı gerektiren
cron job'lar çalışmaz. Çözüm: kritik zamanlı işlemlerde `no_agent=True` cron job'ları.

## No-Agent Cron Pattern

```bash
cronjob action=create \
  name="📹 Seminer - noagent" \
  schedule="2026-07-02T18:00:00" \
  script="zoom_seminer2.sh"
  no_agent=True \
  deliver=origin
```

## Wrapper Script (Argüman İletmek İçin)

No-agent cron job'ları argüman geçemez. Wrapper script yaz:

```bash
# ~/.hermes/scripts/zoom_seminer2.sh
#!/bin/bash
exec /home/ubuntu/.hermes/scripts/zoom_seminer_switch.sh seminer2_1800
```

## Per-Hour Split Recording Pattern

Aynı Zoom linki üzerinden saat başı seminer olduğunda:

1. Her saat başı cron job'ı → eski ffmpeg'i kill et → yeni ffmpeg başlat (`-t 01:05:00`)
2. Chrome tüm gün açık kalır, sadece ffmpeg değişir
3. Tek seferlik one-shot cron job'ları

```bash
# Önce mevcut ffmpeg'i durdur
kill $(pgrep -f "ffmpeg.*zoom_rec") 2>/dev/null
sleep 2

# Socket doğrula
export PULSE_SERVER="unix:/tmp/pulse-zKO69W804zvm/native"

# Yeni ffmpeg başlat
ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k \
  -t 01:05:00 /home/ubuntu/recordings/kampus_zirvesi/seminer3_1900.mp3
```

## Parallel Dual-Recording Pattern

Aynı anda iki farklı kaynak (Zoom + Vimeo) kaydedileceğinde:

```
Kanal 1: Chrome 9333 → PULSE_SINK=zoom_rec   → ffmpeg → meeting1.mp3
Kanal 2: Chrome 9334 → PULSE_SINK=zoom_rec_2 → ffmpeg → meeting2.mp3
```

### Setup

```bash
# 1. zoom_rec_2 null-sink oluştur
pactl load-module module-null-sink sink_name=zoom_rec_2

# 2. Chrome 9334 başlat (farklı profil + port)
PULSE_SINK=zoom_rec_2 DISPLAY=:99 chromium \
  --no-sandbox --remote-debugging-port=9334 --remote-allow-origins=* \
  --user-data-dir=/tmp/zoom_profile_vimeo \
  --use-fake-device-for-media-stream --use-fake-ui-for-media-stream &

# 3. İki ffmpeg (farklı monitor)
ffmpeg -y -f pulse -i zoom_rec.monitor   -c:a libmp3lame -b:a 128k seminer.mp3 &
ffmpeg -y -f pulse -i zoom_rec_2.monitor -c:a libmp3lame -b:a 128k vimeo.mp3 &
```

### Doğrulama

```bash
# İki ffmpeg de çalışıyor mu?
pgrep -af "ffmpeg.*pulse" | grep -v grep

# İki sink de var mı?
pactl list sinks short | grep zoom_rec
```

## Önemli Kurallar

- `no_agent=True` → script çıktısı doğrudan Edel'e iletilir, LLM yorumu olmaz
- Script'ler **executable** olmalı (`chmod +x`)
- Paralel kayıtta her Chrome'un ayrı PULSE_SINK'i olmalı
- `pkill -f "ffmpeg.*zoom_rec"` ikisini de öldürür — spesifik kill kullan
- **3 Tem 2026:** Saatlik geçişler için `scripts/zoom_switch.sh` kullan. No-agent cron'a uygun wrapper script: `bash /home/ubuntu/.hermes/scripts/zoom_switch.sh seminer2_1800 01:05:00`
