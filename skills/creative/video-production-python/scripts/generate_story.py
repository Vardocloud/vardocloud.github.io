#!/usr/bin/env python3
"""Story-to-Video Pipeline. Usage: python generate_story.py [topic]"""
import json, sys, time, re, requests
from pathlib import Path
import numpy as np

WORK_DIR = Path.home() / "bardoyt"
HF_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"


def demo_story():
    return {"title": "The Tortoise and the Hare",
            "story": "A hare mocked a tortoise. The tortoise challenged him to a race. The hare napped. The tortoise won. Slow and steady wins the race.",
            "scenes": [
                {"scene": 1, "visual_prompt": "Storybook illustration of a hare laughing at a tortoise"},
                {"scene": 2, "visual_prompt": "Tortoise challenging a hare at a starting line"},
                {"scene": 3, "visual_prompt": "Hare sleeping under an oak tree"},
                {"scene": 4, "visual_prompt": "Tortoise passing a sleeping hare"},
                {"scene": 5, "visual_prompt": "Tortoise winning a race, animals cheering"}
            ]}


def gen_image(prompt, path, n=1):
    try:
        r = requests.post(HF_URL, json={"inputs": f"storybook illustration, {prompt}"}, timeout=30)
        if r.status_code == 200:
            with open(path, "wb") as f: f.write(r.content)
            return path
    except: pass
    return None


def tts(text, path, voice="Santa"):
    from kokoro import KPipeline
    import soundfile as sf
    p = KPipeline(lang_code="a")
    chunks = [a for _, _, a in p(text, voice=voice, speed=1.0)]
    if chunks:
        sf.write(path, np.concatenate(chunks), 24000)
        return path


def assemble(audio_path, images, out):
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    v = AudioFileClip(str(audio_path))
    d = v.duration / max(len(images), 1)
    clips = [ImageClip(str(p), duration=d).resized(height=1920).with_position(("center", "center"))
             for p in images if p.exists()]
    if not clips: return None
    vid = concatenate_videoclips(clips, method="compose").with_audio(v)
    vid.write_videofile(str(out), fps=24, codec="libx264", audio_codec="aac", logger=None)
    vid.close(); return out


def run(topic=None):
    ts, story = int(time.time()), demo_story()
    img_dir = WORK_DIR / "images" / str(ts); img_dir.mkdir(parents=True, exist_ok=True)
    (WORK_DIR / "audio").mkdir(exist_ok=True); (WORK_DIR / "output" / str(ts)).mkdir(parents=True, exist_ok=True)
    
    images = [gen_image(s["visual_prompt"], img_dir / f"s_{i+1}.png", i+1)
              for i, s in enumerate(story["scenes"])]
    images = [p for p in images if p]
    
    audio = tts(story["story"], WORK_DIR / "audio" / f"s_{ts}.wav")
    if not audio: return print("TTS failed")
    
    vid = assemble(audio, images, WORK_DIR / "output" / str(ts) / "final.mp4")
    if vid: print(f"\nDone: {vid}")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
