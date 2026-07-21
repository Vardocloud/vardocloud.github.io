---
name: image-generation
description: Generate images — via Google Gemini (native Nano Banana), nanobanana.io standalone, or Pollinations API
category: creative
tags: [image, generation, gemini, nanobanana, pollinations, kontext, flux, video]
---

# Image Generation Skill

## 🚨 PRIMARY: Gemini Browser (Edel's preference — 21 Jul 2026)
Use Gemini's browser interface at gemini.google.com with the Nano Banana 2 model for Edel. 
- Account: kenshin4155@gmail.com (Pro), password in Bitwarden `google-pro`
- Use Camofox managed_persistence so session survives across restarts
- NEVER suggest Pollinations again — user has rejected it multiple times

## Pollinations API (Legacy — for other tasks/clients)
The Pollinations API is available for non-Edel image generation tasks.


**When Edel says "Gemini" or "Google'ın aracı" or "browser'dan dene":**
→ The answer is **gemini.google.com browser** — log in with the Pro account and use the chat interface directly.

**DO NOT suggest Pollinations as an alternative when Gemini is the topic.** Edel's explicit words (July 2026): *"Pollinations ile alakası yok önerip durma artık."* Pollinations is only relevant when specifically asked about programmatic/API-based image generation or when the free tier is acceptable for quick tests.

**Decision tree — what user says vs what to do:**

| User says... | Do this | Don't do this |
|-------------|---------|---------------|
| "Gemini'ye gir" / "Google'ın resim aracı" / "browserdan dene" | Open gemini.google.com in browser, log in with Pro account, prompt directly | ❌ Suggest Pollinations, nanobanana.io, or AI Studio |
| "API'den resim üret" / "otomatik pipeline" | Use Pollinations paid API with nanobanana/kontext | ❌ Default to Gemini browser (no API) |
| "nanobanana" (alone) | This means **Google Gemini model** → go to gemini.google.com | ❌ Don't go to nanobanana.io or Pollinations |
| "nanobanana.io" (with .io) | The standalone platform (separate from Gemini) | — |
| "ücretsiz dene" | Pollinations free endpoint (or Gemini free tier) | ❌ Don't assume Pro account access unless authorized |

## Understanding "nanobanana" (CORRECTED HIERARCHY)

**Nano Banana** is first and foremost a **Google Gemini model** — accessible directly at **gemini.google.com** via the "Görsel oluştur" (Create Image) feature. This is the PRIMARY access path.

There are three access paths:

| Path | Access | Best For | Quality |
|------|--------|----------|---------|
| **1. Google Gemini (native)** — gemini.google.com | Browser + Google login | Interactive image gen + image-to-video | ✅ Best / Pro account |
| **2. Pollinations API (proxied)** — `gen.pollinations.ai` with `model=nanobanana` | API key in .env | Automated/programmatic pipelines | ✅ Good |
| **3. nanobanana.io (standalone)** — nanobanana.io | Browser + Google Sign-In | Image editing, upscaling, Seedance video | ✅ Good |

**⚠️ Common misunderstanding corrected:** "nanobanana" is NOT primarily a Pollinations model. Pollinations offers Nano Banana as a proxied model on their paid API. The native source is Google Gemini itself. When the user says "Gemini'ye gir ve resim oluştur seç" — they mean path #1 above.

### Trigger / When to Use Each

| User says... | Path |
|-------------|------|
| "Gemini'yi browser'da dene" / "gemini.google.com'a gir" | **#1 Google Gemini (native)** |
| "API'den resim üret" / "Pollinations'tan dene" | **#2 Pollinations API** |
| "nanobanana.io" / "Seedance video" / "image-to-video yap" | **#3 nanobanana.io standalone** |
| "ücretsiz dene" / "hızlı test" | Pollinations free endpoint (inconsistent quality) |

## 1. Google Gemini (Native) — Browser Access

