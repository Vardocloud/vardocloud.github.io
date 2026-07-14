# MEDIA Dosya Gönderimi — Debugging Rehberi

**Tarih:** 27 Mayıs 2026  
**Keşif:** Telegram'a dosya gönderirken MEDIA etiketi sessizce başarısız olabiliyor — `send_message` "success" döner ama dosya ulaşmaz.

## Sorun Zinciri

1. `send_message` "success" döner, `message_id` alınır → her şey normal görünür
2. Dosya Telegram'a **ulaşmaz**
3. Gateway log'da: `WARNING gateway.platforms.base: Skipping unsafe MEDIA directive path outside allowed roots`

## Root Cause

MEDIA etiketi sadece belirli güvenli dizinlerden dosya gönderir. Varsayılan izinli dizinler:
- `~/.hermes/audio_cache`
- `~/.hermes/image_cache`
- `~/.hermes/video_cache`
- `~/.hermes/document_cache`
- `HERMES_MEDIA_ALLOW_DIRS` env var ile eklenen dizinler

## Debugging Adımları

### 1. Log kontrolü
Gateway log'da "unsafe MEDIA" veya "Skipping" ara.

### 2. Env var yüklü mü?
Running gateway process'in environ'ında `HERMES_MEDIA_ALLOW_DIRS` var mı kontrol et.

### 3. Dosya tipi doğru mu?
```bash
file podcast.mp3
# MPEG ADTS layer III → doğru
# HTML document → yanlış (curl ile auth URL'si inmiş)
# ISO Media, Apple iTunes ALAC/AAC-LC → m4a doğru
```

## Telegram Format Uyumluluğu

| Format | Sonuç |
|--------|-------|
| MP3 | ✅ Güvenilir, downloadable audio |
| m4a | ⚠️ Telegram destekler ama MEDIA path ile aynı sorun |
| OGG | ❌ Dosya olarak gönderildiğinde bazen ulaşmaz |
| .md | ❌ Ulaşmayabilir, metin için mesaj gövdesi kullan |
| .txt | ❌ Aynı şekilde güvenilir değil |

## Dönüştürme Komutları

```bash
# m4a → mp3 (önerilen)
ffmpeg -i podcast.m4a -c:a libmp3lame -b:a 64k podcast.mp3 -y

# m4a → ogg
ffmpeg -i podcast.m4a -c:a libopus -b:a 32k podcast.ogg -y
```

## Gateway Config — Kalıcı Çözüm

1. `.env` dosyasına `HERMES_MEDIA_ALLOW_DIRS` ekle (hedef dizin yolu ile)
2. **Gateway restart ZORUNLU** — `.env` değişikliği sadece restart sonrası yüklenir
3. Gateway process'in environ'ında env var'ın yüklendiğini doğrula
