# No-Agent Sağlık Kontrolü + Fail-Safe Join Bildirim Sistemi

## Ne Zaman Kullanılır

Uzun süren seminer setlerinde (2+ seminer, paralel kayıtlar, tüm gün etkinlikler):
- ffmpeg sessizce ölebilir (Chrome crash, OOM, timeout)
- Join zamanı kaçırılabilir (bekleme modu)
- Edel'e bildirim gitmezse sorun fark edilmez

## No-Agent Health Check Cron

### Pattern
Her 5 dk'da bir ffmpeg process'ini kontrol eden shell script. ffmpeg ölüyse yeniden başlatır.

```bash
#!/bin/bash
# healthcheck_seminer.sh
FFPID=$(pgrep -f "ffmpeg.*zoom_rec" | head -1)
if [ -n "$FFPID" ]; then
    echo "✅ ffmpeg PID=$FFPID çalışıyor"
else
    # Chrome canlı mı kontrol et
    if curl -sf http://localhost:9333/json/version >/dev/null 2>&1; then
        # Part numarasını bul
        PART=1
        while [ -f "/home/ubuntu/recordings/seminer_part${PART}.mp3" ]; do PART=$((PART+1)); done
        nohup ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k \
            -t 00:30:00 "/home/ubuntu/recordings/seminer_part${PART}.mp3" > /tmp/ffmpeg_P${PART}.log 2>&1 &
        echo "⚠️ ffmpeg yeniden başlatıldı (part${PART}, PID $!)"
    else
        echo "⏹️ Chrome da ölü — seminer bitmiş"
    fi
fi
```

### Cron kurulumu
```bash
cronjob action=create \
  name="📼 Sağlık Kontrolü" \
  schedule="5m" \
  script="healthcheck_seminer.sh" \
  repeat=30 \
  no_agent=True \
  deliver=origin
```

### Kurallar
- `no_agent=True` = LLM çağrısı yok, direkt shell script → provider limiti etkilemez
- `repeat=N` ile maksimum tekrar (30 × 5dk = 2.5 saat)
- Her part ayrı dosyaya yaz → ffmpeg crash'inde tüm kayıt gitmez
- Script içinde `nohup ... &` kullan → direkt terminal'de çalışır, `background=true` gerekmez

## No-Agent Join Cron + Fail-Safe Bildirim

### Ne zaman
Her seminer join'inden 10 dk önce tetiklenir. Self-contained Python script join'i dener,
başarısız olursa Edel'e bildirim gönderir.

### Script: `scripts/zoom_autojoin.py`
```bash
# Kullanım
python3 scripts/zoom_autojoin.py "Seminer Adı" "https://zoom.us/j/..." "passcode" "Berkcan Ulucan" 9333

# Cron kurulumu
cronjob action=create \
  name="Join - Seminer Adı" \
  schedule="2026-07-10T21:20:00+03:00" \
  script="zoom_autojoin.py" \
  no_agent=True \
  deliver=origin
```

### Script çıktısı
- `OK` → join başarılı, **sessiz kal** (Edel'e bir şey gitmez)
- `FAIL|sebep` → join başarısız, sebep **Edel'e bildirim olarak gider**

### Fail-Safe Bildirim Formatı (Edel'in gördüğü)
```
🚨 [Seminer Adı]'na giriş YAPILAMADI
⏰ Saat: 21:30
❌ Sebep: Chrome port 9333 ölü / Toplantı bitmiş / PulseAudio yok

Ne yapmalısın: Linki kontrol et veya manuel join dene
```

### 3 Katmanlı Sistem
1. **📋 Todo**: Tüm seminer adımlarını `todo()` aracına gir, sıradaki otomatik gösterilsin
2. **⏰ No-Agent Join Cron**: Join saatine 3dk kala script tetiklenir
3. **🕐 Saat Başı Proaktif Kontrol**: Bekleme moduna geçme, her saat "sıradaki görev ne?" sorgula

## Örnek: 3 Seminerlik Set (10 Tem 2026)

```
Planlama:
  1. APA Webinar (20:00-21:00) → join cron 19:50
  2. YouTube Live (20:00-) → yt-dlp başlat
  3. Çocuk Çizim (21:30-) → join cron 21:20

Health check:
  - APA ve YouTube sağlık kontrolü ayrı cron'lar (5dk, no_agent)
  - YouTube için farklı monitor (zoom_rec_2) ayrı ffmpeg kontrolü

Fail-safe:
  - Her join cron'u başarısız olursa FAIL|sebep döner → Edel görür
  - Sağlık kontrolü ffmpeg ölüyse yeniden başlatır
```
