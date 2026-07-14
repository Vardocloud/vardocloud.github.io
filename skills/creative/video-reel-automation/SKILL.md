---
name: video-reel-automation
description: "Automated Instagram Reel / social media video creation from images using free tools (MoviePy + FFmpeg + Pixabay). 9:16 format, text overlay, transitions, free music."
version: 1.1.0
tags: [video, reel, instagram, social-media, moviepy, automation, creative]
category: creative
---

# Video Reel Automation

Turn a folder of images into a formatted Instagram Reel (9:16, 1080×1920) with text overlays, crossfade transitions, zoom effects, and Telifsiz Pixabay music.

## When to Use

- User says "make a reel / video ad from these photos"
- "Instagram reklam videosu hazırla"
- "Fotoğraflardan video montaj yap"
- Any request to create social-media video content from image sets

## Prerequisites

- `pip install moviepy pillow`
- `ffmpeg` in PATH
- `python3 -m yt_dlp` installed (`pip install yt-dlp`)
- ~500MB free disk for rendering
- **Font:** MoviePy v2.x uses Pillow for text rendering — needs a TTF font file.
  Install Roboto (or another Latin/Cyrillic font):
  ```bash
  mkdir -p ~/.fonts
  curl -sL "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto%5Bwdth,wght%5D.ttf" -o ~/.fonts/Roboto.ttf
  ```
  `font="Arial"` won't work on most headless Linux systems — always use an absolute path to a real TTF file.

## Workflow

### 1. Pixabay'dan Ücretsiz Müzik İndir

Pixabay Cloudflare koruması altında. Doğrudan curl ile indirilemez. **yt-dlp impersonation** ile çalışır:

```bash
# 1. Uygun müziği Pixabay'de bul (corporate, energetic, ambient, etc.)
# 2. Parça sayfasına gir
# 3. İndir:
python3 -m yt_dlp \
  --extractor-args "generic:impersonate" \
  -o "fon_muzigi.mp3" \
  "https://pixabay.com/music/<parca-slinki>-<id>/"
```

**Neden bu yöntem?** Pixabay download butonları JavaScript/Vue ile çalışır, headless browser'da tetiklense bile CDN download URL'ini almak zordur. yt-dlp generic extractor + impersonation Cloudflare'ı geçer ve doğrudan CDN bağlantısını bulur.

**Dikkat:** Sayfa başına ilk istekte Cloudflare challenge geçilir, sonraki istekler hızlı olur. Eğer hata alınırsa (`Got HTTP Error 403`), `--extractor-args "generic:impersonate"` flag'ini ekleyin.

### 2. Script'i Hazırla

Ana script: `reel_olustur.py` (`scripts/reel_olustur.py`)

Kullanım:
```bash
python3 reel_olustur.py \
  --images /path/to/images/ \
  --output reel_cikti.mp4 \
  --slogan "Siz isteyin, biz yapalım." \
  --alt-baslik "İç Mimarlık & Dekorasyon" \
  --iletisim "DM: @..." \
  --music fon_muzigi.mp3 \
  --sure 90
```

### 3. Parametreler

| Parametre | Açıklama | Varsayılan |
|-----------|----------|-----------|
| `--images` | Görsel klasörü | `.` (current dir) |
| `--output` | Çıktı MP4 yolu | `reel_cikti.mp4` |
| `--slogan` | Ana slogan metni | "Siz isteyin, biz yapalım." |
| `--alt-baslik` | Alt başlık | "İç Mimarlık & Dekorasyon Tasarım" |
| `--iletisim` | İletişim bilgisi (son 5sn) | "" (boş) |
| `--music` | Müzik dosyası | None |
| `--sure` | Toplam süre (saniye) | 90 |

### 4. Çıktı Formatı

- **Boyut:** 1080×1920 (9:16 vertical)
- **Codec:** H.264 + AAC
- **FPS:** 24
- **Bitrate:** 4 Mbps
- **Özellikler:** Crossfade geçiş, zoom-in efekti, metin overlay, gradient alt zemin

## Script Detayları

Script şunları yapar:
1. Klasördeki tüm görselleri bulur (.jpg, .jpeg, .png, .webp)
2. Her görseli 9:16'ya crop eder (en-boy oranına göre akıllı kırpma)
3. Her görsele %6 zoom-in efekti uygular
4. Klipler arasına crossfade ekler
5. Metin overlay'leri ekler:
   - Açılış başlığı (3sn, üst kısım)
   - Slogan (altta kalıcı)
   - Alt başlık (slogan üstü)
   - İletişim (son 5sn)
   - Siyah gradient alt zemin (metin okunabilirliği için)
6. Müzik ekler (loop yapabilir, fade in/out)

## Pitfalls

### Font "Arial" Hatası
Çoğu headless Linux sisteminde Arial kurulu değildir. MoviePy v2.x Pillow üzerinden font yükler — `font="Arial"` yazarsanız `OSError: cannot open resource` alırsınız. Çözüm: Gerçek bir TTF fontu indirin ve tam yol ile kullanın.

### ⚠️ Font Descender Kesilmesi (CRITICAL)
Google Fonts CDN'den (fonts.gstatic.com) indirilen bazı font dosyaları eksik subset içerebilir. **PlayfairDisplay-Bold** (123KB, gstatic CDN) descender'ları kırpmıştır — 'y', 'p', 'g' harflerinin alt kuyrukları font dosyasında mevcut değildir.

