# MoviePy 2.x API Notları

## Import (MoviePy 2.x)

```python
# DOĞRU:
from moviepy import ImageClip, TextClip, CompositeVideoClip
from moviepy import AudioFileClip, concatenate_videoclips, VideoClip, vfx, afx

# YANLIŞ (MoviePy 1.x):
from moviepy.editor import *   # ModuleNotFoundError
```

## TextClip

```python
text = TextClip(
    text="Slogan",
    font="/home/ubuntu/.fonts/Font-Bold.ttf",  # Tam yol zorunlu
    font_size=56,
    color="#D4AF37",
    stroke_color="black",
    stroke_width=1,
    text_align="center",
    size=(int(W * 0.85), None),  # int() cast float boyutlar
)
```

### Position API

```python
# "center" = yatay ortalama
# y = metnin ÜST kenarının frame'deki y koordinatı
text.with_position(("center", H * 0.85))  # H = 1920 için y=1632
```

**Uyarı:** `with_position(("center", y))` metnin üstünü y'ye koyar, ortasını değil.

## AudioLoop

```python
# DOĞRU:
audio = audio.with_effects([afx.AudioLoop(n_loops=3)])

# YANLIŞ:
audio = audio.with_effects([afx.AudioLoop(loops=3)])  # TypeError!
```

## Resize & Crop (9:16)

```python
W, H = 1080, 1920

# Görseli yükle
clip = ImageClip(img_path)

# Önce resize, sonra crop
if clip.w / clip.h > W / H:
    # Çok geniş → yüksekliğe göre ölçekle
    clip = clip.resized(height=H)
    clip = clip.cropped(x_center=clip.w / 2, width=W)
else:
    # Çok dar → genişliğe göre ölçekle
    clip = clip.resized(width=W)
    clip = clip.cropped(y_center=clip.h / 2, height=H)
```

## Gradient (NumPy ile)

```python
import numpy as np

gradient_height = int(H * 0.30)  # Alt %30
gradient_start = H * 0.70        # Framedeki başlangıç konumu

def make_gradient(t):
    """Hafif gradient — mekan detayları kaybolmasın"""
    frame = np.zeros((gradient_height, W, 3), dtype=np.uint8)
    for y in range(gradient_height):
        alpha = y / gradient_height
        val = int(alpha * 80)     # 0 → 80 arası gri
        frame[y, :, :] = val
    return frame

gradient = VideoClip(make_gradient, duration=total_duration)
gradient = gradient.with_position((0, gradient_start)).with_opacity(0.45)
```

**Formül:** val = 80, opacity = 0.45 → parlaklık ~105/255. Daha koyu fotoğraflar için val=60, opacity=0.35.

## Crossfade

```python
clip = clip.with_effects([vfx.CrossFadeIn(fade_duration)])
```

## Audio Fade

```python
audio = audio.with_effects([
    afx.AudioFadeIn(2.0),      # Başta yumuşak açılma
    afx.MultiplyVolume(0.7)     # Ses seviyesi %70
])
```

## FFmpeg Frame Çıkarma

```bash
ffmpeg -i video.mp4 -ss 00:00:08 -vframes 1 -q:v 2 /tmp/frame.jpg -y
```

## Pixel Parlaklık Analizi

```bash
ffmpeg -i video.mp4 -ss 00:00:08 -vframes 1 -f rawvideo -pix_fmt gray -s 1080x1920 -y /tmp/bottom.raw
python3 -c "
import numpy as np
data = np.fromfile('/tmp/bottom.raw', dtype=np.uint8).reshape(1920, 1080)
for y in range(1900, 1920):
    print(f'Row {y}: {data[y].mean():.0f}/255')
"
```
