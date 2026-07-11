#!/usr/bin/env python3
"""Transcribe podcast v2 to text using faster-whisper"""
from faster_whisper import WhisperModel
import time

start = time.time()
print("Model yukleniyor (small)...")
model = WhisperModel("small", device="cpu", compute_type="int8")

print("Transkript basliyor...")
segments, info = model.transcribe(
    "/home/ubuntu/.hermes/notebooklm/tibet_podcast_v2.mp3",
    language="tr",
    beam_size=5,
    vad_filter=True
)

print(f"Dil: {info.language} (%{info.language_probability:.0f})")

lines = []
for seg in segments:
    lines.append(f"[{seg.start:.1f}s-{seg.end:.1f}s] {seg.text.strip()}")

output = "\n".join(lines)
path = "/home/ubuntu/.hermes/notebooklm/tibet_podcast_v2_transcript.txt"
with open(path, "w") as f:
    f.write(output)

elapsed = time.time() - start
print(f"Bitti! {len(lines)} segment, {len(output)} karakter, {elapsed:.0f}s")
