---
name: video-production-python
description: "Programmatic video production with Python — MoviePy, FFmpeg, image/text/music assembly for social media Reels, ads, and promotional clips."
category: creative
tags: [moviepy, ffmpeg, video, reel, social-media, instagram, python]
version: 1.1.0
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
- `references/font-troubleshooting.md` — Font descender issues and solutions (from absorbed video-reel-automation)
- `references/pixabay-music-download.md` — Pixabay music download via yt-dlp impersonation (from absorbed video-reel-automation)
- `references/font-download-urls.md` — Google Fonts direct download URLs (from absorbed video-reel)
- `references/moviepy-api-notes.md` — MoviePy 2.x API differences and solutions (from absorbed video-reel)
- `references/absorbed-video-reel-automation.md` — Full original SKILL.md of absorbed sibling
- `references/absorbed-video-reel.md` — Full original SKILL.md of absorbed sibling
- `scripts/reel_olustur.py` — Main Reel creation script (from absorbed video-reel-automation)
- `scripts/olustur.sh` — Easy-use wrapper (from absorbed video-reel-automation)

## AI Storytelling Pipeline (YouTube Automation)

Extend this skill when the user wants to generate short story-driven videos (fables, morals, parables) for YouTube Shorts/Reels using a fully pipelined approach with free AI tools.

### When to Use

- User wants a "story → video" pipeline with AI-generated narrative, images, and voiceover
- Creating faceless YouTube channels (fables, storytelling, educational shorts)
- Automating content production with n8n or similar orchestration
- User is interested in passive income via YouTube content automation

### Core Stack (Free Tools)

| Step | Tool | Why | Free? |
|------|------|-----|-------|
| **Story generation** | LiteRouter API (`claude-haiku-4.5-cheap:free`) | 46 free models, Haiku is fast + cheap | ✅ |
| **Image generation** | **Pollinations** (`image.pollinations.ai/prompt/...`), HuggingFace Inference API (SDXL), or Gemini Pro (browser) | Pollinations free endpoint still works (Pixar 3D style); HF rate-limited without token; Gemini Pro requires Pro account | ✅ |
| **Voiceover** | Kokoro TTS (Santa voice) | Much more natural than Edge TTS; "Santa" has warm old-storyteller quality | ✅ |
| **Background music** | Pixabay / YouTube Audio Library | Free royalty-free | ✅ |
| **Video assembly** | MoviePy + FFmpeg | Already installed | ✅ |
| **Orchestration** | n8n (self-hosted) | Free, runs locally | ✅ |

### ⚠️ Tool Preference Notes (Edel-specific)

| Rejected Tool | Why | Preferred Alternative |
|---------------|-----|----------------------|
| **Edge TTS** | "Basit ve kalitesiz" — robotic, unnatural | Kokoro TTS with **Santa** voice (warm, old storyteller) |
| **Pollinations API** | No longer free — changed pricing model | HuggingFace Inference API (free tier) or Gemini Pro (with Pro account) |
| **Viewmax** | Trustpilot 2.9/5, $14-49/mo, mediocre | Same output achievable with free tools |
| **Emergent** | 3/5 Trustpilot, credit system burns fast | Custom Python pipeline (full control, $0) |

### Pipeline Architecture

```
┌─────────────┐    ┌──────────────┐    ┌───────────┐    ┌────────────┐    ┌──────────┐
│  LiteRouter │───→│  Image Gen   │───→│  Kokoro   │───→│  MoviePy   │───→│ YouTube  │
│ Claude Haiku│    │ HF / Gemini  │    │ TTS Santa │    │ + FFmpeg   │    │ Upload   │
│ → Story     │    │ → 4-6 images │    │ → Voice   │    │ → Video    │    │ API      │
└─────────────┘    └──────────────┘    └───────────┘    └────────────┘    └──────────┘
                                                                    ↑
                                                          ┌──────────┴──────────┐
                                                          │     n8n Workflow    │
                                                          │ (trigger → orchestrate│
                                                          │  → notify)          │
                                                          └─────────────────────┘
```

### Story Generation (LiteRouter API)

**Requires API key registration.** LiteRouter requires an API key (free registration at literouter.com). The free tier ("Basic" plan) gives 50 premium req/day + unlimited free-model req. Without an API key, the endpoint returns HTTP 403.

```python
import requests

LITEROUTER_API = "https://literouter.com/api/chat/completions"
HEADERS = {"Authorization": f"Bearer {LITEROUTER_API_KEY}"}  # Register at literouter.com

payload = {
    "model": "claude-haiku-4.5-cheap:free",  # Free tier model
    "messages": [
        {"role": "system", "content": "You are a master storyteller. Write short fables under 200 words with vivid visual language. Break into 4-6 scenes."},
        {"role": "user", "content": "Aesop-style fable about patience"}
    ],
    "temperature": 0.8,
    "max_tokens": 2000
}
resp = requests.post(LITEROUTER_API, json=payload, headers=HEADERS, timeout=60)
```

Alternative free models on LiteRouter: `deepseek-r1:free`, `gpt-4o-mini:free`, `qwen3.5-7b:free`.

**No API key? Fallbacks:**
- Google Gemini API (free tier via Pro account)
- HuggingFace Inference API (free, no key needed for basic text generation)
- Current Hermes provider model directly

### Image Generation

#### Option A: HuggingFace Free Inference API (Best for automation)
```python
import requests
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
response = requests.post(API_URL, json={
    "inputs": f"storybook illustration, digital art, {prompt}, warm colors, cinematic lighting"
})
# Free tier — rate limited but sufficient for a few images per story
```
#### Option B: Gemini Pro (Best quality, Pro account required)

