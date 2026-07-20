---
name: media-transcription
description: "Video/ses dosyalarını Google Drive, yerel disk veya URL'den alıp Groq Whisper (birincil), Pollinations (yedek) veya faster-whisper (yerel) ile transkript etme ve analiz pipeline'ı"
version: 1.3.0
---

# Media Transcription Pipeline

**Amaç:** Video/ses dosyalarını çeşitli kaynaklardan alıp transkript etme ve analiz etme.

## ⚠️ ZORUNLU: Transkripsiyon Öncesi Dil Seçimi

**Her transkripsiyondan ÖNCE içeriğin dilini belirle. Yanlış dilde transkripsiyon çıktıyı kullanılamaz hale getirir.**

| İçerik Dili | `language=` parametresi |
|-------------|------------------------|
| 🇹🇷 Türkçe (seminer, ders, Türkçe konuşma) | `language=tr` |
| 🇬🇧 İngilizce (APA webinar, uluslararası etkinlik) | `language=en` |
| 🤔 Emin değilsen | Dosya adına bak veya 10 saniye dinle |

**Tespit yöntemi:** Dosya adında "APA", "International", "English", yabancı konuşmacı adı varsa → `language=en`. Türkçe başlık, Türkçe konuşmacı, "seminer", "eğitim" varsa → `language=tr`.

**Bilinen hata (20 Tem 2026):** `language=tr` ile İngilizce içerik transkript edilince çıktı anlamsız Türkçe fonetik dönüşüme uğrar. APA EBSA, APA Mentoring, Masculinity Psychology bu hatayı yaşadı. Çözüm: `language=en` ile yeniden transkript et.

**Doğrulama:** Transkripsiyon sonrası ilk 100 karakterde Türkçe karakterler (ğ, ü, ş, ı, ö, ç) varsa veya "Altyazı M.K." gibi anlamsız tekrarlar görülüyorsa → dil yanlış, yeniden dene.

### Script Kullanımı

```bash
# Yeni evrensel script (önerilen):
~/scripts/transkript.sh chunks_apa/ output.md "Başlık" en    # İngilizce
~/scripts/transkript.sh chunks_miuul/ output.md "Başlık"     # Türkçe (varsayılan)

# Eski script (güncellendi — LANG env değişkeni alır):
LANG=en ~/.hermes/scripts/transkript_all.sh   # İngilizce
~/.hermes/scripts/transkript_all.sh            # Türkçe (varsayılan)
```

## 🔴 Rate Limit: Groq Whisper (7200 sn/saat)

**Groq `whisper-large-v3` için saatlik limit:** 7200 saniye ses (rolling window).

| Durum | Ne olur | Ne yapılmalı |
|-------|---------|-------------|
| Limit aşıldı | API `429` döner: "Rate limit reached... ASPH: Limit 7200, Used X, Requested Y" | Hatadaki `Try again in Xm` süresini bekle, sonra devam et |
| Normal işlem | Her chunk ~20 dk (1200 sn) tüketir | 6 chunk = limitin tamamı |

**Hesaplama:** 7200 sn / 1200 sn(her chunk) = max 6 chunk/saat.

