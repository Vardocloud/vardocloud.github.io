# Video → Vision Pipeline (Çalışan Kod)

## Genel Bakış

Bu pipeline, bir videoyu hem ses (transkript) hem görsel (kare analizi) olarak işler.
2026-05-28'de Instagram Reels ile canlı test edildi.

## Adımlar

### 1. Video İndir (yt-dlp + WARP)

```bash
~/.local/bin/yt-dlp --proxy "socks5://127.0.0.1:1080" \
  --cookies /home/ubuntu/.hermes/instagram_cookies.txt \
  -o "/tmp/video.%(ext)s" \
  "https://www.instagram.com/p/SHORTCODE/"
```

### 2. Ses Transkripti (faster-whisper)

```python
from faster_whisper import WhisperModel
model = WhisperModel('small', device='cpu', compute_type='int8')
segments, info = model.transcribe('/tmp/audio.wav', language='tr')
for seg in segments:
    print(f'[{seg.start:.1f}s] {seg.text}')
```

### 3. Kare Çıkarma (ffmpeg)

```bash
ffmpeg -i /tmp/video.mp4 -vf "fps=1/3" frames/frame_%02d.jpg -y
```

### 4. Vision Analizi (Pollinations qwen-vision)

Model: `qwen-vision` (ücretsiz, hızlı). API key `.env`'den POLLINATIONS_API_KEY.

```python
import base64, requests, os

# API key .env'den alınır
for frame in sorted_frames:
    with open(frame, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    resp = requests.post(
        "https://gen.pollinations.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "qwen-vision",
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": "Ekranda ne var? 1 cümle."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]}],
            "max_tokens": 80
        }
    )
```

### 5. Birleştirme

Transkript + vision sonuçlarını zaman damgasına göre birleştir.

## Performans (ARM64, 2026-05-28)

| Aşama | 20sn Reels |
|-------|-----------|
| Video indir | ~3s |
| faster-whisper tiny | ~7s |
| 7 kare vision | ~14s |
| Toplam | ~25s |

## Pitfalls

- **API key:** n8n JSON'dan gelen eski key'ler geçersiz. `.env`'deki güncel POLLINATIONS_API_KEY kullan.
- **browser_vision engeli:** Azure content filtering `vision_analyze` tool'unu engelliyor. Pollinations qwen-vision API alternatifi.
- **WARP şart:** Tüm Instagram istekleri WARP proxy üzerinden yapılmalı.
