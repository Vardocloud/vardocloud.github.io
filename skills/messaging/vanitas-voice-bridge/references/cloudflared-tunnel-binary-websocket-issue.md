# Cloudflare Quick Tunnel — Binary WebSocket Corruption (18 Tem 2026)

## Bulgu

Cloudflare quick tunnel (`*.trycloudflare.com`) binary WebSocket frame'lerini corrupt ediyor. Real-time audio pipeline için kullanılamaz.

## Test Sonuçları

### Localhost Test (`ws://127.0.0.1:8765`)
- PCM gönderildi: 186624 bytes (5.8s Türkçe speech via edge-tts)
- Sonuç: **Tam transkripsiyon** — "Merhaba Vanitas, nasılsın bugün? Bana bir şeyler anlatır mısın?"
- VAD: 2 speech_start, 2 speech_end (doğru)
- STT: progressive non-final tokens → final text

### Cloudflare Tunnel Test (`wss://*.trycloudflare.com/ws/soniox`)
- Aynı PCM gönderildi
- Sonuç: **0 transkripsiyon**, 0 VAD event
- Gelen mesajlar: 25 byte binary — hex decode: `{"type": "session_start"}` (text olarak gönderilmiş ama binary frame olarak işaretlenmiş!)
- Ardından 29-112 byte binary chunk'lar (normal TTS chunk'ı 16KB+ olmalı)
- Session ~6 saniye sonra kapandı (keepalive timeout)

## Kök Neden

Cloudflare reverse proxy'si WebSocket frame'lerini yeniden paketliyor:
1. **Text frame'leri binary olarak işaretliyor** — `session_start` JSON text gönderildi ama binary 25 byte olarak geldi
2. **Binary PCM frame'leri küçük parçalara bölüyor** — 3200 byte chunk yerine 29-112 byte fragment'ler
3. STT yeterli contiguous audio alamıyor → hiç token üretmiyor
4. Keepalive timeout — Cloudflare 6s'den uzun boşta bağlantıları kapatıyor

## Çözüm Önerileri

1. **Tailscale Funnel** — birincil yöntem (Cloudflare katmanı yok, direkt HTTPS tunnel)
2. **Named Cloudflare Tunnel** (non-quick) — daha iyi WebSocket davranışı olabilir (test edilmedi)
3. **ngrok** — alternatif tünel servisi, binary WebSocket sorun bilinen bir mesele değil
4. Cloudflare Workers'da binary framing override mümkün ama quick tunnel'de değil

## İlgili

- Soniox resmi frontend karşılaştırması: `references/soniox-official-frontend-comparison-18-tem-2026.md`
- Cloudflare Community benzer vakalar: "Websockets disconnecting after 20s", "Audio Corruption in WebSocket Binary Data"