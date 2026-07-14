---
name: media-transcription
description: "Video/ses dosyalarını Google Drive, yerel disk veya URL'den alıp Groq Whisper (birincil), Pollinations (yedek) veya faster-whisper (yerel) ile transkript etme ve analiz pipeline'ı"
version: 1.1.0
---

# Media Transcription Pipeline

**Amaç:** Video/ses dosyalarını çeşitli kaynaklardan alıp transkript etme ve analiz etme.

## Kaynak Türleri

### 1. Google Drive
Google Drive API üzerinden video/ses dosyasını stream et, ffmpeg ile direkt wav'a çevir.

- Google Workspace skill'ini yükle, `build_service('drive', 'v3')` ile service oluştur
- `service.files().get_media(fileId=...)` ile medyayı al
- `MediaIoBaseDownload` ile ffmpeg stdin'ine pipe et
- ffmpeg: `-ar 16000 -ac 1 -c:a pcm_s16le` parametreleriyle wav çıktısı al
- Büyük dosyalarda (4GB+) progress takibi ekle

**Not:** Dosyayı tamamen indirmeden stream etmek için `subprocess.Popen` ile ffmpeg'e pipe et.

### 2. Yerel Dosya
```bash
ffmpeg -i input.mp4 -vn -ar 16000 -ac 1 -c:a pcm_s16le -f wav output.wav
```

### 3. YouTube
YouTube videoları için NotebookLM MCP source_add(source_type='url') kullanılabilir. Alternatif: yt-dlp + ffmpeg.

## Uzun Dosyaları Chunk'a Bölme

20dk+ ses dosyaları için ffmpeg segment:
```bash
ffmpeg -i input.mp3 -f segment -segment_time 1200 -c copy chunk_%03d.mp3
```

- `-segment_time 1200` = 20 dk (1200 saniye)
- `-c copy` = stream copy (yeniden encode etmez, hızlı)
- 128kbps MP3'te her chunk ~18-19MB (Pollinations 25MB limitinin altında)
- Son chunk genellikle daha küçük olur

**Pitfall:** Zoom kayıtları seminer/etkinlik bittikten sonra da devam eder. Sessiz chunk'lar beklenmelidir — faster-whisper VAD filter ile bunlar otomatik atlanır (0 karakter döner).

## faster-whisper Transkripsiyon

- Model: `WhisperModel("base", device="cpu", compute_type="int8")`
- **Dil seçimi kritik:** 
  - `language="en"` — İngilizce içerik (net)
  - `language="tr"` — Türkçe içerik
  - `language=None` — Otomatik algılama (karışık dillerde riskli)
- **VAD Filter:** `vad_filter=True` ekle — sessiz bölümleri atlar, transkript kalitesini artırır, işlemi hızlandırır. Özellikle Zoom kayıtlarında (seminer sonrası boş kayıt) kritik.
- **Hız:** CPU'da base model ~83sn/20dk chunk.
- **Uyarı:** Türkçe model İngilizce konuşmayı zorlayınca "Yılmazlar", "Lira etmezdi" gibi anlamsız çıktı üretir. Her zaman önce dil algıla, sonra explicit dil ile tekrar dene
- Çıktı formatı: `[start_time - end_time] text`
- Timestamp'ler opsiyonel, ihtiyaca göre ekle/çıkar

## Groq Whisper ile Transkripsiyon (Birincil Yöntem) ⭐

**Groq Whisper (`whisper-large-v3`) transkripsiyon için birincil yöntemdir.** Türkçe dahil çoklu dil desteği sunar ve Pollinations proxy'den daha hızlıdır.

### Setup

Groq API key'i Bitwarden Secrets Manager'da `GROQ_API_KEY` olarak saklanır:

```bash
# BWS'den key'i al
GROQ_API_KEY=$(bws secret list | jq -r '.[] | select(.key=="GROQ_API_KEY") | .value')
# veya doğrudan env variable'dan
```

### API Kullanımı

```bash
curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F "file=@chunk.mp3" \
  -F "model=whisper-large-v3" \
  -F "language=tr"  # Dil zorunlu: tr / en / hiçbiri=None (otomatik)
```

- **Endpoint:** `https://api.groq.com/openai/v1/audio/transcriptions`
- **Model:** `whisper-large-v3` (Türkçe için en iyisi, çoklu dil desteği)
- **Format:** multipart/form-data
- **Dil parametresi:** 
  - `language=tr` — Türkçe içerik (önerilen)
  - `language=en` — İngilizce içerik
  - `language=None` — Otomatik algılama (karışık dillerde riskli — İngilizce kısmı anlamsız çıkar)
- **Response:** JSON `{ "text": "..." }` döner

### Chunk Boyutu ve Limitler

