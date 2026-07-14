---
name: video-production-python
description: "Programmatic video production with Python — MoviePy, FFmpeg, image/text/music assembly for social media Reels, ads, and promotional clips."
category: creative
tags: [moviepy, ffmpeg, video, reel, social-media, instagram, python]
version: 1.0.0
---

# Video Production with Python (MoviePy + FFmpeg)

Create Instagram Reels, TikTok videos, ads, and promotional clips programmatically using Python, MoviePy, and FFmpeg — all free/open-source.

## When to Use

Use this when the user needs:
- A video from a set of images (slideshow, reel, ad)
- An Instagram Reel / TikTok / 9:16 short video
- Automated video assembly from photos + music + text
- A promotional video with branding (slogan, logo, contact info)
- A pipeline that can be re-run with new photos

## Core Stack

| Component | Role | Cost |
|-----------|------|------|
| **MoviePy 2.x** | Video assembly (clips, transitions, text, compositing) | Free |
| **FFmpeg** | Codec/compression backend (used by MoviePy) | Free |
| **Pillow (PIL)** | Text rendering (MoviePy TextClip uses PIL) | Free |
| **Pixabay** | Royalty-free background music (free API) | Free |
| **vision_analyze** | Visual QA — verify your output before delivering | Tool |

## Quickstart

```bash
pip install moviepy pillow
```

Basic structure:
```python
from moviepy import ImageClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips, vfx

# 1. Load images, resize to 9:16 (1080×1920)
W, H = 1080, 1920
images = []
for img_path in sorted_photos:
    clip = ImageClip(img_path).resized(height=H)
    # Crop to 9:16 ratio
    if clip.w / clip.h > W / H:
        clip = clip.cropped(x_center=clip.w / 2, width=W)
    else:
        clip = clip.cropped(y_center=clip.h / 2, height=H)
    clip = clip.with_duration(8)  # 8 seconds per image
    images.append(clip)

# 2. Concatenate with transitions
video = concatenate_videoclips(images, method="compose")

# 3. Add text
text = TextClip("Your message", font="/path/to/font.ttf", font_size=48,
                color="#D4AF37", stroke_color="black", stroke_width=1)
text = text.with_position(("center", y_position)).with_duration(duration)

# 4. Composite everything
final = CompositeVideoClip([video, text], size=(W, H))

# 5. Write output
final.write_videofile("output.mp4", codec="libx264", audio_codec="aac", fps=24)
```

## CRITICAL: Font Handling

MoviePy TextClip uses **PIL/Pillow** for text rendering. This has critical gotchas:

### Font Sources (Reliable)

| Source | How | Reliability |
|--------|-----|-------------|
| **Google Fonts CSS API** | `curl -s "https://fonts.googleapis.com/css2?family=FontName:wght@700&display=swap"` → grep for `.ttf` URL | ✅ BEST |
| **JulietaUla/Montserrat GitHub** | `https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf` | ✅ Montserrat only |
| **Google Fonts GitHub raw** | `https://github.com/google/fonts/raw/main/ofl/fontname/...` | ⚠️ Variable fonts only, static paths may 404 |
| `apt-get install fonts-*` | System fonts (DejaVu, Liberation) | ✅ but limited |

### ⚠️ Font Weight / Descender Pitfalls

1. **Variable fonts default to Thin/Regular weight.** Montserrat-VF.ttf (744KB) defaults to `wght=250` (Thin) — text looks silky, unreadable on dark backgrounds. **Always download a static Bold TTF.**

2. **DO NOT** use Google Fonts CDN raw GitHub URLs for static fonts. The URL pattern changes. Use the **CSS API** to get the real CDN URL:
   ```bash
   # Get REAL download URL for Playfair Display Bold:
   curl -s "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap" \
     | grep -oP 'url\(\K[^)]+'
   # → https://fonts.gstatic.com/s/playfairdisplay/v40/...ttf
   ```

3. **Font descenders can be broken in some CDN subsets.** PlayfairDisplay-Bold from Google Fonts gstatic CDN (123KB) had missing descenders — the bottom of 'y', 'p', 'g' letters were clipped. **Always verify with vision_analyze.**

### Verified Working Fonts

| Font | Source | Weight | Works? | Notes |
|------|--------|--------|--------|-------|
| **Montserrat-Bold** | [JulietaUla GitHub repo](https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf) | Bold | ✅ Excellent | Best all-purpose sans-serif |
| **Montserrat-SemiBold** | Same repo | SemiBold | ✅ Good | Subtitle weight |
| **Cormorant Garamond Bold** | Google Fonts CSS API | Bold | ✅ Elegant | Full descenders, great for luxury/classy looks |
| **PlayfairDisplay-Bold** | Google Fonts gstatic CDN | Bold | ❌ **BROKEN** | Descenders (y, p, g tails) clipped — subset corruption |
| **Roboto** (variable) | Google Fonts raw | Regular | ✅ OK | Safe fallback, basic look |

### Font Verification

```python
from PIL import ImageFont
f = ImageFont.truetype(font_path, 48)
bbox = f.getbbox("Your test text here")
print(f"Height: {bbox[3]-bbox[1]}, Ascent offset: {bbox[1]}")
# If bbox appears abnormally small, the font file may be a broken subset
```

### Turkish Character Support

