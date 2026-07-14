---
name: image-generation
description: Generate images using Pollinations API (nanobanana/Gemini-based — primary, same cost as flux)
category: creative
tags: [image, generation, pollinations, nanobanana, kontext, flux]
---

# Image Generation Skill

This skill provides reliable image generation using the Pollinations API.
**Primary model:** `nanobanana` (Gemini-based, same Pollinations cost as flux, good prompt adherence, supports image-to-image).
**Alternative:** `kontext` (FLUX.1 Kontext, for reference-based image-to-image).
**Instagram carousel:** Use nanobanana with square (1:1) aspect ratio for individual slides.

## Configuration

The Pollinations API key is stored in `/home/ubuntu/.hermes/.env` as `POLLINATIONS_API_KEY`.

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

- **nanobanana** is the primary image model (same Pollinations cost as flux, better text+image coherence)
- For sharper detail: `nanobanana-2`. For 4K quality: `nanobanana-pro`
- **Seedance 2.0** is the primary video model — for lyric videos and social clips
- `kontext` (FLUX.1 Kontext) is the alternative for reference-based image-to-image
- Images: JPEG with Exif metadata. Video: MP4.
- Rate limits: Secret keys (sk_) unlimited
- All requests: `private=true` and `nologo=true` for clean results