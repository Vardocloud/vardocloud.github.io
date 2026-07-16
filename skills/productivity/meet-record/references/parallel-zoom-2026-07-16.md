# Parallel Zoom Recording — 16 Temmuz 2026

## Senaryo
İki Zoom toplantısı eş zamanlı kaydedildi:
- **19:30** — Bilinmeyen konu (port 9333, `zoom_rec`)
- **20:00** — Miuul: Python Airflow ile AI Destekli Veri Pipeline - Enes Öztürk (port 9334, `zoom_rec_2`)

## Ortam
- **PulseAudio**: Custom build (`/tmp/pulseaudio_extract`), socket `/tmp/pulse-PKdhtXMmr18n/native`
- **Xvfb**: `:99`, 1280x1024
- **Chrome**: `chromium` (Debian 13), headless modda çalıştırıldı
- **Python**: websocket-client 1.9.0

## Paralel Kurulum

### PulseAudio
```bash
# Birinci sink PulseAudio başlatılırken yüklendi (default.pa)
# İkinci sink dinamik eklendi:
pactl load-module module-null-sink sink_name=zoom_rec_2
```

### Chrome 9334 (20:00 Miuul)
```bash
PULSE_SINK=zoom_rec_2 DISPLAY=:99 chromium \
  --remote-debugging-port=9334 \
  --user-data-dir=~/.hermes/chrome_profile_zoom_9334 \
  --no-sandbox --disable-gpu --disable-dev-shm-usage \
  about:blank
```

### ffmpeg Kayıtlar
| Process | Input | Output | Format |
|---------|-------|--------|--------|
| PID 361128 (sonra düştü) | `zoom_rec.monitor` | `19_30_toplantisi_16tem2026.mp3` | MP3 128k |
| PID 364418 (video) | `:99 + zoom_rec.monitor` | `miuul_airflow_16tem2026.mp4` | H.264 + AAC |
| PID 366692 (audio) | `zoom_rec_2.monitor` | `miuul_airflow_16tem2026.mp3` | MP3 128k |

### PulseAudio Sink Inputs
- **Sink 0 (zoom_rec)**: Chrome 9333 (PID 361338) — 3 playback stream
- **Sink 1 (zoom_rec_2)**: Chrome 9334 (PID 364215) — 1 playback stream

## Zoom Join Akışı (CDP WebSocket)

### Adımlar
1. Navigate to `https://app.zoom.us/wc/join/<MEETING_ID>?pwd=<PASSCODE>`
2. Wait for page load (~8sn)
3. "Join from browser" sayfası gelir → butona tıkla
4. Sayfa redirect: `app.zoom.us/wc/<MEETING_ID>/join?...`
5. Wait for meeting lobby
6. Fill `input-for-name` with display name (native setter gerekli — React input handler)
7. Click "Mute" → audio off
8. Click "Stop Video" → video off
9. Click "Join" → meeting'e gir
10. Click "Join Audio by Computer" → ses bağlantısı
11. Click "Got It" → mic uyarısını dismiss

### Kullanılan CDP Komutları
```
Page.enable → Runtime.enable → Page.navigate(url)
Runtime.evaluate(expression, returnByValue=true)
```

### Karşılaşılan Sorunlar

| Sorun | Çözüm |
|-------|-------|
| CDP HTTP POST boş döndü | WebSocket kullan (ws://localhost:9334/devtools/page/<ID>) |
| iframe içeriğine erişilemedi | Doğrudan `app.zoom.us/wc/join/...` URL'ine navigate et (launcher'ı bypass et) |
| React input değer değişmiyor | Native value setter kullan (`Object.getOwnPropertyDescriptor`) |
| ffmpeg output 0 byte | `pactl list sink-inputs` ile Chrome'un doğru sink'e bağlı olduğunu kontrol et |
| "Cannot detect your microphone" | Beklenen — fiziksel mic yok. "Got It" ile dismiss et |
| "Continue without microphone and camera" | Dismiss et — kayıt için gerekli değil |

## Toplantı Durumu
- Katılımcı: **Sudenaz**
- Meeting topic: **Python Airflow ile AI Destekli Veri Pipeline Geliştirme Etkinliği**
- Katılımcı sayısı: 83 (aktif)
- Ses: Bilgisayar ses bağlantısı kuruldu (Join Audio by Computer)

## Çıkarımlar
- Paralel kayıt için her Chrome ayrı user-data-dir + ayrı PULSE_SINK
- Video kaydı (x11grab) tüm display'i yakalar — aynı anda iki toplantı görünür
- Audio kaydı için "Join Audio by Computer" tıklanmalı (yoksa Zoom ses stream etmez)
- Mikrofon olmaması sorun değil — sadece dinleme/kayıt modu
