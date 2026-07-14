---
name: medya-notlandirma
description: "YouTube/Instagram/podcast/Google Drive videoları → transkripsiyon + yapılandırılmış not. 2 katmanlı strateji (NotebookLM → Pollinations whisper-1 proxy), görsel analiz, wiki entegrasyonu."
version: 2.1.0
metadata:
  hermes:
    tags: [youtube, instagram, transkript, pipeline, medya, google-drive, notebooklm]
    category: productivity
---

# Medya Notlandırma Pipeline v2.1

**Kapsam:** YouTube, Instagram Reels, podcast, ses dosyası, **Google Drive videoları** → transkripsiyon + yapılandırılmış not.
`transcription` ve `youtube-transkript` skill'lerini absorbe etti.

## Tetikleyiciler

- YouTube linki (`youtube.com/watch?v=` veya `youtu.be/`)
- Instagram Reels/Post linki
- Google Drive'daki video/seminer klasörü ("Drive'daki videoları transkript et")
- "Vanitas videoyu izleyip not alır mısın?"
- "Bu videodan not çıkar"
- Podcast/ses transkripti isteği

---

## 2 Katmanlı Transkripsiyon (Hız Sırasıyla)

| Katman | Yöntem | Hız | Ne Zaman |
|--------|--------|-----|----------|
| 🥇 | **NotebookLM direkt link** | ~3sn | YouTube linki varsa — HER ZAMAN önce bunu dene |
| 🥈 | **Pollinations whisper-1 (proxy)** | ~1.3x realtime | Google Drive videosu, podcast, ses — TÜM ses transkripsiyonu için TEK tercih |

**KRİTİK KURAL:** Yerel faster-whisper ASLA kullanma. Edel CPU'yu kastırdığı gerekçesiyle kaldırılmasını istedi. Tüm transkripsiyon işlemleri sadece Pollinations API üzerinden yapılır.
**KRİTİK KURAL 2:** Google Drive videolarını indirirken faster-whisper kullanma — aynı kural geçerli. Audio'yu Pollinations whisper-1 proxy'e gönder.

### Katman 1: NotebookLM (En Hızlı — ~10-15sn)

```python
# NotebookLM YouTube linklerinden direkt caption çeker
mcp_notebooklm_mcp_source_add(notebook_id="...", source_type="url", url="https://youtu.be/VIDEO_ID")
# ⚠️ Kaynak işlenene kadar 10-15 saniye bekle (ready: false → true)
mcp_notebooklm_mcp_source_get_content(source_id="...")
# → Transkript hazır, sıfır maliyet
```

### Katman 2: Pollinations whisper-1 (Lokal proxy üzerinden)

```python
import json, urllib.request, io, uuid

with open('ses.mp3', 'rb') as f:
    file_data = f.read()

boundary = uuid.uuid4().hex
body = io.BytesIO()
body.write(f'--{boundary}\r\n'.encode())
body.write(b'Content-Disposition: form-data; name="file"; filename="audio.mp3"\r\n')
body.write(b'Content-Type: audio/mpeg\r\n\r\n')
body.write(file_data)
body.write(f'\r\n--{boundary}\r\n'.encode())
body.write(b'Content-Disposition: form-data; name="model"\r\n\r\n')
body.write(b'whisper-1')
body.write(f'\r\n--{boundary}\r\n'.encode())
body.write(b'Content-Disposition: form-data; name="language"\r\n\r\n')
body.write(b'tr')
body.write(f'\r\n--{boundary}--\r\n'.encode())

req = urllib.request.Request(
    "http://127.0.0.1:19999/v1/audio/transcriptions",
    data=body.getvalue(),
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST"
)

with urllib.request.urlopen(req, timeout=120) as resp:
    result = json.loads(resp.read())
    text = result.get('text', '')
    print(text)
```

- **Endpoint:** `http://127.0.0.1:19999/v1/audio/transcriptions` (lokal Pollinations proxy)
- **Model:** `whisper-1` (API key gerektirmez, proxy otomatik ekler)
- **Format:** multipart/form-data, MP3 veya WAV
- **Dil:** `tr` parametresi zorunlu (Türkçe accuracy için). İngilizce içeriklerde `en` kullan.
- **Limit yok** — proxy'den geçen her şey çalışır

---

## Google Drive Video → Transkripsiyon Workflow

Google Drive'daki videoları transkript etmek için:

### 1. Videoları Bul

```python
# Google Workspace skill'ini yükle, drive search kullan
# Not: drive search wrapper'ı parents sorgularını desteklemez
# Bunun yerine doğrudan build_service kullan:
from google_api import build_service
service = build_service('drive', 'v3')
results = service.files().list(
    q="'FOLDER_ID' in parents and trashed=false",
    pageSize=20,
    fields='files(id, name, mimeType, modifiedTime, webViewLink, size)'
).execute()
```

### 2. Audio Extraction (get_media + ffmpeg pipe)

