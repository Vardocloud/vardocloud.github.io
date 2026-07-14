# Video → Not Pipeline (Colab Uyarlaması) — DEPRECATED

> **⚠️ BU DOKÜMAN GÜNCELLENMEYİ BEKLİYOR**
>
> İçerdiği faster-whisper kullanımı **Edel tarafından kaldırıldı** (CPU yükü).
> Tüm transkripsiyon işlemleri **Pollinations whisper-1 proxy** üzerinden yapılır.
> Yeni workflow için SKILL.md'deki Katman 2 ve `references/google-drive-transcription.md`'ye bak.
>
> Bu doküman arşiv amaçlıdır — yeni işlerde kullanma.

## Genel Bakış

Bu pipeline, Colab'daki `full_ocr_trans_çıkarma.py` scriptinin sunucu uyarlamasıdır.
YouTube ve Instagram Reels videolarını işleyip yapılandırılmış not çıkarır.

## IG Reels Özel Notları

- Reels URL formatı: `https://www.instagram.com/reel/SHORTCODE/`
- **WARP proxy OLMADAN ASLA istek atma** (Edel'in kuralı — bot detection'a yakalanır)

### Cookie Formatı (KRİTİK)

yt-dlp Netscape cookie formatında **ilk satır mutlaka** şu olmalı:
```
# Netscape HTTP Cookie File
```
`# Netscape cookie jar format` başlığı kabul edilmez → `does not look like a Netscape format cookies file` hatası.

### Instagram Reels İndirme (Sadece Ses)

```bash
~/.local/bin/yt-dlp --proxy "socks5://127.0.0.1:1080" \
  --cookies /home/ubuntu/.hermes/instagram_cookies.txt \
  -x --audio-format wav --audio-quality 0 \
  -o "/tmp/ig_reels.%(ext)s" \
  "https://www.instagram.com/p/SHORTCODE/"
```

### Playwright Cookie Yükleme (Netscape → Playwright)

```python
def parse_netscape_cookies(path):
    cookies = []
    with open(path) as f:
        for line in f:
            if line.startswith('#') or not line.strip(): continue
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                cookies.append({
                    'name': parts[5], 'value': parts[6],
                    'domain': parts[0], 'path': parts[2],
                    'secure': parts[3] == 'TRUE', 'httpOnly': False
                })
    return cookies
```