Use Playwright (already installed with Chromium) to automate Gemini's image generation when you have a Google account with Gemini Pro:

```python
# playwright + chromium already available
# Strategy: open gemini.google.com → generate image with Imagen → download
# Each Pro account has image generation limits + 3 video generations
```

**Setup notes:**
- Playwright + Chromium must be installed: `pip install playwright && playwright install chromium`
- Requires login session (cookie-based or fresh login per run)
- Best for batch image generation when no API-only free option works

### Voiceover (Kokoro TTS — Santa Voice)

#### Full Dependency Chain

Kokoro needs these packages in order — missing any will crash at import time:

```bash
pip install kokoro soundfile misaki spacy phonemizer espeakng_loader
```

| Package | Why needed | Notes |
|---------|-----------|-------|
| `kokoro` | Main TTS engine | v0.9.4+ |
| `soundfile` | Audio file writing | WAV output |
| `misaki` | Phoneme/grapheme processing | Kokoro uses misaki.en for English |
| `spacy` | NLP pipeline (used by misaki) | Large download (~50MB on first pip install) |
| `phonemizer` | Text-to-phoneme conversion | Uses espeak-ng backend |
| `espeakng_loader` | Bundled espeak-ng library | ✅ Includes `libespeak-ng.so` + `espeak-ng-data` — **no `sudo apt install espeak-ng` needed** |

**Important:** The `espeakng_loader` package ships with the compiled `.so` and voice data, so it works on systems without root/sudo access (WSL, Docker containers without root). First load downloads the Kokoro-82M model (~300MB from HuggingFace HF Hub repo `hexgrad/Kokoro-82M`). Model is cached in `~/.cache/huggingface/` for subsequent use. First download can take 1-3 minutes.

```python
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code='a')  # American English
generator = pipeline(story_text, voice='Santa', speed=1.0)

all_audio = []
for gs, ps, audio in generator:
    all_audio.append(audio)
combined = np.concatenate(all_audio)
sf.write("output.wav", combined, 24000)
```

**Santa voice:** Warm old-storyteller quality, perfect for fables and moral stories. Speed=0.95 to 1.0 is natural. Voice name is case-sensitive: `'Santa'` (alias) or `'am_santa'` (American male), `'em_santa'` (English male). Available voices from HF repo: `af_*` (American female), `am_*` (American male), `bf_*` (British female), `bm_*` (British male).

### Full Video Assembly Script

See `scripts/generate_story.py` for a complete working pipeline that:
1. Calls LiteRouter → generates story with scene breakdown
2. Generates 4-6 images per scene (HF API or Pollinations fallback)
3. Generates Kokoro voiceover with Santa voice
4. Assembles video with MoviePy (images + voiceover + optional background music)

### n8n Orchestration

```bash
npm install -g n8n  # or: n8n (already installed)
n8n start           # Web UI at localhost:5678
```

Sample workflow nodes:
1. **Manual/Schedule trigger** — run daily/weekly
2. **HTTP Request** → LiteRouter API → story JSON
3. **Function node** → parse story, split into scenes
4. **Loop** over scenes → **HTTP Request** → HuggingFace API → images
5. **Execute Command** → Python script for video assembly (generate_story.py)
6. **HTTP Request** → YouTube Data API v3 → upload video

### YouTube Monetization Timeline (Realistic)

| Period | Milestone | Income |
|--------|-----------|--------|
| Month 1-3 | Build content library, 0-100 subs | $0 |
| Month 3-6 | Monetization (1K subs + 4K hours) | $50-300/mo |
| Month 6-12 | Content + consistency | $200-1,000+/mo |
| 12+ months | Multiple channels scaled | $500-3,000+/mo |

**Reality check:** First 3-6 months are investment. Quality + consistency > tools.

### Storytelling Content Strategy

- **Format:** English, 60-90 second shorts, 9:16 vertical
- **Theme:** Fables, moral stories, philosophical tales (Aesop's fables proven: 500-1K views per short in testing)
- **Voice:** Kokoro Santa (warm, older narrator) creates emotional connection
- **Key tactic:** Storytelling hooks + moral lesson + cliffhanger for engagement
- **Source material:** Aesop's fables (Library of Congress — `read.gov/aesop/001.html` has 147 public domain fables), world folktales, original AI-generated stories with custom moral
- **Pollinations image gen:** `https://image.pollinations.ai/prompt/{url_encoded_prompt}` — returns JPEG. Free, no key needed. Good for Pixar-style 3D CGI illustrations
- **Background music (free):** SoundHelix (`https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3`), Pixabay, YouTube Audio Library
- **MoviePy v2.x confirmed API:** `clip.resized(height=1920)`, `clip.with_position(("center", "center"))`, `clip.with_duration(s)`, `clip.with_effects([lambda x: x * 0.12])`, `concatenate_videoclips(clips, method="compose")`
- **Style:** Images are storybook-style illustrations, not photorealistic — matches the fable genre
- **Refer to:** Storytelling tactics document (if user has one) for hook/open-loop/moral techniques

## References & Scripts

### Added in v1.1.0 — AI Storytelling Pipeline
- `scripts/generate_story.py` — Complete AI story-to-video pipeline (LiteRouter → images → Kokoro → MoviePy assembly)
- This script lives at `~/bardoyt/scripts/generate_story.py` during active development

## Absorbed Skills

| Skill | Key Content |
|---|---|
| `video-reel-automation` | Instagram Reel automation script; specific Pixabay download approach; font troubleshooting. Absorbed into `scripts/` and `references/`. |
| `video-reel` | Transition effects (crossfade, slide, kenburns, zoomblur, wipe); font URL references; MoviePy v2 API notes. Absorbed into `references/`. |
