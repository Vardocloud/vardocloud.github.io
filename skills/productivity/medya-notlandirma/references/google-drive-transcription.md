# Google Drive Video Transkripsiyonu

Google Drive'daki seminer/kurs videolarını transkript etme workflow'u.

## Gerekenler

- Google Workspace skill (Drive erişimi) — OAuth ile authenticate olunmuş olmalı
- ffmpeg (ses çekme)
- Pollinations whisper-1 proxy (127.0.0.1:19999) — transkripsiyon

## Adım Adım

### 1. Videoları Bul

```python
# Google API service oluştur
import importlib.util
spec = importlib.util.spec_from_file_location('google_api', 'google_api.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
service = mod.build_service('drive', 'v3')

# Klasör ara
results = service.files().list(
    q="fullText contains 'klasor_adi'",
    fields='files(id, name, mimeType)'
).execute()

# Klasör içindekileri listele
folder_id = results['files'][0]['id']
files = service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    fields='files(id, name, mimeType, size)'
).execute()
# files['files'] → videoların listesi
```

**⚠️ ÖNEMLİ:** `drive search` wrapper'ı (`google_api.py drive search`) parents sorgularını desteklemez. Doğrudan `build_service().files().list()` kullan.

### 2. Audio Extraction (get_media + ffmpeg pipe)

Google Drive API'den videoyu stream ederken ffmpeg ile direkt WAV'a çevir (diske video yazmaz):

```python
from googleapiclient.http import MediaIoBaseDownload
import subprocess, os

output_dir = '/home/ubuntu/transcripts'
os.makedirs(output_dir, exist_ok=True)

file_id = 'GOOGLE_DRIVE_FILE_ID'
output_wav = f'{output_dir}/video_adi.wav'

request = service.files().get_media(fileId=file_id)
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
    if hasattr(status, 'progress'):
        print(f"  Progress: {int(status.progress() * 100)}%")
ffmpeg.stdin.close()
ffmpeg.wait()
# output_wav: ~1.4 MB/dk, 1 saatlik video ~40-50 MB
```

### 3. Pollinations whisper-1 ile Transkript

```python
import json, urllib.request, io, uuid

with open(output_wav, 'rb') as f:
    file_data = f.read()

boundary = uuid.uuid4().hex
body = io.BytesIO()
body.write(f'--{boundary}\r\n'.encode())
body.write(b'Content-Disposition: form-data; name="file"; filename="audio.wav"\r\n')
body.write(b'Content-Type: audio/wav\r\n\r\n')
body.write(file_data)
body.write(f'\r\n--{boundary}\r\n'.encode())
body.write(b'Content-Disposition: form-data; name="model"\r\n\r\n')
body.write(b'whisper-1')
body.write(f'\r\n--{boundary}\r\n'.encode())
body.write(b'Content-Disposition: form-data; name="language"\r\n\r\n')
body.write(b'en')  # en / tr
body.write(f'\r\n--{boundary}--\r\n'.encode())

req = urllib.request.Request(
    "http://127.0.0.1:19999/v1/audio/transcriptions",
    data=body.getvalue(),
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST"
)
with urllib.request.urlopen(req, timeout=300) as resp:
    result = json.loads(resp.read())
    text = result.get('text', '')

# Kaydet
with open(output_wav.replace('.wav', '_transcript.txt'), 'w', encoding='utf-8') as f:
    f.write(text)
```

### 4. Paralel İşlem (Birden Fazla Video)

Birden fazla video varsa sırayla işle — çünkü:
- Pollinations whisper-1 rate limit uygulayabilir
- Google Drive API'nin de kotası var
- CPU'da tek bir transkripsyon zaten kaynak yoğun

Arka planda indirme + transkripsiyon için `terminal(background=True, notify_on_complete=True)` kullan.

```python
# Her video için ayrı bir background process başlat
# terminal(background=True, notify_on_complete=True) ile
```

## Video Uzunluğu Tahmini (MP4 boyutundan)

| Kalite | 1 saat | 30 dk |
|--------|--------|-------|
| 1080p  | ~3-5 GB | ~1.5-2.5 GB |
| 720p   | ~1-2 GB | ~500 MB-1 GB |
| 480p   | ~500 MB-1 GB | ~250-500 MB |

WAV çıktı: ~40-50 MB / saat video

## WARP vs Google API

| Durum | Proxy |
|-------|-------|
| Google Drive API | `ALL_PROXY=""` (direkt) — WARP connection reset yapar |
| Google OAuth | `ALL_PROXY=""` — token yenileme için |
| YouTube yt-dlp | WARP zorunlu — Oracle IP Google tarafından engellenir |
| Pollinations proxy | Her iki şekilde de çalışır |

## İzlenen Transkripsiyon Yaklaşımı

Google Drive videosunun **tamamını indirmeden** sadece ses track'ini çekmek için:
1. `service.files().get_media(fileId=id)` ile API stream'i al
2. ffmpeg'e pipe'la (stdin)
3. ffmpeg `-vn` flag'i ile video stream'ini atla, sadece audio çıkar
4. Çıktıyı 16kHz mono WAV olarak kaydet

Bu yöntem:
- 4-5 GB indirip sonra silme derdinden kurtarır
- Sadece ~40-50 MB WAV yazar
- ffmpeg pipe sırasında progress gösterir
