# Reel Pipeline — Full Working Script

This is the complete Reel automation script from the inaugural session (13 Jul 2026 — interior design ad for Edel's friend).

## Script Location

`/home/ubuntu/reel-otomasyonu/reel_olustur.py`

## What It Does

1. Reads all images from a folder
2. Crops each to 9:16 (1080×1920) with center-crop
3. Applies zoom-in effect + crossfade transitions
4. Adds gradient overlay (bottom ~55%)
5. Overlays text: opening title, subtitle, gold slogan, contact
6. Loops background music to match video duration
7. Renders MP4 in Instagram Reel format

## How to Run

```bash
cd /home/ubuntu/reel-otomasyonu
python3 reel_olustur.py \
  --images fotograflar \
  --output reel.mp4 \
  --slogan "Siz isteyin, biz yapalım." \
  --alt-baslik "İç Mimarlık & Dekorasyon Tasarım" \
  --iletisim "DM'den iletişime geçin" \
  --music fon_muzigi.mp3 \
  --sure 80
```

## Dependencies

```bash
pip install moviepy pillow
```

## Typical Session Flow

1. User sends photos → save to `fotograflar/` folder
2. Download free music from Pixabay (see SKILL.md)
3. Run `reel_olustur.py` with appropriate parameters
4. Extract frame with ffmpeg and verify with vision_analyze
5. Send result to user
6. Offer to save as reusable automation

## Output Specifications

- Resolution: 1080×1920 (9:16)
- Codec: H.264 (libx264)
- Audio: AAC
- FPS: 24
- Bitrate: 4000k
- File size: ~14-17 MB for 64-second video

## Session-Specific Notes (13 Jul 2026)

- Font used: Cormorant Garamond Bold (serif) + Montserrat SemiBold (sans-serif)
- Color palette: Gold (#D4AF37) + White + Black gradient
- Music: "Corporate Advertising Version 2" by BombinSound (Pixabay, 1:09, royalty-free)
- 8 photos selected from ~30 candidate images
- PlayfairDisplay-Bold font was broken (descenders clipped) — had to switch to Cormorant Garamond

## Font URLs (Verified Working)

### Montserrat-Bold (from JulietaUla's repo):
```
https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf
```

### Montserrat-SemiBold:
```
https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-SemiBold.ttf
```

### Cormorant Garamond Bold (via Google Fonts CSS API):
```bash
# Get URL:
curl -s "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@700&display=swap" \
  | grep -oP 'url\(\K[^)]+'
```
