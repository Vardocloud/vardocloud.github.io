# 30 Haziran 2026 — Paralel İkili Kayıt + Transkripsiyon

## Özet
Aynı anda iki Zoom semineri kaydedildi: APA (Mentoring as Networking) ve Miuul (İK Analitiği Söyleşisi). İkisi de 20:00'deydi.

## Toplantı Linkleri

**Seminer 1 (APA):** `https://apa-org.zoom.us/w/96791192762?tk=TOKEN&pwd=...&uuid=...`
- Token+passcode webinar (PWA iframe pattern)
- İsim sormadı, sadece passcode ile join oldu
- Host: Tanya Menon, PhD — "Mentoring as Networking"

**Seminer 2 (Miuul):** `https://miuul.zoom.us/j/89746634770?pwd=...`
- Standart meeting landing page
- "Join from Browser" → isim formu (input-for-name) → join
- İsim: "Sudenaz" kullanıldı
- Konu: İK Analitiği Söyleşisi

## PulseAudio Setup

```bash
# 1. null-sink
pactl load-module module-null-sink sink_name=zoom_rec
pactl load-module module-null-sink sink_name=zoom_rec_2

# 2. Chrome'lar wrapper script ile başlat (env kaybını önlemek için)
# /tmp/start_chrome1.sh — PULSE_SINK=zoom_rec, port 9333
# /tmp/start_chrome2.sh — PULSE_SINK=zoom_rec_2, port 9334

# 3. ffmpeg
ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k /home/ubuntu/recordings/seminer_kaydi.mp3
ffmpeg -y -f pulse -i zoom_rec_2.monitor -c:a libmp3lame -b:a 128k /home/ubuntu/recordings/seminer2_kaydi.mp3
```

## Join Flow (PWA Iframe Pattern)

Token+passcode webinar'da meeting client `<iframe id="webclient">` içinde yüklenir:
```python
idoc = iframe.contentDocument || iframe.contentWindow.document
pwd = idoc.getElementById('input-for-pwd')
# passcode gir → join → bekleme odası (otomatik)
```

Normal meeting'de standart form (input-for-name + input-for-pwd).

## Kayıt Süreleri (HATA)

ffmpeg `-t` parametresiz başlatıldığı için seminer bitmesine rağmen kayıt devam etti:
- APA: 3s 33dk (196MB) — seminer ~1.5 saat
- Miuul: 3s 14dk (179MB) — seminer ~1 saat

## Transkripsiyon

Pollinations whisper bakiye yetersiz (0.0012 pollen). Groq Whisper (whisper-large-v3) tercih edilmeli. GROQ_API_KEY konfigüre edilmemiş — Bitwarden'a eklenmesi gerekiyor.

Chunk'lar 20'şer dakikalık parçalara bölündü (APA: 11, Miuul: 10).

## Dersler

1. Seminer bitişi aktif takip edilmedi — Edel uyardı. Sonraki sefer Chrome tab'larını periyodik kontrol et.
2. ffmpeg -t parametresiz çalıştırılmamalı.
3. Background process env wrapper script ile başlatılmalı.
4. Groq Whisper birincil tercih.
