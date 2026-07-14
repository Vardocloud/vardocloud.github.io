# Pipeline Test — 13 Haziran 2026

## Setup
- Chrome 9333, PulseAudio zoom_rec null-sink, ffmpeg MP3
- Xvfb :99, fake-device flag'leri

## Test Sonuçları

### getUserMedia
- 3 fake audio cihazı: "Fake Default Audio Input", "Fake Audio Input 1", "Fake Audio Input 2"
- navigator.mediaDevices yalnızca HTTP/HTTPS sayfalarında var (about:blank'te yok)
- getUserMedia({audio: true}) → başarılı

### AudioContext
- userGesture: True olmadan → "suspended" state
- userGesture: True ile → "running" state, ses üretilebilir

### Ses Pipeline
- AudioContext oscillator (660Hz sine) → PulseAudio null-sink monitor
- ffmpeg capture → MP3 — çalışıyor
- **Ses seviyesi:** mean_volume: -13.9 dB, max_volume: -10.3 dB ✅

### CDP Bağlantısı
- Browser-level WebSocket: `ws://.../devtools/browser/UUID`
- Page-level WebSocket: `ws://.../devtools/page/TAB_ID`
- Sayfa navigasyonu + loadEventFired bekleme çalışıyor

## Sorunlar ve Çözümler
- browser_click "Join from browser" butonunda çalışmadı → MCP puppeteer veya CDP kullan
- app.zoom.us/wc/join/ID → "invalid link (3001)" meeting başlamamışsa
- AudioContext suspended → userGesture: True zorunlu
