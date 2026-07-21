# BerZoo US — Storytelling Video Pipeline (21 Jul 2026)

## Prompt Architecture (Film Director's Cut)

### Image Prompt Formula
```
[Subject] + [Action] + [Location] + [Composition] + [Style] + [Lighting]
```
Use **narrative descriptions**, not keyword lists. Cinematic lens terminology: `low angle shot`, `shallow DOF f/1.8`, `85mm portrait lens`, `volumetric lighting`. Positive framing only: describe what IS wanted, not what to avoid.

### Negative Prompt Package (shared across all scenes)
```
deformed limbs, fused body parts, extra fingers on paws, distorted faces,
asymmetrical eyes, melting objects, double contours, blurry artifacts,
watermarks, text overlay, flat 2D cartoon, plastic skin, unrealistic proportions,
scary or menacing expression, dark horror atmosphere, realistic fur texture
```

### Video Prompt Formula (Veo 3 / Image-to-Video)
```
[Keyframe Reference] + [Shot Framing & Motion] + [Action] + [Duration] + [Atmosphere]
```
Camera motions: `slow handheld push-in`, `orbital dolly`, `crane reveal`, `handheld cuts`, `tracking pull-back`. Duration: 5-10s per scene.

### Production Config
- Model: `gemini-3.1-flash-image` (Nano Banana 2)
- Aspect: 9:16 (1080×1920)
- Resolution: 1K
- Voice: Kokoro `am_santa`, speed 0.82
- Music: soft orchestral/felt piano, volume 0.08-0.10
- Assembly: MoviePy, 24fps, H.264, AAC

### Scene Breakdown Template
Each scene in a fable:
1. **Narration text** (for Kokoro voiceover)
2. **Image prompt** (Nano Banana 2 — narrative, cinematic, 9:16)
3. **Negative prompt** (deformed elements, artifacts)
4. **Video prompt** (Veo 3 — camera motion, timing, atmosphere)

### Full pipeline script
`~/bardoyt/berzoo_prompts_v2.py` — complete 6-scene pipeline for The Town Mouse & Country Mouse

## Pitfalls
- **Pollinations free endpoint** produces broken/glitched images — NEVER use for production BerZoo content. Use Gemini Nano Banana 2 directly.
- **Speed=0.95 is too fast** for Santa voice. User preference: 0.80-0.85.
- **Background music must match tone** — random SoundHelix tracks don't work. Use Pixar-style orchestral/felt piano instrumentals from Pixabay.
- **Camofox managed_persistence required** — without it, Gemini session dies between restarts and requires full re-login.