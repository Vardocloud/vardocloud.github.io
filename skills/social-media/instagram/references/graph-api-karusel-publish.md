# Graph API ile Karusel Yayınlama

**Durum:** Calisiyor (27 Haziran 2026, API v24.0)

## On Kosullar
- Instagram Business Account + Facebook Page baglantisi
- Graph API token: instagram_content_publish scope'lu
- IG Business Account ID (ornek: 17841478124961208)
- Gorseller herkese acik URL'de olmali

## Akis (4 Adim)
1. Her gor sel icin IMAGE container olustur -> container_id
2. CAROUSEL container olustur (children=[id1,id2,...], caption=...) -> karusel_container_id
3. Container FINISHED olana kadar poll et (status_code kontrol)
4. media_publish ile yayinla

## Gorsel URL Saglama

### Cloudinary (ONCELIKLI) ⭐

Cloudinary'e upload icin iki yontem:

**Yontem 1 — Basic Auth (signature gerekmez, onerilen):**
```bash
curl -X POST "https://api.cloudinary.com/v1_1/<CLOUD_NAME>/image/upload" \
  -u "<API_KEY>:<API_SECRET>" \
  -F "file=@/path/to/image.jpg" \
  -F "public_id=<PUBLIC_ID>"
```

**Yontem 2 — Signature-based:**
SHA1(sorted_params + api_secret) ile imza olustur, POST data'da gonder.
(Dokumantasyon: https://cloudinary.com/documentation/upload_images)

**API Key + Secret erisimi (Bitwarden):**
```bash
# BWS (Bitwarden Secrets Manager)
export PATH="$HOME/.hermes/bin:$PATH"
bws secret list                              # tum secret'lari listele
bws secret get <SECRET_ID>                   # tek secret detayi

# bw-serve (port 8087)
curl -s http://localhost:8087/status         # durum kontrol
curl -s http://localhost:8087/list/object/items  # tum item'lar
```

**Cloudinary credential notu:** BWS'de `CLOUDINARY_API_KEY` secret'i cloud_name, api_key ve CLOUDINARY_URL icerir. Format: `cloudinary://api_key:api_secret@cloud_name`. BWS bazen value'yu maskeler (`**********`), gercek degeri almak icin `bws secret get <ID>` kullan.

### Unsigned Upload Preset (API Secret Gerektirmez)
Cloudinary Dashboard > Settings > Upload > Upload Presets > Add preset > Mode: Unsigned
```bash
curl -X POST "https://api.cloudinary.com/v1_1/<CLOUD_NAME>/image/upload" \
  -F "file=@image.jpg" \
  -F "upload_preset=<PRESET_NAME>"
```

### Diger Servisler (WSL/Docker'da CALISMAYABILIR)

Asagidaki servisler **WSL/Docker container** ortaminda calismayabilir (DNS cozulemez, upload timeout, 404). Docker disi bir ortamda calisiyorsan kullanilabilir:

- **catbox.moe** — `curl -F "reqtype=fileupload" -F "fileToUpload=@file" https://catbox.moe/api/upload`
- **0x0.st** — `curl -F "file=@file" https://0x0.st`
- **imgur** — `curl -H "Authorization: Client-ID <ID>" -F "image=@file" https://api.imgur.com/3/image`

### Calismayan:
- Pollinations URL'leri (`gen.pollinations.ai/image/...`) — Instagram "Media URI doesn't meet requirements" hatasi verir (code 9004)
- Local file path — erisilebilir olmali
- data URI — base64 kabul edilmez

## Pitfall'lar

- **image_url herkese acik URL olmali** — localhost, 127.0.0.1, WSL internal IP calismaz
- **Pollinations URL'leri calismaz** — query parameter icerdigi icin Instagram kabul etmez. Gorseli indirip catbox/0x0.st/imgur'a yukle
- **Container FINISHED degilse publish hata verir** — status_code poll etmeyi unutma
- **Rate limit** ~200 istek/saat. 7 slayt + 1 karusel + poll = ~16 istek
- **Token expires_at=0** olsa bile 60 gunde bir kontrol et. Sifre degisikligi token'i gecersiz kilar
- **API versiyonu** v24.0 test edildi, versiyon degisikliklerinde endpoint'leri kontrol et