**Test edilmiş fontlar:**

| Font | Kaynak | Weight | Descender | Tavsiye |
|------|--------|--------|-----------|---------|
| **Cormorant Garamond Bold** | Google Fonts CSS API | Bold | ✅ Tam | Slogan/başlık (serif) |
| **Montserrat-Bold** | JulietaUla GitHub | Bold | ✅ Tam | Alt başlık (sans-serif) |
| **Montserrat-SemiBold** | JulietaUla GitHub | 600 | ✅ Tam | Alt başlık (orta kalın) |
| **PlayfairDisplay-Bold** | Google Fonts gstatic | Bold | ❌ Kesik | KULLANMA |
| **Roboto** (variable) | Google Fonts raw | Regular | ✅ Tam | Güvenli yedek |

**Font indirme yöntemleri:**

```bash
# ✅ GÜVENİLİR: Google Fonts CSS API'den gerçek CDN URL'sini al
curl -s "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@700&display=swap" \
  | grep -oP 'url\(\K[^)]+' \
  | xargs curl -sL -o ~/.fonts/CormorantGaramond-Bold.ttf

# ✅ GÜVENİLİR: Montserrat'ın resmi GitHub repo'su
curl -sL "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf" \
  -o ~/.fonts/Montserrat-Bold.ttf

# ❌ GÜVENSİZ: Google Fonts raw GitHub URL'leri — static font'larda 404/bozuk
```

**Font doğrulama:** Font kullandıktan sonra MUTLAKA `vision_analyze` ile bir frame alıp kontrol edin. Özellikle 'y', 'p', 'g', 'j' harflerinin alt kuyruklarını inceleyin.

```bash
ffmpeg -i output.mp4 -ss 00:00:05 -vframes 1 -q:v 2 /tmp/qa.jpg
# → vision_analyze ile kontrol et
```

### `size` ve Pozisyon Hataları
- **`size=(W * 0.85, None)`** → `TypeError: 'float' object cannot be interpreted as an integer`. MoviePy içindeki Pillow `Image.new()` integer bekler. Çözüm: `size=(int(W * 0.85), None)`.
- **`with_position(("center", y))`** → `y` metnin **üst kenarını** belirtir, ortasını değil. Serif fontlarda descender'lar bu değerin altına taşar. Her zaman bol pay bırakın.

### Gradient Tuning (Deneme-Yanılma)

Gradient ayarları fotoların parlaklığına göre değişir. Varsayılan değerleri kullanın, sonra vision ile doğrulayın.

**Sinyaller:**
- User: "videonun yarısı siyah" → gradient başlangıcı çok yukarıda (`H*0.45` yerine `H*0.70` dene)
- User: "mekan görünmüyor" → opacity çok yüksek (0.80 → 0.45 düşür), val max'ı artır (45 → 80)
- User: "yazılar okunmuyor" → opacity artır, val min'i düşür

### Diğer
- **MoviePy AudioLoop:** `from moviepy import afx` → `afx.AudioLoop(loops=N)`
- **Pixabay müzik:** yt-dlp impersonation ile (`--extractor-args "generic:impersonate"`)
- **Görsel kalitesi:** En az 1080×1080 input önerilir
- **Pillow uyumluluğu:** pip resolver uyarıları güvenle göz ardı edilebilir
- **FFmpeg:** `ffmpeg -version` ile kontrol edin

## Visual QA Protocol (MANDATORY)

Always verify visual output with `vision_analyze` before delivering to the user. **What MoviePy thinks it produced and what actually renders can differ** — broken font subsets, descender clipping, positioning miscalculations.

```bash
# Extract a frame at a key moment
ffmpeg -i output.mp4 -ss 00:00:05 -vframes 1 -q:v 2 /tmp/qa_frame.jpg -y
```

Then call `vision_analyze` with specific questions about:
- Descender visibility ('y', 'p', 'g', 'j' letters)
- Font rendering quality
- Gradient coverage (% of screen)
- Text contrast against background

### Multi-Iteration Approach

Expect 3-8 iterations for a new Reel type. Each iteration should target exactly ONE problem:
1. First pass: get structure working (images, duration, music)
2. Font pass: fix font rendering, descenders
3. Gradient pass: tune opacity, height, position
4. Polish pass: colors, spacing, decorative elements

**Sinyaller ve çözümleri:**
| User şikayeti | Muhtemel çözüm |
|----------------|-----------------|
| "yazının altı kesik" | Font descender sorunu → font değiştir |
| "videonun yarısı siyah" | Gradient çok büyük → `gradient_start`'ı `H*0.70` yap, `opacity`'yi 0.45'e düşür |
| "mekan görünmüyor" | Gradient çok koyu → `val` max'ı 80 yap, opacity 0.45 |
| "yazılar silik" | Font Regular/Thin kullanılıyor → Bold/SemiBold kullan |

## References

- `scripts/reel_olustur.py` — Ana Reel oluşturma script'i
- `scripts/olustur.sh` — Kolay kullanım wrapper'ı
- `references/pixabay-music-download.md` — Pixabay müzik indirme detayları
- `references/font-troubleshooting.md` — Font descender sorunu ve çözümü (Playfair Display → Cormorant Garamond)
