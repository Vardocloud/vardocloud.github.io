# Pixabay Müzik İndirme — yt-dlp Impersonation

Pixabay Cloudflare koruması altında ve Vue.js ile render ediliyor. Download butonları
JavaScript ile çalıştığından headless browser'da tetiklenmesi zordur.

## Çalışan Yöntem

```bash
# Parça sayfasına git, yt-dlp Cloudflare'i geçip CDN linkini bulur
python3 -m yt_dlp \
  --extractor-args "generic:impersonate" \
  -O "fon_muzigi.mp3" \
  "https://pixabay.com/music/<parca-slinki>-<id>/"
```

## Doğrulanmış Örnek (13 Tem 2026)

**Parça:** "Corporate Advertising Version 2" — BombinSound (1:10, corporate)
**URL:** `https://pixabay.com/music/corporate-corporate-advertising-version-2-537813/`

```bash
python3 -m yt_dlp \
  --extractor-args "generic:impersonate" \
  -o "fon_muzigi.mp3" \
  "https://pixabay.com/music/corporate-corporate-advertising-version-2-537813/"
```

Bu parça iç mimarlık reklamı için kullanıldı — enerjik, modern, kurumsal.

## Notlar

- **403 hatası:** `Got HTTP Error 403 caused by Cloudflare anti-bot challenge` alırsan
  `--extractor-args "generic:impersonate"` flag'ini ekle. Bu olmadan Cloudflare geçilmez.
- **İlk istek yavaş olabilir:** Cloudflare challenge çözümü ilk seferde 2-5sn sürebilir.
  Sonraki istekler hızlı olur.
- **Format listesi:** `python3 -m yt_dlp --extractor-args "generic:impersonate" -F <URL>`
  ile mevcut formatları görebilirsin. Pixabay'de genelde tek MP3 formatı vardır.
- **Alternatif:** Pixabay API'si (`pixabay.com/api/`) ücretsiz API key ile kullanılabilir
  ama yt-dlp yöntemi daha az kurulum gerektirir.
