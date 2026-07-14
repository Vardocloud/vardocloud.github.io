---
name: drive-video-transkript-pipeline
description: "Google Drive'daki MP4 videolari API stream + ffmpeg + faster-whisper ile transkript etme pipeline'i"
---

# Google Drive Video → Transkript Pipeline

## Ne Zaman Kullanilir
Google Drive'daki MP4 seminer/kayit videolarini transkript etmek icin.

## Pipeline
1. Drive'da dosyayi bul (klasor ID'si ile listele)
2. `service.files().get_media(fileId=ID)` ile stream et
3. ffmpeg pipe ile dogrudan wav'a cevir (16kHz mono PCM)
4. faster-whisper ile transkript et

## Kritik Noktalar
- **Dil secimi:** Yanlis dilde transkript almissan `language="en"` ile tekrar dene
- **Timeout:** >1.5 GB videolar foreground'da calismaz. `background=true` + `notify_on_complete=true` kullan
- **Buffer:** Python stdout buffer problemi yasaniyorsa `flush=True` ekle veya `-u` flag'i kullan
- **Paralel isleme:** CPU'da ayni anda tek whisper modeli calistir
- **Temizlik:** WAV dosyalari (~100-150 MB/video) transkript sonrasi silinebilir

## Ornek Kod

```python
import subprocess
from googleapiclient.http import MediaIoBaseDownload

request = service.files().get_media(fileId=VIDEO_ID)
ffmpeg_cmd = ['ffmpeg', '-i', 'pipe:0', '-vn', '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', '-f', 'wav', 'output.wav']
ffmpeg = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
downloader = MediaIoBaseDownload(ffmpeg.stdin, request)
done = False
while not done:
    status, done = downloader.next_chunk()
ffmpeg.stdin.close()
ffmpeg.wait()

from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu", compute_type="int8")
segments, _ = model.transcribe("output.wav", language="en", beam_size=5)
```
