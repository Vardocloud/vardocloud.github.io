# Fable Scene Prompt Template (Film Director Approach)

Template for generating consistent, high-quality image prompts for Aesop's fable video scenes.

## Structure Per Scene

Each scene gets:
1. **Image Prompt** — detailed visual description in film-director language
2. **Negative Prompt** — what to avoid (distortions, style breakers)
3. **Video Prompt** — camera motion for image-to-video (if available)
4. **Camera Specs** — lens, lighting, composition, depth of field

## Template

```python
SCENES = [
    {
        "scene": "Scene Title (duration)",
        "image_prompt": (
            "<subject and action in vivid detail>. "
            "<setting and environment>. "
            "<lighting description>. "
            "<art style directive>. "
            "3D Pixar animation style, cinematic quality, highly detailed, "
            "warm color palette, soft ambient lighting"
        ),
        "negative_prompt": (
            "distorted faces, extra limbs, fused objects, "
            "blurry, low quality, photorealistic, dark, scary, "
            "watermark, text, signature"
        ),
        "video_prompt": (
            "<camera motion description>"
        ),
        "camera": {
            "lens": "35mm",
            "aperture": "f/2.8",
            "lighting": "description",
            "composition": "rule of thirds",
            "depth_of_field": "shallow",
        },
        "duration": 8.5,  # seconds
    },
    # ... repeat for each scene
]
```

## Key Prompt Engineering Rules (from Google's whitepaper + testing)

1. **Be specific about lighting** — "warm sunlight streaming through window at 45 degree angle" beats "nice lighting"
2. **Describe the composition** — "mouse centered in frame, wheat field filling background"
3. **Style consistency phrase** at end of every prompt: `3D Pixar animation style, cinematic quality, highly detailed`
4. **Negative prompt is essential** — prevents fused objects, distorted faces common in free image gen
5. **Camera specs improve video gen** — Veo 3 / Seedance 2.0 honor lens and lighting hints

## Scene Count Formula

- ~45-60 second video → 5-6 scenes
- ~80-120 word fable → 6 scenes
- Duration per scene: 5-9 seconds (matching narration pace at speed=0.85)

## Moral Card (Final Scene)

Always end with a text-only moral card (black background, gold text, no image gen needed):
- Duration: ~5 seconds
- Text centered, elegant serif font
- Moral stated in plain English