| Parametre | Değer |
|-----------|-------|
| Maksimum dosya boyutu | ~25MB (HTTP 413'ü önlemek için) |
| Önerilen chunk süresi | **20 dakika** (128kbps MP3'te ~18-19MB) |
| Bekleme süresi | Chunk'lar arasında **2 saniye** (rate limit) |

**ffmpeg ile chunk'a bölme:**
```bash
ffmpeg -i input.mp3 -f segment -segment_time 1200 -c copy chunk_%03d.mp3
```
- `-segment_time 1200` = 20 dakika
- `-c copy` = stream copy (yeniden encode etmez)

### Paralel Toplu Transkripsiyon (10 Tem 2026 — Kanıtlanmış)

Birden fazla kaydı aynı anda transkript etmek için:

```python
import subprocess, os, time, json

def transcribe_chunk(chunk_path, api_key, lang="tr"):
    """Tek chunk'ı Groq'a gönder, text döndür."""
    curl_cmd = [
        "curl", "-s", "-X", "POST",
        "https://api.groq.com/openai/v1/audio/transcriptions",
        "-H", f"Authorization: Bearer {api_key}",
        "-F", f"file=@{chunk_path}",
        "-F", "model=whisper-large-v3",
        "-F", f"language={lang}"
    ]
    result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=120)
    data = json.loads(result.stdout)
    return data.get("text", "")

def transcribe_recording(mp3_path, label, api_key, lang="tr"):
    """Bir MP3 kaydını chunk'lara böl, transkript et, birleştir."""
    # Dizin oluştur
    chunks_dir = f"chunks_{label}"
    os.makedirs(chunks_dir, exist_ok=True)
    os.makedirs(f"chunks_{label}/done", exist_ok=True)
    
    # Chunk'lara böl
    subprocess.run([
        "ffmpeg", "-y", "-i", mp3_path,
        "-f", "segment", "-segment_time", "1200",
        "-c", "copy", f"{chunks_dir}/chunk_%03d.mp3"
    ], check=True, capture_output=True)
    
    # Her chunk'ı transkript et
    chunks = sorted([f for f in os.listdir(chunks_dir) if f.endswith('.mp3')])
    transcript_parts = []
    
    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(chunks_dir, chunk)
        text = transcribe_chunk(chunk_path, api_key, lang)
        transcript_parts.append(text)
        # Chunk'ı taşı
        os.rename(chunk_path, os.path.join(f"{chunks_dir}/done", chunk))
        time.sleep(2)  # Rate limit
    
    # Birleştir ve kaydet
    full_transcript = "\n".join(transcript_parts)
    with open(f"transkript_{label}.md", "w") as f:
        f.write(f"# {label}\n\n**Toplam Süre:** ~{len(chunks)*20} dakika\n**Chunk Sayısı:** {len(chunks)}\n\n---\n\n{full_transcript}\n\n---\n*Groq Whisper (whisper-large-v3) ile oluşturulmuştur.*\n")
    
    return f"transkript_{label}.md"

# Kullanım:
# api_key = bws_secret_get("GROQ_API_KEY")
# api_key = os.environ["GROQ_API_KEY"]
# result = transcribe_recording("apa.mp3", "APA-EBSA", api_key, lang="tr")
# result = transcribe_recording("yt.mp3", "Bodynext-Masterclass", api_key, lang="tr")
```

### Dil Karışıklığı Sorunu (Bilinen)

**Whisper İngilizce+Türkçe karışımı içerikte sorun yaşar.** `language=tr` ile Türkçe kısım iyi transkript olur ama İngilizce konuşma "anlamsız Türkçe sesler" olarak çıkar (örneğin "school soccer team" → "skul sakır tim" gibi).

**Geçici çözüm:** Transkript sonrası manuel düzeltme veya NotebookLM'e ham halde yükle (NotebookLM Gemini contextual düzeltme yapabilir).

## Pollinations Proxy ile Transkripsiyon (Yedek / Fallback)

Groq kapalıysa veya API key yoksa Pollinations proxy kullan:

```bash
curl -s -X POST http://localhost:19999/v1/audio/transcriptions \
  -F "file=@chunk.mp3" -F "model=whisper-1" -F "language=tr"
```

**Önemli kısıtlar:**
- **Bakiye:** Her istek ~0.0015 pollen tüketir. Bakiye sıfırsa `PAYMENT_REQUIRED` hatası döner.
- **Dosya limiti:** 25MB üzeri chunk'lar proxy tarafından reddedilir.
- **Rate limiting:** API çağrıları arasında **2 saniye** beklenmelidir.
- **Model:** `whisper-1` (OpenAI Whisper) kullanılır.
- **Fallback:** Pollinations bakiyesi tükendiğinde yerel faster-whisper'a geç.

## Transkript Analizi

Analiz için LiteRouter deepseek-v3.2 kullanılır (`references/transkript-analiz-promptu.md`).

- Endpoint: `https://api.literouter.com/v1/chat/completions`
- Model: `deepseek-v3.2` (":free" soneki olmadan)
- Header: `User-Agent: Vanitas/1.0` zorunlu (yoksa 403)
- API Key: `LITEROUTER_API_KEY` env variable
- max_tokens: 4096, temperature: 0.3
- System prompt analiz prompt'u, user message transkript içeriği

## Referanslar
- `references/transkript-analiz-promptu.md` — Transkript analizi için system prompt

## Önemli Notlar
- **Dil seçimi kritik:** Yanlış dil modeli anlamsız çıktı üretir
- **Karışık dil (EN+TR):** Whisper `language=tr` ile İngilizce kısmı anlamsız sesler olarak transkript eder — ham haliyle NotebookLM'e yüklenebilir (Gemini bağlamsal düzeltme yapabilir)
- **CPU mode:** GPU yoksa yavaş ama çalışır
- **Disk temizliği:** WAV dosyaları ~40-150MB, transkript sonrası sil
- **Paralel işlem:** Birden fazla video varsa download+transcribe paralel yapılabilir (watch CPU)
- **Groq API Key:** BWS (Bitwarden Secrets Manager) 'de `GROQ_API_KEY` olarak saklanır. `bws secret list` ile bul, ID ile al.
- **Chunk sırası:** Chunk'lar `chunk_000.mp3`, `chunk_001.mp3` sırasıyla işlenmeli — sessiz chunk'lar atlanmamalı (sıra korunur)
