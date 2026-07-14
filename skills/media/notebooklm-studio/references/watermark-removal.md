# NotebookLM Slide Deck — Watermark Removal

## Overview

NotebookLM Studio slide deck'lerinin PDF çıktılarında sağ alt köşede küçük bir "NotebookLM" watermark'ı bulunur.

## Kural (Edel, 10 Tem 2026)

**ASLA crop kullanma.** Görselin alt kısmını kırpmak kompozisyonu bozar. Clone stamp yöntemi kullan.

## Yöntem: Clone Stamp

Watermark bölgesini, hemen üstündeki temiz piksellerle değiştir. İki bölge de aynı renk gradyanına sahip olduğu için geçiş fark edilmez.

### Koordinatlar (200 DPI, 3823x2134px çıktı)

```
X: 3531 - 3791  (260px genişlik)
Y: 2079 - 2105  (26px yükseklik)
```

### Python

```python
import cv2, os
input_dir = "/path/to/pngs"
for fname in sorted(os.listdir(input_dir)):
    if not fname.endswith(".png"): continue
    img = cv2.imread(os.path.join(input_dir, fname))
    src = img[2040:2075, 3500:3823].copy()  # watermark'ın hemen üstü
    img[2075:2110, 3500:3823] = src         # watermark bölgesi
    cv2.imwrite(os.path.join(input_dir, fname), img)
```

### Doğrulama

```python
roi = cv2.imread("test.png")[2075:2110, 3500:3823]
dark = np.sum(np.all(roi < 60, axis=2))
assert dark == 0, f"{dark} koyu piksel kaldı"
```

## Neden Clone Stamp?

| Yöntem | Sonuç |
|--------|-------|
| Crop | ❌ Kompozisyon bozulur |
| Inpainting | ⚠️ Bulanıklık yapabilir |
| Clone stamp | ✅ Geçiş fark edilmez, boyut korunur |

## Ne Zaman Inpainting Kullan?

Clone stamp **source bölgede de koyu piksel varsa** (sayfa numarası vb.) işe yaramaz. Bu durumda **Navier-Stokes inpainting** kullan:

```python
import cv2, numpy as np

img = cv2.imread("slayt.png")
h, w = img.shape[:2]
wx1, wx2 = 3423, 3791  # koordinatları görsele göre ayarla
wy1, wy2 = 1984, 2105

# Maske: sadece koyu yazı pikselleri
roi = img[wy1:wy2, wx1:wx2]
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
_, mask = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)

kernel = np.ones((2,2), np.uint8)
mask = cv2.dilate(mask, kernel, iterations=1)

full_mask = np.zeros((h, w), dtype=np.uint8)
full_mask[wy1:wy2, wx1:wx2] = mask

result = cv2.inpaint(img, full_mask, inpaintRadius=5, flags=cv2.INPAINT_NS)
cv2.imwrite("slayt_temiz.png", result)
```

Inpainting threshold'u (`80`) watermark yazı rengine göre ayarla. Koyu gri yazılar için `100`, açık gri için `60` kullan.

## Yöntem Seçim Kılavuzu

| Durum | Yöntem |
|-------|--------|
| Source bölge temiz (arka plan düz renk) | Clone stamp |
| Source bölgede de koyu piksel var | Navier-Stokes inpainting |
| Watermark çok büyük (>50px) | Inpainting |
| Görselde gradient/doku var | Inpainting |

İlk uygulama: 10 Temmuz 2026, "Belirsizlik Çağı ve Kaygı" karuseli.