Google Drive API'nin `get_media()` metodunu ffmpeg'e pipe ederek videoyu diske yazmadan direkt WAV'a çevir:

```python
from googleapiclient.http import MediaIoBaseDownload
import subprocess

request = service.files().get_media(fileId=VIDEO_FILE_ID)
output_wav = "/tmp/video_audio.wav"

ffmpeg_cmd = [
    'ffmpeg', '-i', 'pipe:0', '-vn',
    '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le',
    '-f', 'wav', output_wav
]
ffmpeg = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
downloader = MediaIoBaseDownload(ffmpeg.stdin, request)
done = False
while not done:
    status, done = downloader.next_chunk()
ffmpeg.stdin.close()
ffmpeg.wait()
# → output_wav hazır (~video_süresi × 1.4 MB/dk)
```

Bu yöntem:
- 4-5 GB video indirmez, sadece ses track'ini çeker
- Çıktı ~35-50 MB (1 saatlik video için)
- Google Drive'a authenticate olmuş halinle çalışır (ek auth gerekmez)

### 3. Pollinations whisper-1 ile Transkript

```python
# Yukarıdaki Katman 2 kodunu kullan
# Dil: içerik İngilizceyse language='en', Türkçeyse 'tr'
with open(output_wav, 'rb') as f:
    # ... multipart POST to Pollinations proxy
```

### ⚠️ WARP vs Google API Çakışması

WARP SOCKS5 proxy'si Google API'lerini (Drive, OAuth, Gmail) **engelliyor**.
Google Drive işlemleri için `ALL_PROXY=""` ile direkt bağlan.

- Google Drive / OAuth → `ALL_PROXY=""` (direkt bağlantı)
- YouTube auto-caption için WARP şart (Google IP engeli)
- Kural: Google servisi → ALL_PROXY="", diğer her şey → WARP

---

## YouTube Özel: Auto-Caption (yt-dlp)

```bash
# Türkçe auto-caption kontrol
yt-dlp --proxy socks5://127.0.0.1:1080 --write-auto-subs --sub-lang tr --skip-download \
  --convert-subs srt "URL" -o "/tmp/transcript_%(id)s"
```

WARP proxy zorunlu (Oracle IP'si Google tarafından engelleniyor).

---

## Görsel Analiz (Video Kareleri)

```bash
# Her 3 saniyede bir kare çıkar
ffmpeg -i video.mp4 -vf "fps=1/3" frames/frame_%02d.jpg

# Pollinations qwen-vision ile analiz
for f in frames/*.jpg; do
  base64 "$f" | curl -X POST "https://gen.pollinations.ai/v1/chat/completions" \
    -H "Authorization: Bearer $POLLINATIONS_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"qwen-vision","messages":[{"role":"user","content":"Bu karede ne var?"}],...}'
done
```

### ❌ KALDIRILDI: browser_vision (Azure filter)
- **Sebep:** Instagram ekran görüntülerinde Azure content filter engelliyor
- **Yerine:** Pollinations qwen-vision API (doğrudan, filtresiz)

---

## Instagram Reels Pipeline

Instagram Reels için **yetkili skill:** `instagram`. Bu skill'deki IG aksamı `instagram` skill'ine taşındı.

Özet: `instagram-reel-indirme` → `instagram` skill'ine absorbe edildi.

İhtiyaç halinde: `instagram` skill'ini yükle → cookie + WARP → yt-dlp indir → Pollinations whisper-1 transkript.

---

## Yapılandırılmış Not (Evrensel Prompt)

Transkript hazır olduktan sonra:

1. `~/.hermes/prompts/evrensel-transkript-donusturucu.md` prompt'unu yükle
2. Ham transkripti temizle, başlıklandır, ikinci geçişle eksik tamamla
3. Çıktıyı `~/wiki/concepts/` altına kaydet
4. İstenirse NotebookLM'de podcast/study guide üret

---

## Tarayıcı Politikası

- **Playwright** (lokal Chromium headless) → tüm yeni işler için standart
- **Browserbase** → TERK EDİLDİ (3. parti ABD, timeout, KVKK uyumsuz)

---

## Çıktı Formatı

```
╔══════════════════════════╗
║  👁️ GÖRSEL (N kare)     ║
║  00s → ...              ║
╠══════════════════════════╣
║  🎙️ SES (transkript)    ║
║  "..."                  ║
╠══════════════════════════╣
║  🧠 ÖZET                ║
╚══════════════════════════╝
```

---

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| NotebookLM caption yok | Katman 2'ye geç (Pollinations whisper-1) |
| Pollinations whisper-1 502 | Proxy çalışmıyor — `systemctl --user restart pollinations-proxy` dene |
| 20dk üstü ses | 20'şer dakika parçala, 5sn overlap |
| Google Drive parents sorgusu | `drive search` wrapper'ı desteklemez — doğrudan `build_service().files().list()` kullan |
| Google Drive + WARP | Connection reset — `ALL_PROXY=""` ile direkt bağlan |
| IG Reels erişimi | `instagram` skill'ini yükle |