Nano Banana is a **Google Gemini model**. Access it at **gemini.google.com** with a signed-in Google account.

### What Gemini Offers

| Feature | Model/Tool | Notes |
|---------|-----------|-------|
| **Image generation** | Nano Banana (Imagen) | "Görsel oluştur" feature in Gemini chat |
| **Image variants** | Nano Banana 2 (sharper), Nano Banana Pro (4K) | Selected within Gemini's image tool |
| **Image-to-video** | Built-in (Imagen Video / Veo) | ✅ **Confirmed working (July 2026)** — Flash model accepts "create a short video of..." prompts directly in chat and generates 3-8s clips from reference images |
| **Image editing** | Prompt-based inpainting | Edit existing images with natural language |

### Access Steps

1. Navigate to https://gemini.google.com (use `?hl=tr` for Turkish UI)
2. Sign in with Google account (Pro/Advanced recommended for full features)
3. Enter a prompt in the chat box — **no need to switch to a special image mode**; just prompt directly
4. For image gen: describe the scene (e.g. "a cute mouse in a field, Pixar 3D style")
5. For **image-to-video**: after generating the image, send a follow-up prompt like "create a short video of this mouse walking through the field, 5 seconds" — Gemini accepts and begins generating the video inline
6. Image appears inline with download/share buttons

### Persistent Browser Session (Camofox — REQUIRED for Gemini)

**Without persistence, the Gemini session dies every time the browser page goes blank or the session restarts.** To keep kenshin4155@gmail.com permanently logged in:

```bash
hermes config set browser.camofox.managed_persistence true
hermes config set browser.engine camofox
```

This uses Camofox (Firefox fork) with `managed_persistence` — cookies, logins, and session state survive across restarts. Login ONCE, then Gemini stays open forever.

**⚠️ Headless Chrome vs Camofox:** Google classifies headless Chrome as untrusted and refuses to persist sessions (confirmed in headless-browser-auth skill). Camofox with `managed_persistence` avoids this — it was designed specifically for persistent browser profiles in Hermes.

**When NOT to use Camofox:** Cloud-only workflows that need Browserbase features (residential proxies, CAPTCHA solving). For Gemini image gen, Camofox local is the right choice.

### Login Workflow (Tested Working — 21 Jul 2026)

When you need to log in to gemini.google.com with the Pro account:

1. **Retrieve password from Bitwarden** — account is stored as `google-pro` in bw:
   ```bash
   curl -s 'http://127.0.0.1:8087/list/object/items?search=pro'
   ```
   Returns `{"name": "google-pro", "login": {"username": "kenshin4155@gmail.com", "password": "..."}}`

2. **Browser login flow:**
   - Navigate to https://gemini.google.com/app (English UI is fine; `?hl=tr` for Turkish)
   - Click "Sign in" → enter kenshin4155@gmail.com → "Next"
   - Enter password → "Next"
   - **2FA** will appear — preferred flow is **SMS** (user can read code from phone). If SMS shows "Unavailable on this device" (Camofox quirk), use **"Tap Yes on your phone"** instead — sends a push notification with a 2-digit number to the registered devices (Lenovo Yoga Tab 11 / Redmi Note 12 Pro 5G). User taps matching number to approve.
   - ⚠️ **Google Authenticator is NOT preferred** — the 30-second code window is too tight for the browser-based login flow (typing speed + ref ID changes). SMS gives ~5 minutes.
   - "Don't ask again on this device" checkbox is auto-checked — → session persists via Camofox managed persistence

### Account / Credentials

- **Email:** kenshin4155@gmail.com (Gemini Pro/Advanced, also known as "Kenshın Himura")
- **Bitwarden item:** `google-pro` — password retrievable via bw-serve API at localhost:8087
- **Password:** NOT stored in any skill or memory file. Only accessible via Bitwarden.
- **2FA:** SMS to phone ending in 59 — user provides code when needed
- **Free tier:** Basic image gen only; Pro unlocks full quality + video

