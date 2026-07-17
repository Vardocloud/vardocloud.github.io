---
name: video-reel
description: "Instagram/TikTok Reel oluşturma — fotoğraflardan 9:16 video, geçiş efektleri, metin overlay, müzik. MoviePy + FFmpeg ile ücretsiz otomasyon."
version: 1.0.0
metadata:
  hermes:
    tags: [video, reel, moviepy, social-media, automation, instagram, tiktok]
    category: media
    triggers: [reel, instagram video, tiktok video, slideshow, fotoğraf video, reklam videosu]
---

# Video Reel Otomasyonu

Fotoğraflardan Instagram/TikTok Reel'i (9:16) otomatik oluşturma.

## Kullanım

```bash
cd /path/to/project
python3 reel_olustur_v2.py \
  --images fotograflar/ \
  --output reel.mp4 \
  --slogan "Siz isteyin, biz yapalım." \
  --alt-baslik "İç Mimarlık & Dekorasyon Tasarım" \
  --iletisim "DM'den iletişime geçin" \
  --music fon_muzigi.mp3 \
  --sure 80 \
  --efekt crossfade
```

## Geçiş Efektleri (`--efekt`)

| Değer | Açıklama |
|-------|----------|
| `crossfade` | Klasik yumuşak geçiş (varsayılan) |
| `slide` | Yandan kaydırmalı geçiş |
| `kenburns` | Yavaş zoom + pan efekti |
| `zoomblur` | Zoom + bulanıklaştırma |
| `wipe` | Silme/yana açılma efekti |

## Setup

```bash
pip install moviepy pillow
# FFmpeg sistemde kurulu olmalı
ffmpeg -version
```

## Font Kurulumu

Google Fonts CSS API'den doğru URL ile indir:

```bash
# CSS API'den Bold font URL'sini bul
curl -s "https://fonts.googleapis.com/css2?family=Font+Name:wght@700" | grep -oP 'url\(\K[^)]+' | head -1
# İndir
curl -sL "<URL>" -o ~/.fonts/FontName-Bold.ttf
```

**Çalışan fontlar:**
- `CormorantGaramond-Bold` — şık serif ✅
- `Montserrat-SemiBold` / `Montserrat-Bold` — modern sans ✅
- `PlayfairDisplay-Bold` — Google CDN'den indirilen ✱BOZUK✱ (descender'lar kesik)

## Teknik Notlar

### MoviePy 2.x API
- Import: `from moviepy import ImageClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips, VideoClip, vfx, afx`
- AudioLoop: `afx.AudioLoop(n_loops=N)` (NOT `loops=`)
- TextClip position: `("center", y)` — y metnin ÜST kenarının konumu
- Variable font'lar MoviePy TextClip'te weight axis'i desteklemez — statik TTF kullan

### Gradient Tasarımı
- Alt %30-35'lik alanı kaplasın (mekan görünsün)
- `val = int((y / gradient_height) * 80)` — 80/255 gri, çok koyu değil
- `opacity=0.45` — mekan detayları kaybolmasın
- Başlangıç: H*0.70 (alt kısım)
- `np.zeros((gradient_height, W, 3))` — R=G=B eşit olunca gri tonlama
- Eğer fotoğraflar zaten koyuysa, gradient daha hafif olmalı

### Slogan Pozisyonu
- Descender'ları (y, p, g, j) olan fontlarda metnin altında en az 200px boşluk bırak
- `H * 0.85` güvenli bir başlangıç noktası (1920px frame'de yaklaşık 1632px)

## Pitfall'lar

1. **Font kesintisi**: PlayfairDisplay Bold fontu Google Fonts CDN'den bozuk geliyor — alt uzantılar (descender'lar) eksik. Cormorant Garamond Bold ile değiştir.
2. **Gradient çok koyu**: Fotoğraf + gradient birleşince ekran %90 siyah olabiliyor. Opaklık 0.45'i, val max 80'i geçmesin.
3. **Variable fontlar**: PIL'de `set_variation_by_axes([700])` ile Bold yapılabiliyor ama MoviePy TextClip font path alıyor, PIL objesi almıyor. Statik TTF kullan.
4. **AudioLoop API**: MoviePy 2.x'te `loops=` değil `n_loops=` parametresi.
5. **Metadata boyutu**: Özellikle büyük fotoğraflarda resize önce crop'tan önce yapılmalı.

## References

- `references/font-download-urls.md` — Google Fonts doğrudan indirme URL'leri
- `references/moviepy-api-notes.md` — MoviePy 2.x API farklılıkları ve çözümleri
