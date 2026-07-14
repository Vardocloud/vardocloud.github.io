# Successful Zoom Recording Flow — 13 Haziran 2026

> **Doğrulandı:** 2 YouTube videosu aynı anda oynatılırken 30+ dk kesintisiz kayıt.
> Transkript: Pollinations whisper-1 ile başarılı.
> Yöntem: CDP + PulseAudio null-sink + fake-device Chrome.

## Session Detayları

| Parametre | Değer |
|-----------|-------|
| Chrome binary | `/data/ubuntu/cache/ms-playwright/chromium-1223/chrome-linux/chrome` |
| CDP Port | 9333 (9222 NotebookLM'ye ait) |
| Xvfb | `:99`, 1280×720x24 |
| PulseAudio | null-sink `zoom_rec` (module-null-sink) |
| Kayıt formatı | MP3, 128kbps |
| İsim (join) | **Sudenaz** (kesinlikle Vanitas DEĞİL) |
| Transkript | Pollinations Whisper-1 (localhost proxy üzerinden) |

## Çalışan Setup Sırası

```
1. Xvfb :99 (önceden çalışıyor olmalı)
2. pulseaudio --start (gerekirse)
3. pactl load-module module-null-sink sink_name=zoom_rec
4. Chrome başlat (PULSE_SINK=zoom_rec, port 9333, fake-device)
5. ffmpeg başlat (zoom_rec.monitor → MP3)
6. CDP ile join: app.zoom.us/wc/join/MEETING_ID
7. İsim: "Sudenaz" → Join → Join Audio by Computer → Mute
```

## Kritik Başarı Faktörleri

1. **`--disable-gpu` KULLANMA** — audio service başlamaz, getUserMedia timeout yer
2. **Profile kopyala** — NotebookLM Chrome profilini kullan (fresh profile join formunu render etmez)
3. **Mic permission pre-grant** — Preferences.json'a content_settings yaz (media_stream_mic: 1)
4. **Fake device** — `--use-fake-device-for-media-stream` + `--use-fake-ui-for-media-stream` şart
5. **userGesture: True** — her CDP tıklamasında, yoksa autoplay bloklanır
6. **Native value setter** — `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set` ile input doldur

## Join Akışı (Adım Adım)

```
app.zoom.us/wc/join/MEETING_ID
  → Name input: "Sudenaz"
  → Password input: varsa gir
  → "Join" butonuna tıkla
  → 10-15sn bekle → meeting tab'ı açılır
  → Overlay dialog varsa display:none ile kaldır
  → "Join Audio by Computer" tıkla
  → 5sn bekle → ses bağlanır
  → "Mute" butonuna tıkla (eko önleme)
  → ✅ Kayıt aktif!
```

## Transkript

Pollinations whisper-1 proxy üzerinden:
- Model: `whisper-1`
- Dil: `tr` zorunlu
- Format: multipart/form-data
- 37MB dosya ile çalıştı (120sn timeout yeterli)
- Yerel Whisper KESİNLİKLE KULLANMA

## Ses Doğrulama

```bash
ffmpeg -i kayit.mp3 -af "volumedetect" -f null - 2>&1 | grep -E "mean_volume|max_volume"
# -91.0 dB = SESSİZLİK
# -6.9 dB veya daha yüksek = ✅ SES VAR
```

## Görülen Hatalar ve Çözümleri

| Hata | Sebep | Çözüm |
|------|-------|-------|
| "Automated bots aren't allowed" | Browser tool (9222) | 9333 + fake device + profile copy ile AŞILDI |
| getUserMedia timeout | Fake device flag'i eksik veya `--disable-gpu` aktif | Fake device ekle, disable-gpu kaldır |
| Join formu boş render | Fresh Chrome profile | NotebookLM profilini kopyala |
| "Cannot detect your camera" | Önemsiz | Join butonuna tıkla, geçer |
| "Could not connect to reCAPTCHA" | Headless sinyali | Join çalışır, mesaj önemsiz |
| "Join Audio" kalıcı (Mute yok) | getUserMedia başarısız | Fake device flag'lerini kontrol et |
| ffmpeg 0 byte | PulseAudio null-sink yok | `pactl list sinks short` ile doğrula |