Test with: `İ ı Ş ş Ç ç Ü ü Ğ ğ Ö ö`
- **Montserrat** (all weights) — ✅ Full support
- **Cormorant Garamond** — ✅ Full support (though the dotless 'ı' may render subtly, it's legible)

## Text Positioning

MOVIEPY `with_position(("center", y))` interprets `y` as the **top** of the text (not center).

### Safe Position Calculation for 1920px height

```python
# For a 9:16 (1080×1920) frame:
gradient_start = int(H * 0.45)  # Gradient overlay begins here
alt_baslik_y = int(H * 0.52)     # "İç Mimarlık..." (small, sans-serif)
slogan_y = int(H * 0.62)         # Main message (big, serif, gold)
iletisim_y = int(H * 0.75)       # Contact info (bottom)
```

**Rule of thumb:** Most serif fonts need the baseline to be at or above `H * 0.65` to avoid bottom clipping. Test with vision_analyze.

### Gradient Background for Text Legibility

**V8 (working) version** — hafif, mekan görünsün:
```python
gradient_height = int(H * 0.30)   # Alt %30
gradient_start = H * 0.70          # %70'ten başla

def make_gradient(t):
    frame = np.zeros((gradient_height, W, 3), dtype=np.uint8)
    for y in range(gradient_height):
        val = int((y / gradient_height) * 80)  # 0→80
        frame[y, :, :] = val
    return frame

gradient = VideoClip(make_gradient, duration=total_duration)
gradient = gradient.with_position((0, gradient_start)).with_opacity(0.45)
```

**Gradient tuning guide:**
- `gradient_start < H*0.50` → too much of the screen is dark; mekan kaybolur
- `val max > 90` → gradient çok aydınlık, metin okunmaz
- `opacity > 0.70` → fotoğraf kaybolur
- Sweet spot for bright interior photos: start=H*0.70, max_val=80, opacity=0.45

**TEST with pixel values:**
```python
# Check actual pixel brightness at text position
ffmpeg -i video.mp4 -ss 00:00:05 -vframes 1 -f rawvideo -pix_fmt gray \
  -s 1080x1920 -y /tmp/raw.raw
python3 -c "
import numpy as np
d = np.fromfile('/tmp/raw.raw', dtype=np.uint8).reshape(1920, 1080)
print(f'Text area brightness: {int(d[1630].mean())}/255')
print(f'Bottom brightness: {int(d[1910].mean())}/255')
"
# Target: text area 80-120/255, bottom 120-150/255, mid-frame >140/255
```

## Music (Free Sources)

### Pixabay (Royalty-Free, No Attribution)

Best source for free background music. Use yt-dlp with impersonation to bypass Cloudflare:

```bash
pip install yt-dlp
python3 -m yt_dlp --extractor-args "generic:impersonate" \
  -o "output.mp3" "https://pixabay.com/music/corporate-.../"
```

Good Pixabay genres for ads: Corporate, Corporate Advertising, Upbeat, Modern.

### Audio Loop Pattern

When music is shorter than video:
```python
from moviepy import afx
if audio_clip.duration < video_duration:
    loops = int(video_duration / audio_clip.duration) + 1
    audio_clip = audio_clip.with_effects([afx.AudioLoop(loops=loops)])
    audio_clip = audio_clip.with_duration(video_duration)
audio_clip = audio_clip.with_effects([afx.AudioFadeIn(2.0), afx.MultiplyVolume(0.7)])
```

## Visual QA Protocol (MANDATORY)

**Always verify visual output with vision_analyze before sending to the user.**

```bash
# Extract a frame at a key moment
ffmpeg -i output.mp4 -ss 00:00:05 -vframes 1 -q:v 2 /tmp/qa_frame.jpg -y
```

Then call `vision_analyze` with specific questions:
- Are any text parts cut off (especially descenders: y, p, g, j)?
- Is text readable against the background?
- Are fonts rendering correctly?
- Do colors and styling match the intended aesthetic?

Do NOT trust the rendering pipeline — what MoviePy thinks it produced and what actually renders can differ (broken font subsets, descender clipping, positioning miscalculations).

### Multi-Iteration Approach

Expect 3-8 iterations for a new Reel type. Each iteration should target exactly ONE problem:
1. **Structure pass** — images, duration, music working
2. **Font pass** — fix font rendering, descenders, verify with vision_analyze
3. **Gradient pass** — tune opacity, height, position using pixel-level brightness checks
4. **Polish pass** — colors, spacing, decorative elements

**Quick signal-reference table:**
| User complaint | Likely fix |
|----------------|------------|
| "yazının altı kesik / text cut off" | Font descender issue → switch font (Playfair Display broken) |
| "yarısı siyah / half the screen black" | Gradient starts too high → set start to H*0.70, opacity 0.45 |
| "mekan görünmüyor / room invisible" | Gradient too dark → increase max_val to 80, lower opacity to 0.45 |
| "yazılar silik / text faint" | Using Regular/Thin → switch to Bold/SemiBold weight |

## Full Pipeline Script Structure

See `references/reel-pipeline.md` for a complete working example (the Reel automation script from the inaugural session).

### Key Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `--images` | dir path | `.` | Folder with jpg/jpeg/png/webp |
| `--output` | file path | `reel_cikti.mp4` | Output video |
| `--slogan` | string | `"Siz isteyin, biz yapalım."` | Main message |
| `--alt-baslik` | string | `"İç Mimarlık..."` | Subtitle |
| `--iletisim` | string | `""` | Contact info (last 5s) |
| `--music` | file path | None | Background music |
| `--sure` | int | 90 | Target duration (seconds) |

## References

- `references/reel-pipeline.md` — Complete working script from the inaugural interior-design Reel session