### Limitations (Browser Path)

- Requires browser automation with live login session
- No programmatic API — only works through the web UI
- Image-to-video output is short (3-8s clips), takes a few minutes to generate
- Browser session can be unstable (pages sometimes go blank on headless setup) — retry with fresh navigate if this happens

## Configuration (Pollinations API Path)

For programmatic/automated access, use Pollinations API. The API key is stored in `/home/ubuntu/.hermes/.env` as `POLLINATIONS_API_KEY`.

## Usage

### Generate Image (Direct API)

```bash
# Set API key
export POLLINATIONS_API_KEY=$(grep POLLINATIONS_API_KEY /home/ubuntu/.hermes/.env | cut -d= -f2)

# Generate image
python3 -c "
import httpx
import urllib.parse
import os

api_key = os.environ['POLLINATIONS_API_KEY']
prompt = 'your prompt here'
encoded_prompt = urllib.parse.quote(prompt)
url = f'https://gen.pollinations.ai/image/{encoded_prompt}?model=kontext&width=1024&height=1024&nologo=true&private=true&key={api_key}'

response = httpx.get(url, timeout=60.0)
with open('/tmp/generated_image.jpg', 'wb') as f:
    f.write(response.content)
print('Image saved to /tmp/generated_image.jpg')
"
```

### Parameters

- **model**: `nanobanana` (PRIMARY — Gemini-based, same Pollinations cost as flux), `nanobanana-2` (sharper detail), `nanobanana-pro` (4K, thinking mode), `kontext` (FLUX.1 Kontext, image-to-image alternative), `flux` (fast), `seedream/seedream-pro` (photorealistic), `gptimage` (OpenAI)
- **width/height**: 64-4096 pixels (default 1024)
- **nologo**: Remove Pollinations watermark (default: true)
- **private**: Hide from public feed (default: true)
- **enhance**: Let AI improve prompt (default: false)
- **negative_prompt**: What to avoid
- **seed**: For reproducible results
- **guidance_scale**: 1-20, how closely to follow prompt
- **quality**: low/medium/high/hd
- **transparent**: Transparent background
- **image**: Reference image URL for image-to-image (kontext supports single image)

### Image-to-Image (Reference-based)

```bash
python3 -c "
import httpx
import urllib.parse
import os

api_key = os.environ['POLLINATIONS_API_KEY']
prompt = 'transform this into a cyberpunk style'
reference_url = 'https://example.com/reference.jpg'
encoded_prompt = urllib.parse.quote(prompt)
url = f'https://gen.pollinations.ai/image/{encoded_prompt}?model=kontext&width=1024&height=1024&nologo=true&private=true&key={api_key}&image={urllib.parse.quote(reference_url)}'

response = httpx.get(url, timeout=60.0)
with open('/tmp/generated_image.jpg', 'wb') as f:
    f.write(response.content)
"
```

## Integration with Hermes

To use this in Hermes agent workflows:

1. The API key is automatically available via the `.env` file
2. Use the `terminal` tool to run the generation command
3. The generated image can be sent via Telegram using `MEDIA:/path/to/image.jpg`

## Examples

### Basic Generation
```python
# In a Hermes task
result = terminal(command="""
export POLLINATIONS_API_KEY=$(grep POLLINATIONS_API_KEY /home/ubuntu/.hermes/.env | cut -d= -f2)
python3 -c "
import httpx, urllib.parse, os
api_key = os.environ['POLLINATIONS_API_KEY']
prompt = 'a beautiful sunset over mountains, photorealistic'
url = f'https://gen.pollinations.ai/image/{urllib.parse.quote(prompt)}?model=kontext&width=1024&height=1024&nologo=true&private=true&key={api_key}'
r = httpx.get(url, timeout=60)
open('/tmp/sunset.jpg', 'wb').write(r.content)
print('/tmp/sunset.jpg')
"
""")
```