**Recovery stratejisi:**
- Rate limit hatası alınca kaç saniye bekleneceğini error mesajından oku
- Bekleme süresince diğer hazırlıkları yap (chunk'lama, ön işleme)
- Kalan chunk'ları saat dilimi sıfırlanınca transkript et
- Toplu transkripsiyon planlanırken bu limit göz önünde bulundurulmalı

**Detay:** `references/groq-rate-limit.md`

---

**Google Meet otomatik altyazıları (captions) Türkçe için GÜVENİLİR DEĞİLDİR.** 17 Temmuz 2026'da test edilmiş ve onaylanmıştır: Meet'in İngilizce otomatik çevirisi Türkçe konuşmayı anlamsız karakterlere dönüştürür.

**Kural — transkripsiyon yöntem seçimi:**
- Türkçe veya karışık TR/EN içerik → **Ses kaydı + Groq Whisper (whisper-large-v3)** birincil
- Sadece İngilizce içerik → Meet captions yeterli olabilir
- Asla Meet captions'ı Türkçe için yeterli GÖRME

**Canlı toplantıda ses yakalama ön koşulları:**
- `pulseaudio --check` OK olmalı
- `ffmpeg` kurulu olmalı
- `GROQ_API_KEY` env'de veya BWS'de olmalı
- Eksik varsa → Edel'e hemen bildir

**Kayıt sonradan gelirse:** Bu skille ait tüm yöntemler kullanılabilir.

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
  - `language="en"` — İngilizce içerik
  - `language="tr"` — Türkçe içerik
  - `language=None` — Otomatik algılama (karışık dillerde riskli)
- **VAD Filter:** `vad_filter=True` ekle — sessiz bölümleri atlar, transkript kalitesini artırır
- **Hız:** CPU'da base model ~83sn/20dk chunk.
- **Uyarı:** Türkçe model İngilizce konuşmayı zorlayınca anlamsız çıktı üretir. Her zaman önce dil algıla, sonra explicit dil ile tekrar dene

## Groq Whisper ile Transkripsiyon (Birincil Yöntem) ⭐

**Groq Whisper (`whisper-large-v3`) transkripsiyon için birincil yöntemdir.**

### Setup

Groq API key'i Bitwarden Secrets Manager'da `GROQ_API_KEY` olarak saklanır:

```bash
GROQ_API_KEY=$(bws secret list | jq -r '.[] | select(.key=="GROQ_API_KEY") | .value')
```

### API Kullanımı

```bash
curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F "file=@chunk.mp3" \
  -F "model=whisper-large-v3" \
  -F "language=tr"  # İçeriğin diline göre tr/en
```

- **Endpoint:** `https://api.groq.com/openai/v1/audio/transcriptions`
- **Model:** `whisper-large-v3`
- **Format:** multipart/form-data
- **Dil parametresi:** `tr` / `en` (içeriğe göre seç, asla sabit varsayılan kullanma)
- **Response:** JSON `{ "text": "..." }` döner

### Chunk Boyutu ve Limitler

| Parametre | Değer |
|-----------|-------|
| Maksimum dosya boyutu | ~25MB (HTTP 413'ü önlemek için) |
| Önerilen chunk süresi | **20 dakika** (128kbps MP3'te ~18-19MB) |
| Bekleme süresi | Chunk'lar arasında **2 saniye** |
| Saatlik ses limiti | **7200 saniye** (roling window, ~6 chunk/saat) |

### Dil Karışıklığı Sorunu (Bilinen)

**Whisper İngilizce+Türkçe karışımı içerikte sorun yaşar.** `language=tr` ile Türkçe kısım iyi transkript olur ama İngilizce konuşma anlamsız sesler olarak çıkar.

**Çözüm:** İçerik tek dilli ise doğru `language=` parametresini kullan. Karışık dilli içerikte:
- Ham transkripti NotebookLM'e yükle (Gemini bağlamsal düzeltme yapabilir)
- Veya içeriği dil bazında ayırıp ayrı ayrı transkript et

## Pollinations Proxy ile Transkripsiyon (Yedek / Fallback)

Groq kapalıysa veya API key yoksa Pollinations proxy kullan:

```bash
curl -s -X POST http://localhost:19999/v1/audio/transcriptions \
  -F "file=@chunk.mp3" -F "model=whisper-1" -F "language=tr"
```

**Önemli kısıtlar:**
- **Bakiye:** Her istek ~0.0015 pollen tüketir
- **Dosya limiti:** 25MB üzeri chunk'lar reddedilir
- **Rate limiting:** 2 saniye bekle
- **Model:** `whisper-1` (OpenAI Whisper)
- **Fallback:** Bakiye tükenince faster-whisper'a geç

## Transkript Analizi

Analiz için LiteRouter deepseek-v3.2 kullanılır (`references/transkript-analiz-promptu.md`).

- Endpoint: `https://api.literouter.com/v1/chat/completions`
- Model: `deepseek-v3.2`
- Header: `User-Agent: Vanitas/1.0` zorunlu (yoksa 403)
- max_tokens: 4096, temperature: 0.3

## Post-Transkripsiyon: Adlandırma + Özet + Wiki + NotebookLM Pipeline

### 0. Ön Kontrol: Mevcut Rapor/Özet Var mı?

Transkript dosyası bozuk/garbled ise `~/recordings/` dizininde `rapor_` ile başlayan dosyaları kontrol et. Varsa içeriklerini oku ve doğrudan kullan.

### 1. Dosya Adlandırma Standardı

```bash
~/recordings/{YYYY-MM-DD}-{konu-slug}.md
```

- Tarih başa, tire ile ayrılmış küçük harfler
- Kısa ve tanımlayıcı (2-5 kelime)
- Bozuk dosyalar: `garbled-` veya `empty-` ön eki

### 2. Özet Çıkarma (ZORUNLU)

Her transkripsiyon sonrası ana konu, 3-5 başlık, önemli vaka/veri, pratik çıkarım çıkarılır. Subagent'larla paralel işlenebilir.

### 3. Wiki → NotebookLM Bridge

Wiki sayfası oluşturulduktan sonra NotebookLM Vault'a da eklenir.

```bash
nlm source add <NOTEBOOK_UUID> --file ~/.hermes/wiki/seminerler/... --title "..." --wait --wait-timeout 120
```

## Referanslar
- `references/transkript-analiz-promptu.md` — Transkript analizi için system prompt
- `references/meeting-prep-checklist.md` — Canlı toplantı öncesi hazırlık kontrol listesi
- `references/groq-rate-limit.md` — Groq API rate limit detayları ve kurtarma stratejisi

## Önemli Notlar
- **Dil seçimi kritik:** Bu skill'in en önemli kuralıdır. Her transkripsiyondan önce içerik dilini tespit et
- **Karışık dil (EN+TR):** Whisper `language=tr` ile İngilizce kısmı anlamsız sesler olarak transkript eder
- **Rate limit:** Saatte max 7200 sn ses (6 chunk)
- **Chunk sırası:** Chunk'lar dosya sırasıyla işlenmeli, sessiz chunk'lar atlanmamalı
- **Scriptler:** `~/scripts/transkript.sh` (yeni evrensel) ve `~/.hermes/scripts/transkript_all.sh` (güncellendi, LANG env alır)
