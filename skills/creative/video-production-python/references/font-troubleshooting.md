# Font Troubleshooting for MoviePy Reels

## The PlayfairDisplay-Bold Descender Bug (2026-07-13)

### Symptoms
"Siz isteyin, biz yapalım." sloganının 'y' ve 'p' harflerinin alt kuyrukları kesik görünüyordu. Harfler "Siz istevin, biz vanalım" gibi okunuyordu.

### Root Cause
PlayfairDisplay-Bold.ttf (123 KB) indirilen dosya, Google Fonts CDN'den (fonts.gstatic.com) eksik bir subset içeriyordu. Font dosyasında descender glifleri (aşağı sarkan harf kısımları) bulunmuyordu.

### Investigation Process

1. **Farklı fontlarla test** — Aynı metin üç fontta test edildi:
   - PlayfairDisplay-Bold → ❌ Kesik (descender'lar yok)
   - Cormorant Garamond Bold → ✅ Tam (descender'lar görünüyor)  
   - Montserrat Bold → ✅ Tam (tüm harfler görünüyor)

2. **Pixel-level doğrulama** — ffmpeg ile ham pixel değerleri okundu:
   ```bash
   ffmpeg -i video.mp4 -ss 00:00:05 -vframes 1 -f rawvideo -pix_fmt gray \
     -s 1080x1920 -y /tmp/raw.raw
   python3 -c "
   import numpy as np
   data = np.fromfile('/tmp/raw.raw', dtype=np.uint8).reshape(1920, 1080)
   for y in range(1620, 1640):
       print(f'Row {y}: {data[y].mean():.0f}/255')
   "
   ```

3. **Vision ile çapraz kontrol** — vision_analyze her seferinde harflerin durumunu değerlendirdi.

### Lesson
**Font subset'lerine güvenme.** Özellikle Google Fonts gstatic CDN'den indirilen dosyalar bazen eksik glif seti içerebilir. Her zaman vision_analyze ile doğrula.

### Verified Font URLs

| Font | URL | 
|------|-----|
| Cormorant Garamond Bold | `https://fonts.gstatic.com/s/cormorantgaramond/v21/co3umX5slCNuHLi8bLeY9MK7whWMhyjypVO7abI26QOD_hg9GnM.ttf` |
| Montserrat Bold | `https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf` |
| Montserrat SemiBold | `https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-SemiBold.ttf` |

### Font Download Script (Reliable)

```bash
# Get REAL CDN URL via CSS API (works for any Google Font)
curl -s "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@700&display=swap" \
  | grep -oP 'url\(\K[^)]+' \
  | xargs curl -sL -o ~/.fonts/CormorantGaramond-Bold.ttf
```

This CSS API → URL extraction pattern is the most reliable method. Direct GitHub raw URLs for Google Fonts static files often 404.
