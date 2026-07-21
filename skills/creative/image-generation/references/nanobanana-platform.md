# nanobanana.io Standalone Platform

**⚠️ Critical distinction — THREE paths to Nano Banana:**

| Path | What | Primary? |
|------|------|----------|
| **#1 Google Gemini (native)** | gemini.google.com → "Görsel oluştur" | ✅ PRIMARY |
| **#2 Pollinations API (proxied)** | `gen.pollinations.ai` with `model=nanobanana` | Programmatic fallback |
| **#3 nanobanana.io (standalone)** | https://nanobanana.io | Separate platform (this doc) |

**This file covers path #3 (nanobanana.io standalone).** It is a SEPARATE platform from Pollinations. The `nanobanana` model inside Pollinations API is a different thing — Pollinations licensed/rebadged the model.

## What It Is

A Gemini-powered AI image editor and generator platform. Supports:
- Text-to-image generation
- Prompt-based image editing (inpainting, style transfer, object manipulation)
- Image-to-video (Seedance 2.0)
- Consistent character editing across multiple images
- High-resolution output (up to 4K with Pro)

## Available Models (as of July 2026)

| Model | Purpose | Notes |
|-------|---------|-------|
| **Nano Banana 2** | Primary image gen | Best for consistent characters, storytelling illustrations |
| **Seedream 5.0 Pro** | Photorealistic image gen | Higher detail, realistic textures |
| **Seedance 2.0** | Image-to-video | 2-10s clips, multi-image input |

## Access

1. Visit https://nanobana.io
2. Click "Sign In with Google"
3. Use the pro account credentials
4. Free credits on first sign-in; Pro tier unlocks more capabilities

## Why Use It Over Pollinations Free Endpoint

| Aspect | Pollinations Free | nanobanana.io (Pro) |
|--------|-------------------|---------------------|
| Quality | Inconsistent, broken/glitched elements | Consistent, production-ready |
| Character consistency | Poor across generations | Excellent (same character across scenes) |
| Image-to-video | ❌ | ✅ Seedance 2.0 |
| Resolution | Variable | Up to 4K |
| Prompt adherence | Weak | Strong (Gemini-powered) |
| Cost | Free | Pro account required |

## Use Cases for BerZoo / Storytelling

1. **Generate scene images** consistently — same mouse character style across all scenes
2. **Upscale to 4K** for YouTube Shorts vertical resolution
3. **Image-to-video** — animate key moments (the cat scratching, the mouse running)

## Batch Workflow

Since nanobanana is browser-based (no programmatic API known), use browser automation:
1. Sign in via Google OAuth
2. Upload reference image for consistent character
3. Generate each scene with prompt + reference
4. Download and feed into MoviePy assembly pipeline
