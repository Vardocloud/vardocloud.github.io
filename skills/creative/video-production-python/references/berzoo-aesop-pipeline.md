# BerZoo US — Aesop Fable Video Pipeline

**Working pattern for BerZoo US** YouTube channel (Aesop's fables in English, 60-90s shorts, 9:16 vertical).

## Core Stack

| Step | Tool | Details |
|------|------|---------|
| Story | Hardcoded Aesop fable | Public domain, 5 scenes |
| Images | Pollinations AI | `image.pollinations.ai/prompt/{url_encoded}` — Pixar 3D style |
| Voiceover | Kokoro TTS | `am_santa` (American male, warm storyteller), speed=**0.85** (NOT 0.95 — Edel found 0.95 too fast) |
| Music | SoundHelix / Pixabay | Royalty-free, volume=**0.08-0.10** (NOT 0.12 — was too loud, overpowered narration) |
| Assembly | MoviePy 2.x | 9:16 (1080×1920), 24fps, libx264 |

## Proven Prompt Formula for Pixar-style Images

```
Two cute mice sitting at a small rustic wooden table, ... 
cozy countryside cottage with warm sunlight streaming through window, 
3D Pixar animation style, cinematic quality, highly detailed
```

Key elements: `3D Pixar animation style`, `cinematic quality`, `highly detailed`, scene-specific lighting.

## Working MoviePy 2.x API (verified)

```python
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips

clip = ImageClip(img_path).with_duration(dur_per_img)
clip = clip.resized(height=1920)              # NOT .resize()
clip = clip.with_position(("center", "center"))
clip = clip.resized(lambda t: 1 + 0.02*t)     # Slow Ken Burns zoom

# Background music at proven volume
bg = AudioFileClip(str(bg_path)).with_duration(video.duration)
bg = bg.with_volume_scaled(0.10)              # 0.08-0.10 for storytelling; NOT 0.12 (overpowers voiceover)
new_audio = CompositeAudioClip([voiceover, bg])

video.write_videofile(str(path), fps=24, codec='libx264', audio_codec='aac', 
                      preset='medium', threads=2, logger=None)
```

## Session History

- **20 Jul 2026:** First pipeline created. 5 images generated via Pollinations. Background process was orphaned when session reset killed it.
- **21 Jul 2026:** Recovery session. Used `session_search` to find the incomplete task, re-ran voiceover + assembly using existing images.
- **21 Jul 2026 (later):** Created `berzoo_prompts_v2.py` with full 6-scene prompt pipeline for *The Town Mouse & Country Mouse* using film-director approach (image prompt + negative prompt + video prompt + camera specs per scene). Template generalized in `templates/fable-scene-prompt-template.md`.

## Related Files

- `~/bardoyt/berzoo_prompts_v2.py` — Full 6-scene prompt pipeline for Town Mouse & Country Mouse (image + negative + video + camera)
- `templates/fable-scene-prompt-template.md` — Reusable template for fable scene prompts (film director approach)

## Pitfalls

- **Background processes die on session reset.** Always use `notify_on_complete=true` with long-running `terminal(background=true)` processes.
- **Santa voice speed >0.85 is too fast for fables.** Edel confirmed speed=0.95 made the narration sound hurried. Use 0.85 for natural pacing.
- **Pollinations sometimes returns small/garbled images.** Always check `len(resp.content) > 5000`. Multiple re-rolls may be needed.
- **Kokoro first load is slow.** Downloads Kokoro-82M model (~300MB) from HuggingFace on first run. Cached afterward.
- **Music genre must match narrative.** A generic upbeat track clashes with a slow fable narration. Select soft piano, acoustic, or ambient for storytelling.
- **Pollinations Pixar-style images can have overlapping/broken elements.** Prompt engineering is critical — scene-specific lighting and "cinematic quality" helps but doesn't guarantee clean results. Consider generating 2-3 variants per scene.
- **File paths.** Images, audio, and output all under `~/bardoyt/`. Music under `~/bardoyt/music/`.
- **Image-to-video options (Jul 2026):** nanobanana.io Seedance 2.0 (pro account), Google Gemini browser, Vibes.ai (free, watermark). MoviePy fallback: cross-dissolve + slow Ken Burns zoom/pan.
