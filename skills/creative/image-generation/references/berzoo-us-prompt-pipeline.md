# BerZoo US — Aesop Fable Prompt Pipeline (21 Jul 2026)

Complete prompt engineering framework for transforming Aesop fables into YouTube Shorts.

## Platform: Gemini Browser (gemini.google.com)
- Model: Nano Banana 2 (gemini-3.1-flash-image / Flash)
- Account: kenshin4155@gmail.com (Pro)
- Browser: Camofox with managed_persistence

## Image Prompt Formula
```
[Subject] + [Action] + [Location] + [Composition] + [Style] + [Lighting]
```
- Narrative description, NOT keyword lists
- Cinematic lens terms: f/1.8, shallow DOF, volumetric lighting
- Positive framing: "empty street" not "no cars"

## Video Prompt Formula (Veo 3 / Image-to-Video)
```
[Keyframe reference] + [Shot framing & motion] + [Action] + [Duration] + [Atmosphere]
```
- Camera motions: slow push-in, orbital dolly, crane rise, tracking shot
- Generate keyframe with Nano Banana 2 first, then feed to Veo

## Negative Prompt Package (shared across scenes)
```
deformed limbs, fused body parts, extra fingers on paws, distorted faces,
asymmetrical eyes, melting objects, double contours, blurry artifacts,
watermarks, text overlay, flat 2D cartoon, plastic skin, unrealistic proportions,
scary expression, dark horror atmosphere
```

## Scene Structure (5-6 scenes per fable)
1. Opening (character + setting intro)
2. Development (event, encounter)
3. Turning point (conflict)
4. Resolution
5. Closing + Moral card

## Production Config
- Aspect: 9:16 (1080x1920), 1K resolution
- Voice: Kokoro am_santa, speed 0.82
- Music: soft orchestral / felt piano, volume 0.08-0.10
- Assembly: MoviePy, 24fps, H.264 AAC

## Resources
- Google Prompt Engineering Whitepaper (Lee Boonstra, 65pp)
- Nano Banana 2 Lighting Prompts (9 image-to-image templates)
- Storytelling Guidebook (Korzay Koçak)