### With Reference Image (Image-to-Image)
```python
# For kontext model - single reference image
prompt = 'make this photo look like a watercolor painting'
reference_url = 'https://example.com/photo.jpg'
# ... same as above with &image= parameter
```

## Google Gemini — Browser-Based Image & Video Generation (PRIMARY)

**nanobanana (Nano Banana)** is NOT primarily a Pollinations model — it is **Google Gemini's native image generation model** available at [gemini.google.com](https://gemini.google.com) and [aistudio.google.com](https://aistudio.google.com). Pollinations proxies the same model, but the source/origin is Google Gemini.

When Edel wants image generation for BerZoo or similar projects:
1. **Login to Gemini** via browser at gemini.google.com
2. **Credentials:** kenshin4155@gmail.com — password in Bitwarden as "google-pro" (retrieve via `bw_secure_get.py` or bw-serve API — see `sensitive-data-pipeline` skill)
3. **Image generation:** Gemini's "Görsel oluştur" / "Create image" module — Nano Banana model
4. **Image-to-video:** **Veo** model (same Google ecosystem) for generating video from images
5. All accessed via browser at gemini.google.com — no API key needed, just Google login

### Workflow for BerZoo Images

1. Open gemini.google.com in browser → Sign in with kenshin4155@gmail.com
2. Select the image generation module (Görsel oluştur)
3. Nano Banana model is the default for images
4. Write prompts in English with Pixar/3D style keywords for BerZoo aesthetic
5. For image-to-video: use Veo model (available in same interface or aistudio.google.com)

**Note on quality:** Gemini's Nano Banana produces significantly more consistent results than the free Pollinations endpoint — fewer broken elements, better composition, proper 3D Pixar styling. Worth using over free Pollinations for production-grade content.

## Video Generation (Seedance / Veo — Pollinations API)

Pollinations also supports **AI video generation** — for lyric videos, social clips, animations. This is the direct API behind LYRC Studio ($12-89/mo) at near-zero cost.

### Available Video Models

| Model | Max Duration | Audio | Image-to-Video |
|-------|-------------|-------|----------------|
| **Seedance 2.0** | 2-10s | ❌ | ✅ multi-image |
| **Seedance Pro** | 2-10s, best quality | ❌ | ✅ multi-image |
| **Veo** | 4/6/8s | ✅ | ✅ single image |

### Usage via MCP Tool

```python
# Lyric-style video generation
mcp_pollinations_generateVideo(
    prompt="a person singing with animated text appearing around them, music video style",
    model="seedance",
    duration=5,
    nologo=True,
    private=True
)
```

### LYRC Studio Bypass (Direct API Alternative)

LYRC wraps Seedance 2.0 + GPT Image 2. You can bypass it:
1. **Video**: Pollinations Seedance 2.0 direkt (ücretsiz/çok ucuz)
2. **Cover art**: Pollinations `gptimage` modeli
3. **Lyric sync**: Python + FFmpeg ile elle text overlay
4. **Cost**: ~$0 vs $12+/mo LYRC

### Trigger

Use this when the user shares a LYRC/Seedance/lyric video link and asks about cost, or when they need budget-friendly video generation.

## Notes

- **Nano Banana** is primarily a Google Gemini model (native at gemini.google.com). Pollinations also offers it as a proxied model; nanobanana.io is a separate standalone platform.
- For sharper detail: `nanobanana-2`. For 4K quality: `nanobanana-pro`
- **Pollinations Seedance 2.0** is the primary video model on that platform — for lyric videos and social clips
- `kontext` (FLUX.1 Kontext) is an alternative for reference-based image-to-image on Pollinations
- Images: JPEG with Exif metadata. Video: MP4.
- Rate limits (Pollinations): Secret keys (sk_) unlimited
- All requests: `private=true` and `nologo=true` for clean results

## Fallback Chain for Image Generation

