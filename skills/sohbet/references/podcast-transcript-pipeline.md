# Podcast & Transcript Pipeline

> NotebookLM + Pollinations whisper ile YouTube → Study Guide → Podcast → Transkript iş akışı.

## Pipeline Adımları

```
YouTube linki
  ↓ source_add(url)
NotebookLM kaynağı (caption otomatik çekilir)
  ↓ studio_create(report, custom_prompt)
Study Guide (.md)
  ↓ studio_create(audio, focus_prompt)
Podcast (.m4a)
  ↓ Pollinations whisper-1
Transkript (.txt)
  ↓ source_add(file)
NotebookLM'e geri besleme
```

## Kritik Detaylar

### NotebookLM studio_create
- **Report (Study Guide):** `custom_prompt` parametresi çalışır. "İkinci geçiş: eksik tamamlama" gibi talimatlar verilebilir.
- **Audio (Podcast):** `focus_prompt` parametresi çalışır. `audio_format="deep_dive"` daha uzun/kapsamlı podcast üretir.
- **Dil:** `language="tr"` Türkçe çıktı için.

### Podcast İndirme
- `download_artifact(artifact_type="audio")` kullan.
- **Dosya uzantısı `.m4a` veya `.mp4` olmalı** — `.mp3` hatası: "NotebookLM delivers AAC audio in an MP4 container".
- Bazen `download_artifact` ilk seferde başarısız olur — **tekrar dene**, ikincide genelde çalışır.
- Google'ın `lh3.googleusercontent.com` URL'si doğrudan indirilemez (auth ister).

### Transkript (Pollinations whisper)
- **Endpoint:** `POST https://gen.pollinations.ai/v1/audio/transcriptions`
- **Auth:** `Authorization: Bearer $POLLINATIONS_API_KEY` (`.env`'den)
- **Model:** `whisper-1`
- **Format:** `response_format=json` (text değil! text hata veriyor)
- **Dil:** `language=tr`
- **Süre:** 23 dk podcast ~95 saniyede transkript edilir.

### NotebookLM'e Kaynak Ekleme
- `source_add(source_type="file")`: `.md`, `.txt`, `.pdf` çalışır.
- `source_add(source_type="url")`: YouTube linkleri çalışır (caption'ı otomatik çeker).
- **Ses dosyası eklenemez** — NotebookLM ses kaynağı desteklemez.

## Telegram'a Dosya Gönderme (MEDIA)

### İzinli Dizinler
`MEDIA:` etiketi sadece şu dizinlerden dosya gönderebilir:
- `~/.hermes/audio_cache/`
- `~/.hermes/image_cache/`
- `~/.hermes/video_cache/`
- `~/.hermes/cache/*`

Ek dizin eklemek için: `.env`'e `HERMES_MEDIA_ALLOW_DIRS=/path/to/dir` ekle → gateway restart.

### Format Desteği
- ✅ `.mp3` — Telegram'da ses dosyası olarak görünür
- ✅ `.ogg` — Telegram'da sesli mesaj baloncuğu olarak görünür
- ✅ `.txt` — Döküman olarak gönderilir
- ✅ `.jpg`, `.png`, `.webp` — Fotoğraf
- ❌ `.md` — Telegram desteklemez, `.txt`'ye çevir

### Pitfall
`send_message` "success" dönebilir ama dosya ulaşmaz. Gateway loglarında `"Skipping unsafe MEDIA directive path outside allowed roots"` kontrol et. Bu hata → dosya izinli dizinde değil demektir.
