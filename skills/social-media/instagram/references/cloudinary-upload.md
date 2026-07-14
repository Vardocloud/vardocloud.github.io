# Cloudinary Upload — Karusel Görselleri İçin

## Neden Cloudinary?

WSL/Docker ortamında Catbox.moe, 0x0.st, Imgur gibi upload servisleri çalışmayabilir (DNS, WARP proxy, dosya yolu sorunları). Cloudinary en güvenilir alternatiftir.

## Unsigned Upload Preset (ÖNERİLEN)

API secret yönetimi sorun çıkarır. **Unsigned upload preset** ile API secret gerekmez.

### Kurulum (tek seferlik)
1. Cloudinary Dashboard → **Settings** → **Upload** sekmesi
2. **Upload presets** bölümü → **Add preset**
3. Preset name: örn. `karusel_upload`
4. **Signing Mode**: **Unsigned** seç
5. Save

### Kullanım

```python
import requests

cloud_name = "dqpqusi3e"  # veya kendi cloud_name'in
preset = "karusel_upload"

with open("slayt.jpg", "rb") as f:
    resp = requests.post(
        f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload",
        data={"upload_preset": preset, "public_id": "benzersiz_id"},
        files={"file": f}
    )
data = resp.json()
url = data["secure_url"]  # https://res.cloudinary.com/...
```

## Signed Upload (Alternatif — API Secret Gerekli)

### Auth Yöntemleri

#### 1. HTTP Basic Auth (ÖNERİLEN)
```bash
curl -u "API_KEY:API_SECRET" \
  -F "file=@slayt.jpg" \
  -F "public_id=karusel_01" \
  https://api.cloudinary.com/v1_1/CLOUD_NAME/image/upload
```

#### 2. Signature-based Auth
```python
import hashlib, time, requests

params = {"timestamp": int(time.time()), "public_id": "..."}
sorted_str = "&".join(f"{k}={v}" for k,v in sorted(params.items()))
signature = hashlib.sha1((sorted_str + API_SECRET).encode()).hexdigest()

with open("slayt.jpg", "rb") as f:
    resp = requests.post(
        f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/image/upload",
        data={"api_key": API_KEY, "timestamp": params["timestamp"],
              "public_id": params["public_id"], "signature": signature},
        files={"file": f}
    )
```

### İmza Hatası ("Invalid Signature")
- Secret yanlış olabilir → `bw-serve` veya BWS'den teyit et
- SHA-1 kullanıldığından emin ol (Cloudinary varsayılanı)
- `api_key` POST body'de gönder ama imzaya DAHİL ETME
- `file`, `cloud_name`, `resource_type`, `signature` parametreleri imzaya dahil edilmez

### "api_secret mismatch" Hatası
- Basic Auth'ta bu hata = API Key ile API Secret eşleşmiyor
- Cloudinary Dashboard → Settings → API Keys'ten doğrula
- Çözüm: unsigned upload preset'e geç (API secret gerekmez)

## Görsel Optimizasyonu (Instagram Karusel İçin)

Cloudinary'e yüklemeden önce görselleri Instagram formatına çevir:

```python
from PIL import Image

img = Image.open("slayt.png")
target_w, target_h = 1080, 1350  # Instagram karusel (4:5)

# Oranı koru, padding ekle
orig_w, orig_h = img.size
scale = target_w / orig_w
new_w, new_h = int(orig_w * scale), int(orig_h * scale)
img_resized = img.resize((new_w, new_h), Image.LANCZOS)

if new_h < target_h:
    # Pastel arkaplan padding
    canvas = Image.new("RGB", (target_w, target_h), "#F5F0EB")
    y_offset = (target_h - new_h) // 2
    canvas.paste(img_resized, (0, y_offset))
    final = canvas
else:
    # Fazla yüksekliği crop et
    crop_top = (new_h - target_h) // 2
    final = img_resized.crop((0, crop_top, target_w, crop_top + target_h))

final.save("slayt.jpg", "JPEG", quality=92)
```

## Üretimde Dikkat Edilecekler

- Unsigned upload preset **önceden ayarlanmalı** — kod içinde oluşturulamaz
- `public_id` benzersiz olmalı (timestamp ekle: `karusel_{konu}_{i:02d}`)
- `secure_url` HTTPS linkidir, image_url olarak kullanılır
- Rate limit: Cloudinary Upload API rate-unlimited'dır
- EU bölgesi için `api-eu.cloudinary.com` endpoint'ini kullan