**⚠️ EDEL RULE (July 2026): When Gemini is mentioned, USE GEMINI BROWSER. Pollinations is NOT the fallback from Gemini.**

When user needs an image, try in this order:

1. **Google Gemini (native browser)** — best quality, requires login session at gemini.google.com. **Use this when user says "Gemini", "Google", or "browser'dan dene".** 
2. **Pollinations paid API** (`nanobanana`/`kontext` models) — good quality, needs API key in .env. **Use only when user explicitly asks for API/automated generation.**
3. **nanobanana.io standalone** — good for image editing + Seedance video, needs browser login
4. **Pollinations free endpoint** — inconsistent quality, use for quick tests only
5. **HuggingFace Free Inference API** — rate-limited, good for automation without key

## 3. nanobanana.io Standalone Platform

**Path #3 — tertiary access.** nanobanana.io is a SEPARATE Gemini-powered platform from both Google Gemini and Pollinations. The `nanobanana` model inside Pollinations API is a different thing (Pollinations licensed the model). This section covers the **standalone platform** at https://nanobanana.io.

### Capabilities

| Feature | Tool | Notes |
|---------|------|-------|
| **Image generation** | Nano Banana 2 / Seedream 5.0 Pro | Pro account gives higher quality + consistency |
| **Image-to-video** | Seedance 2.0 | Supports multi-image input, 2-10s clips |
| **Image editing** | Nano Banana | Prompt-based editing, inpainting, style transfer |

### Access

Uses **Google Sign-In** at https://nanobanana.io. Pro account (kenshin4155@gmail.com) unlocks higher resolution (4K), more credits, and Seedance 2.0 video.

### When to Use (Instead of Paths #1 or #2)

- User needs **Seedance 2.0 image-to-video** with multi-image input (Gemini browser only does single-image video)
- User wants **consistent character editing** across multiple images (Nano Banana 2 excels at this)
- User needs **4K upscaling** for professional output
- Pollinations API is unavailable or quality is insufficient

## Free Pollinations Endpoint (No API Key)

For quick tests or when API key is unavailable, Pollinations also has a free endpoint:

```
https://image.pollinations.ai/prompt/{url_encoded_prompt}
```

Returns a JPEG directly (no JSON wrapper). **No API key needed.**

**⚠️ Limitations (observed):**
- Quality is inconsistent — images can have **broken/glitched elements**, overlapping objects, garbled compositions
- Multiple re-rolls often needed
- Best for Pixar/3D cartoon style with prompts containing: `3D Pixar animation style, cinematic quality, highly detailed`
- Not suitable for production where consistent quality is required
- **Does NOT support** image-to-image (img2img) — only text-to-image
- **Does NOT support** the parameters available on the paid API (model selection, negative prompt, guidance_scale, etc.)

When consistency matters, use the paid API with `nanobanana` or `kontext` models above.

For details about the standalone nanobanana.io platform (image gen + Seedance 2.0 image-to-video), see `references/nanobanana-platform.md`.

## Prompt Engineering Resources (3 PDFs — July 2026)

Edel provided three documents to improve general prompt engineering skills. Apply across ALL tasks (coding, image gen, research, etc.):

| Resource | Source | Key Takeaway |
|----------|--------|-------------|
| **Google Prompt Eng. Whitepaper** | Lee Boonstra, 65sf | LLM config (temp/top-K/top-P), zero/few-shot, CoT/ReAct, system/role/contextual, best practices |
| **Nano Banana 2 Işık Promptları** | 9 lighting prompt examples | Image-to-image template: base reference → instructions → hard rules |
| **Hikaye Anlatıcılığı Kitapçığı** | Korzay Koçak | Story structure, character development, sensory description |

See `references/prompt-engineering-resources.md` for full extracted techniques and templates.
See `references/storytelling-video-pipeline.md` for the film-director prompt architecture used in BerZoo US — image prompt formula, video prompt formula, camera lexicon, scene breakdown template, production config, and pitfalls.