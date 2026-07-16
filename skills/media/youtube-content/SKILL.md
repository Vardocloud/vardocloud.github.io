---
name: youtube-content
description: "YouTube içeriğini işle: transkript çek → notebooklm'e ekle → wiki'ye kaydet → değerlendir → uygulama fikri yürüt. ASLA özet çıkarma."
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link.

## 🎯 MODE DECISION — Casual Share vs Deep Processing

**This is the most important decision in the skill.** Choosing the wrong mode wastes time or misses the point.

### Mode A: Casual Share (Quick Overview for Discussion)
**When:** Edel shares a link without asking for transcript/work/processing. She just says "look at this" or shares it mid-conversation.
**What to do:** `web_extract(urls=["URL"])` → read the summary → analyze relevance to Edel's situation → discuss. No transcription, no pipeline, no wiki/NotebookLM save unless she asks.
**Examples:** "Vanitas şuna bak", "Ne diyorsun?", link drop with no instruction.
**Output:** Concise summary + personal relevance analysis. No deep processing.

### Mode B: Deep Processing (Full Pipeline)
**When:** Edel explicitly asks for transcript, analysis, saving to wiki/NotebookLM, or anything involving the content itself.
**What to do:** Follow the full 3-method transcription pipeline → wiki save → NotebookLM save → deep content extraction.
**Output:** Full transcript + structured content + dual save.

### Mode C: Structured Output
**When:** Edel asks for a specific format (blog post, thread, chapter list, etc.).
**What to do:** Pipeline til you have clean text → then convert to requested format.

### How to choose
1. Did Edel say "transkript", "kaydet", "işle", "wiki", "NotebookLM", "özümle", "çevir", "çıkar"? → **Mode B**
2. Did she say "şuna bak", "ne diyorsun", "haberin olsun", or just drop the link with commentary? → **Mode A**
3. Did she name a format ("post yap", "thread yap", "bölümler halinde")? → **Mode C**
4. Not sure? **Just ask:** "Bunu işlememi ister misin yoksa sadece haberin olsun mu istedin?" — don't guess.

## ⚠️ KRİTİK: Önce İZLE/DİNLE, Sonra Rapor Et

**Bu kuralın ihlali Edel'in en çok şikayet ettiği hatadır.**

- Bir video/link hakkında **asla** thumbnail, başlık, ilk birkaç saniye veya yorumlardan yola çıkarak içeriği tahmin etme
- "Muhtemelen şu konuda", "şunla ilgili olabilir", "büyük ihtimalle" gibi ifadeler kullanma — bunlar çıkarım/hallüsinasyondur
- web_extract ile ön tarama yapabilirsin (yönlendirme için) ama o özeti **asla** nihai içerik olarak kullanma
- Video/link'in **tamamını** tüket (izle/dinle/oku) ve ancak ondan sonra rapor ver
- Bunu atlarsan Edel'in tepkisi net olur: "Sen direk özet geçmişsin" — güven kaybı

**Doğru akış:**
1. İçeriğin tamamını tüket (browser + vision, yt-dlp + transcript, web_extract ile tam metin)
2. Notlarını çıkar
3. Sentezle ve raporla
4. Ancak ondan sonra uygulama/çıkarım yap

Also useful for: requesting a transcript, extracting chapters/quotes, or reformatting content for analysis.

**3 katmanlı transkripsiyon stratejisi (Edel onaylı):**
1. YouTube auto-caption (WARP ile) — her zaman önce dene
2. Pollinations whisper API — auto-caption overlapping/yoksa ana yol
3. Yerel faster-whisper small — Pollinations down ise son çare

⚠️ **SRT overlapping tuzağı:** YouTube auto-caption'ları SRT formatında her cümleyi 3 kere tekrarlar (overlapping segments). `clean_srt.py` sadece zaman damgalarını temizler, 3x tekrarı gidermez. Çıktıda aynı cümleler 3'er 3'er tekrarlanıyorsa — **metin hala okunabilir**, segmentasyon ve pattern eşleştirme ile yapısal içerik çıkarılabilir. Sadece tamamen okunamaz durumdaysa Method 2'ye geç.

Detaylı karşılaştırma: `references/transcription-methods.md`
ARM64 benchmark: `references/whisper-small-benchmark.md`
x86_64 benchmark + Whisper Türkçe sınırlamaları: `references/x86-64-whisper-benchmark.md`
SRT temizleme: `python3 SKILL_DIR/scripts/clean_srt.py input.srt output.txt`

## Setup

```bash
pip install yt-dlp youtube-transcript-api
uv pip install PySocks  # SOCKS5 proxy desteği (cloud IP'ler için)
```

**⚠️ python3 -m yt_dlp vs yt-dlp:** Eğer `yt-dlp` komutu PATH'te bulunamazsa (exit code 127), pip ile kurulmuş olabilir. `python3 -m yt_dlp` şeklinde çağırmayı dene. Skill'deki tüm `yt-dlp` komutları, `python3 -m yt_dlp` ile değiştirilerek de kullanılabilir.

## Transcript Extraction Methods (KATI tercih sırası — bunu değiştirme!)

### Method 1: yt-dlp auto-captions (HER ZAMAN ÖNCE BUNU DENE)

YouTube'un otomatik altyazılarını doğrudan indirir. Saniyeler içinde tamamlanır. Cloud IP'ler için WARP proxy gerekir.

**⚠️ ytInitialPlayerResponse timedtext tuzağı:** Browser'dan aldığın caption URL'si dışarıdan curl ile çağrıldığında HTTP 200 + boş gövde dönebilir (signature IP binding). Bu URL'ye güvenme — doğrudan yt-dlp ile dene. Detay: Error Handling > "YANILGI — ytInitialPlayerResponse timedtext URL"

```bash
# Metadata kontrol (auto-caption var mı?)
# yt-dlp PATH'te yoksa "python3 -m yt_dlp" dene
CMD="yt-dlp"
which $CMD >/dev/null 2>&1 || CMD="python3 -m yt_dlp"

$CMD --proxy socks5://127.0.0.1:1080 --dump-json "URL" -o /dev/null > /tmp/v.json 2>/dev/null \
  && python3 -c "import json; d=json.load(open('/tmp/v.json')); print(f'title: {d[\"title\"]}\nduration: {d[\"duration\"]}s'); ac=d.get('automatic_captions',{}); print(f'auto-captions: {list(ac.keys()) if ac else \"YOK\"}')"

# Türkçe auto-caption'ları SRT formatında indir (video indirilmez)
CMD="yt-dlp"; which $CMD >/dev/null 2>&1 || CMD="python3 -m yt_dlp"
$CMD --proxy socks5://127.0.0.1:1080 \
  --write-auto-subs --sub-lang tr --skip-download --convert-subs srt \
  "URL" -o "/tmp/transcript_%(id)s"
```

**ÖNEMLİ:** yt-dlp JSON çıktısı pipe ile Python'a aktarılamaz (stderr karışır). Dosyaya yazıp sonra oku. `-o /dev/null > file 2>/dev/null` kalıbını kullan.

**Proxy fallback:** WARP proxy zaman aşımına uğrarsa veya bağlanamazsa, proxy'siz dene. Cloud IP olsa bile bazen çalışır (sadece JS runtime uyarısıyla — `WARNING: [youtube] No supported JavaScript runtime could be found`). Bu uyarı format seçimini etkileyebilir ama auto-caption indirme genelde çalışır. Proxy hatası alındığında önce `--proxy` olmadan tekrar dene.

### Method 2: Pollinations Whisper (auto-caption YOKSA veya BOZUKSA — ana yol)

Cloud tabanlı, hızlı. 60dk video ~2-3dk. Türkçe doğruluk çok iyi.

**⚠️ Maliyet:** Her Whisper isteği ~0.0020 pollen tüketir (16dk video, 31MB WAV). Bakiye 0.0003 gibi düşükse HTTP 402 alırsın. Kullanmadan önce bakiye kontrolü yoksa, hatayı alınca Method 3'e geç (vakit kaybetme). Detay: `references/pollinations-whisper-api.md`

```bash
# 1. Sesi indir (format 140 = medium m4a)
yt-dlp --proxy socks5://127.0.0.1:1080 -f 140 "URL" -o "/tmp/yt_audio.%(ext)s"
```

**⚠️ Format 140 (m4a) yoksa — Android client fallback (12 Tem 2026):**
Cloud IP'lerde YouTube bazen ayrı ses formatı (140) döndürmez, sadece HLS video+audio formatları (91-96) verir. Bu durumda progressive download çok daha hızlıdır:

```bash
# Önce android client ile formatları listele
CMD="yt-dlp"; which $CMD >/dev/null 2>&1 || CMD="python3 -m yt_dlp"
$CMD --extractor-args "youtube:player_client=android" --list-formats "URL"
# Format 18 (progressive 360p MP4, ~130MB/31dk) genelde gelir
$CMD --extractor-args "youtube:player_client=android" -f 18 \
  --extract-audio --audio-format mp3 "URL" -o "/tmp/yt_audio.%(ext)s"
```

Progressive HTTP download, HLS segment streaming'den çok daha hızlıdır. 12 Tem 2026 test: 31dk video ~35sn'de indi + MP3'e dönüştü (3.69 MiB/s). WARP proxy gerektirmez (android client direct HTTP).

Detaylı benchmark (android fallback + whisper): `references/android-fallback-benchmark-12tem2026.md`

# 2. 16kHz mono wav'a çevir
ffmpeg -y -i /tmp/yt_audio.m4a -ar 16000 -ac 1 /tmp/yt_audio.wav

# 3. Pollinations whisper API (model=whisper, language=tr)
curl -s -X POST "https://gen.pollinations.ai/v1/audio/transcriptions" \
  -H "Authorization: Bearer $POLLINATIONS_API_KEY" \
  -F "model=whisper" \
  -F "language=tr" \
  -F "file=@/tmp/yt_audio.wav"
```

Pollinations whisper endpoint: `POST /v1/audio/transcriptions`, model=`whisper`, multipart form (file + model + language).

**KRİTİK — Dosya boyutu limiti:** 56MB üzeri 524 timeout verir. **20MB'a kadar tek seferde güvenli** (09 Haz 2026 test: 19MB WAV, ~12dk ses, Pollinations Whisper çalıştı, tam transkript döndü). 20MB+ için `ffmpeg -f segment -segment_time 600 -ar 16000 -ac 1` ile parçalara böl, her birini ayrı gönder, sonuçları birleştir.

Performans: 10dk parça ~32sn işlem, ~7300 karakter. 12dk parça (19MB) ~5sn işlem.

Detaylı benchmark ve karşılaştırma: `references/transcription-methods.md`
Pollinations whisper API detayları (limitler, yetenekler): `references/pollinations-whisper-api.md`

### Method 3: Yerel faster-whisper small (Pollinations down/bakiye yetmezse)

Sadece Pollinations ulaşılamaz olduğunda, **bakiye yetmediğinde** (HTTP 402 PAYMENT_REQUIRED) veya çok küçük işler için. 1 CPU ARM64'te yavaş; x86_64'te daha hızlı (~0.5-0.7x realtime).

```bash
python3 -c "
from faster_whisper import WhisperModel
model = WhisperModel('small', device='cpu', compute_type='int8')
segments, _ = model.transcribe('/tmp/yt_audio.wav', language='tr', beam_size=5)
for s in segments:
    print(f'[{s.start:.1f}s-{s.end:.1f}s] {s.text}')
" 2>/tmp/whisper_stderr.log
```

**Performans (1 CPU ARM64):** ~1.1x realtime, 360MB RAM. 60dk video ~66dk işlem.
**Performans (x86_64, 4 çekirdek):** ~0.1-0.2x realtime (16:37 video ~2-3dk işlem, 31MB WAV). CPU-bound, çekirdek sayısı ve boost clock belirleyici.

**⚠️ Import timeout tuzağı:** `WhisperModel()` ilk import modeli RAM'e yüklediği için **15-30 saniye sürebilir**. terminal(timeout=...) bu süreyi aşarsa timeout hatası alırsın. Bunu önlemek için:
- terminal timeout'unu en az 120sn ayarla
- Output'u stderr heartbeat ile 2 aşamada al (model yüklenirken `print('[WHISPER] Loading...', file=sys.stderr)`)
- `2>/tmp/whisper_stderr.log` ile stderr'i ayrı dosyaya yönlendir
- timestamp'lerle output al (`[{seg.start:.1f}s-{seg.end:.1f}s]`)

**Ses dosyası formatı:** WAV 16kHz mono. Doğrudan uzun segmentleri işleyebilir (31MB WAV = ~16dk, sorunsuz). 20MB sınırı Pollinations içindir, faster-whisper için geçerli değil.

**⚠️ Whisper Türkçe transkripsiyon sınırlamaları (12 Tem 2026):**
- İngilizce özel isimler Türkçe mode'da yanlış çıkabilir: Claude→Cloud, J-Space→G-Space/Giz Bes, Searle→Seyrılin/Sirlin, Harnad→Harnat, Dennett→Denett
- Sebep: Whisper Türkçe modeli İngilizce proper noun'ları Türkçe fonetiğe zorlar. Sonrasında elle düzelt.

### Method 4: Browser + vision_analyze ile Caption Yakalama (NİHAİ SON ÇARE — 16 Tem 2026)

**Ne zaman kullanılır:** Auto-caption boş (PO token tuzağı), Whisper/ses transkripsiyonu mevcut değil (whisper kurulu değil, Pollinations API yok, bakiye yetersiz) ve video yine de izlenip raporlanması gerekiyorsa.

**Nasıl çalışır:**
1. Videoyu browser'da aç (`browser_navigate`)
2. JavaScript ile videoyu oynat (`browser_console` ile `document.querySelector('video').play()`)
3. Başa sar (`document.querySelector('video').currentTime = 0`)
4. Video oynarken belirli aralıklarla `browser_vision(question="Read ALL captions on the video right now")` ile caption'ları oku
5. Her karede gördüğün caption metnini birleştir

**⚠️ Önemli tuzaklar:**
- **Video süresini kontrol et:** YouTube Shorts bazen normal video olabilir. `document.querySelector('video')?.duration` ile süreyi kontrol et (60sn üstü = normal video)
- **Her karede farklı caption:** vision_analyze her seferinde o anki caption'ı gösterir. Aynı cümleleri tekrar görmemek için her screenshot'tan sonra `currentTime`'ı 5-10sn ileri sar
- **Yavaş yöntem:** 20-30sn'lik Short için ~5 screenshot yeterli olur. 130sn'lik video için 10-15 screenshot gerekebilir
- **Arka plana dikkat:** vision_analyze hem caption'ı hem video üzerindeki görsel metinleri okur. İkisini ayırt et

**Not:** Bu yöntem, otomatik transkripsiyon altyapısının olmadığı durumlarda son çaredir. Asla birincil yöntem olarak kullanma — video tamamen dinlenemez ama yine de içerik çıkarılması gereken durumlar için vardır.

## Output Formats

After fetching the transcript, format it based on what the user asks for. **NOTE:** Edel için varsayılan akış output formatı kullanmaz — bilgiyi wiki'ye kaydet + değerlendir. Output formatları sadece Edel açıkça "bunu şu formata çevir" derse kullan.

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow (Edel için — özet çıkarma, işle ve kaydet)

0. **ÖN TARAMA (web_extract ile):** Pipeline'a başlamadan önce `web_extract(urls=["https://www.youtube.com/watch?v=VIDEO_ID"])` ile hızlı bir ön bakış al. YouTube genellikle video başlığı, açıklama, bölüm listesi (chapters), izlenme/beğeni sayısı ve otomatik özet döndürür. Bu adım:
   - Videonun ne hakkında olduğunu anlamanı sağlar
   - Chapter listesi varsa yapısal framework'ü önceden görürsün
   - ~2 saniye sürer, pipeline'ı gereksiz yere başlatmamak için faydalıdır
   - **Dikkat:** web_extract özeti ASLA nihai içerik olarak kullanma — sadece yönlendirme içindir. Asıl transkript her zaman Method 1-2-3 ile alınır.

1. **ÖNCE auto-caption dene (Method 1):** yt-dlp ile `--write-auto-subs --sub-lang tr`. Saniyeler içinde.
2. **Auto-caption YOKSA veya overlapping SORUNLUYSA → Pollinations whisper (Method 2):** Sesi indir (format 140), 16kHz mono wav'a çevir, Pollinations API'ye gönder. Dakikalar içinde.
3. **Pollinations DOWN/bakiye yetmezse → yerel whisper (Method 3):** Son çare. x86_64'te 16dk video ~30-40sn. Her zaman çalışır.
4. **Cloud IP'deysen (Oracle/AWS/GCP):** Önce proxy'siz dene. Metadata (--dump-json) ve audio download (format 140) bazen proxy'siz çalışır (sadece JS runtime uyarısıyla). Proxy gerekirse tüm yt-dlp çağrılarında `--proxy socks5://127.0.0.1:1080` kullan.\n   **Lokal IP'deysen (Windows/WSL, ev bağlantısı):** Proxy'siz çalışır. yt-dlp doğrudan format 140 ve auto-caption alabilir. Android client fallback'e (player_client=android) gerek yoktur.
5. **Validate:** çıktı boş değil mi, doğru dil mi kontrol et. Auto-caption SRT'sinde 3x overlapping varsa (aynı cümle 3 kere tekrar ediyorsa) → metin hala okunabilir olduğu için devam et. Segmentasyon + pattern eşleştirme ile yapısal içerik çıkar (bkz. adım 7). Sadece tamamen okunamaz durumdaysa Method 2'ye geç.
6. **Chunk if needed:** transkript ~50K karakteri aşarsa parçala (~40K + 2K overlap).
7. **DERİN İÇERİK ÇIKARMA (KRİTİK — 16 Haz 2026):** Transkripti aldıktan sonra, yüzeysel özet geçip hemen uygulama fikrine atlama. Şunları yap:
   - **Yapısal framework'leri tespit et:** Video numbered list, step-by-step, framework veya kategori sunuyorsa her bir maddeyi ayrı ayrı çıkar.
   - **Konuşmacının kendi ağzından açıklamayı al:** Her madde için ne dediğini, hangi örneği/hikayeyi anlattığını aktar.
   - **Alıntıları çıkar:** Önemli cümleleri doğrudan alıntı olarak kaydet.
   - **Çıkarılan içeriği Edel'e sun:** "Videoda şunlar konuşulmuş" formatında detaylı döküm ver. ÖZET YAPMA — tüm içeriği ver.
   - **⚠️ SELF-CHECK — Az madde tuzağı (29 Haz 2026):** 5-10 dakikalık bir kısa videoda bile genelde 5+ ayrı konu/teknik/fikir olur. 20+ dk'lık bir videoda 5 madde çıkardıysan **yüzeysel kalmışsındır** — tekrar tara. Şu soruları kendine sor:
     * Videoda kaç tane numbered list, framework, kategori, adım var? Her birini ayrı satır yaptın mı?
     * Konuşmacının verdiği her örnek/hikaye/alıntıyı çıkardın mı?
     * Video süresi / toplam konu sayısı orantılı mı? (27dk video → 15-30+ konu normaldir)
     * Sadece "sistemimize uyarlanabilir" olana değil, tüm içeriğe baktın mı?
     - **Test:** Edel "sadece 5 tane mi fikir çıktı?" derse bu tuzağa düşmüşsündür.
     - **⚠️ Short süre tuzağı (16 Tem 2026):** YouTube bazen normal videoları Shorts olarak listeler (URL'de `/shorts/` prefix'i olmasına rağmen video süresi 60sn üstüdür). Her zaman `document.querySelector('video')?.duration` ile süreyi kontrol ET — 60sn üstü normal videodur, Method 1 veya 2 ile transkript alınabilir.
     - **⚠️ En kritik self-check — Tahmin tuzağı:** Şu soruları kendine sor:
          * Videoyu baştan sona izledin/dinledin mi, yoksa thumbnail/başlık/yorumlardan çıkarım mı yaptın?
          * **Short'sa bile tam süreyi kontrol ettin mi?** (YouTube bazen normal videoları Short olarak etiketler — `document.querySelector('video')?.duration` ile kontrol et. 60sn üstü = normal video.)
          * "Büyük ihtimalle şu", "muhtemelen bu" gibi ifadeler kullandıysan — DUR ve gerçek içeriği tüket.
          * Raporunda "şunla ilgili olabilir" tarzı belirsizlik var mı? Varsa henüz işi bitirmemişsindir.
          * **Standart transkripsiyon yöntemleri çalışmadıysa ne yaptın?** Sadece "olmuyor" deyip bırakma — Method 4'ü (browser + vision_analyze) dene.
   - **SRT 3x tekrar sorunu:** YouTube auto-caption her cümleyi 3 kere tekrarlasa bile metin hala okunabilir. Segmentasyon ve pattern eşleştirme ile yapısal içerik çıkarılabilir. Sadece tamamen okunamaz durumdaysa Method 2'ye geç.

8. **ÖNCE ÖĞRENME, SONRA UYGULAMA (Edel kuralı — 16 Haz 2026):** İçeriği Edel'e sunduktan sonra, önce onun öğrenmesine fırsat ver. Şunlara DİKKAT ET:
   - "Bunu şuraya uyarlayalım", "şu içerik serisine çevirelim" gibi uygulama fikirlerine hemen atlama.
   - Edel bilgiyi öğrenmeden önce içerik üretimi önermek geri teper: "Bu bilgileri ben öğrenmedikten sonra niye böyle bir şey yapayım?"
   - İçeriği sunduktan sonra Edel'in tepkisini bekle. O "bunu nasıl kullanırız?" derse uygulama fikirlerine geç.
   - Sorulabilecek iyi sorular: "Bu maddelerden hangisi senin için en ilginç?", "Bunu daha önce biliyor muydun?", "Bu konuda ne düşünüyorsun?"

9. **ÇİFT KAYIT (Edel onaylı — 09 Haz 2026):**
   - **A — NotebookLM:** YouTube URL'sini NotebookLM'e kaynak olarak ekle. **İKİ YÖNTEM (sırayla dene):**
     **Yöntem 1 (Önce dene) — URL source:** `mcp_notebooklm_mcp_source_add` ile `type="url"`. NotebookLM kendi transcript'ini çeker.
     **Yöntem 2 (Fallback) — Text source:** URL ekleme başarısız olursa (`"Could not add url source"`), temiz transkript metnini `source_type="text"` ile text source olarak ekle. Başlığa video adını + kanalı koy, giriş cümlesi ekle, ardından transkript metnini ver. Text source her zaman çalışır.
     **⚠️ Notebook ID formatı:** `notebook_list`'ten gelen ID'ler full UUID'dir (`e263e756-c97f-...`). `notebook_get` gibi bazı işlemler short ID ile çalışmaz — **full UUID kullan.**
     **Hangi notebook:**
     - AI/tool/coding → `🛠️ Tech Tools Updates` (id: e263e756-c97f-440a-9f14-dd461ae894eb)
     - Hermes Agent → `Hermes Docs` (id: 194c049a-215c-42bd-a2c3-7dae0169aa95)
     - Psikoloji/akademik → `APA Bilgi` (id: c44469fe-a69a-4a86-8dd8-756c2f365109)
     - Diğer → `notebook_list` ile tara, uygun olanı seç veya yenisini oluştur
   - **B — Wiki:** Temiz transkripti `~/wiki/concepts/` veya uygun klasöre kaydet. Detaylar, benchmark verileri, önemli alıntılar dahil olsun.
   - **Neden ikisi birden:** NotebookLM (A) podcast/quiz için, Wiki (B) kalıcı bilgi tabanı için. İkisi farklı amaçlara hizmet eder, birbirini tamamlar.
10. **Değerlendir:** Edel ile içeriği konuş — ne anladın, nereleri ilginç buldun, hangi kısımlar tartışmaya değer.

11. **Uygulama fikri yürüt (SADECE Edel isterse):** Bu bilgi bizim için ne ifade ediyor? Nasıl kullanabiliriz? Denemeye değer mi?

12. **ÖZET ÇIKARMA.** Bilgiyi işle, kaydet, değerlendir. Bilgi zaten videonun kendisinde var.

## Error Handling

### Known Failure Modes (Sıralı kontrol et)

**1. IP blocked (TCP/HTTP 403)**
- **Belirti:** yt-dlp timeout, curl connection refused, HTTP 403
- **Neden:** Oracle/AWS/GCP IP aralıkları YouTube tarafından bloklanır
- **Çözüm:** WARP SOCKS5 proxy (`--proxy socks5://127.0.0.1:1080`). Load `warp-proxy` skill for setup.

**2. PO Token / Bot Detection (SESSİZ BAŞARISIZLIK)** ⚠️
- **Belirti:** yt-dlp auto-caption indirir, SRT dosyası oluşur AMA içi boştur veya yalnızca 1 satır `WEBVTT` header'ı vardır. WARP bağlıdır (timeout/403 yok), video bilgisi gelir, transcript boş döner.
- **Neden:** Google / YouTube, Cloudflare WARP IP aralıklarını (104.28.x.x) bot trafiği olarak sınıflandırır. YouTube'un innertube API'si PO (Proof of Origin) token kontrolü yapar — token yoksa transcript boş/hatalı döner, ama TCP bağlantısı ve video meta verileri normal görünür. Bu "sessiz başarısızlık"tır — hata mesajı yok, sadece boş çıktı vardır.
- **Ayırt etme:** `ls -la /tmp/transcript_*.srt` yap, dosya boyutuna bak. 0-100 byte ise → PO token tuzağı. yt-dlp JSON'da `automatic_captions` anahtarı dolu ama içerik boş.
- **Çözüm 1 (Hemen):** Method 2'ye (Pollinations Whisper) geç. Ses indir → transkripte et. PO token bypass gerekmez — Whisper doğrudan sesten okur.
- **Çözüm 2 (Kesin):** Playwright CDP ile headless Chrome'dan YouTube sayfasını aç. captureStream veya CDP üzerinden transcript DOM'unu parse et. Gerçek browser Google'a gerçek kullanıcı gibi görünür, PO token gerektirmez.
- **Çözüm 3 (İleri düzey):** yt-dlp + browser'dan export edilmiş cookies.txt + PO token injection. Ama PO token'ın TTL'si kısadır, sürekli refresh gerekir. Sadece otomatize cron job için uğraşmaya değer.
- **ÖNEMLİ:** PO token sorunu yaşarken SRT'yi düzeltmeye çalışma, video formatını değiştirme, proxy rotasyonu dene — hepsi zaman kaybı. Kök neden PO token'dır, IP veya format değil. Doğrudan Method 2 veya Playwright'a geç.

- **YANILGI — ytInitialPlayerResponse timedtext URL (12 Tem 2026):**
  Browser'ın `ytInitialPlayerResponse.captions.playerCaptionsTracklistRenderer.captionTracks[0].baseUrl` değerinden aldığın timedtext API URL'si dışarıdan çağrıldığında HTTP 200 döner AMA gövde boştur. Bunun sebebi URL'deki signature parametresinin browser session'ına bağlı olmasıdır (IP binding + imzalı URL). Bu bir **"false hope"** tuzağıdır — URL var, caption var, ama dışarıdan erişilemez.
  - **Ayırt etme:** `curl -sI "<URL>"` → HTTP 200 + `Content-Length: 0`. Dosyaya yazıp oku, 0 byte.
  - **Çözüm:** Vakit kaybetme, doğrudan Method 2 veya 3'e geç. Browser içinden async fetch de çalışmaz (CORS / signature binding). Sadece browser'ın kendi sayfasından yapılan istekler geçerlidir.
  - **Ne işe yarar:** Bu URL'den `format=sbv` veya `format=json3` parametreleriyle farklı format dene — hepsi aynı sonucu verir (boş). Bu tuzağa düşme.

**3. Auto-caption yok veya overlapping bozuk**
- **Belirti:** yt-dlp `--write-auto-subs` başarılı ama SRT içinde her cümle 3 kere tekrarlanıyor
- **Neden:** YouTube'un overlapping segment formatı
- **Çözüm 1 (Önce dene):** Metin hala okunabilir. Python segmentasyon + pattern eşleştirme ile yapısal içerik çıkarılabilir (numbered list'ler, framework'ler). Sadece tamamen okunamaz durumdaysa Çözüm 2'ye geç.
- **Çözüm 2:** Method 2'ye (Pollinations whisper) geç. SRT'yi düzeltmeye çalışma.
- **Ayırt etme:** Çıktıda aynı cümleler 3'er 3'er tekrarlanıyorsa → overlapping. clean_srt.py sadece zaman damgasını temizler, 3x dedup YAPMAZ.

**4. Pollinations whisper down / bakiye yetmez**
- **Belirti:** Pollinations API 500/503/timeout **veya** HTTP 402 `"PAYMENT_REQUIRED"` / `"Insufficient balance"`
- **Neden (402):** Pollinations hesabında yeterli pollen yok. Her Whisper isteği ~0.0020 pollen tüketir.
- **Çözüm:** Method 3'e geç (yerel faster-whisper small). x86_64'te 16dk video ~30-40sn işlem sürer, Pollinations'tan çok yavaş değildir.

**5. NotebookLM YouTube URL source ekleme hatası (YENİ — 29 Haz 2026)**
- **Belirti:** `mcp_notebooklm_mcp_source_add(type="url")` çağrısı `"Could not add url source"` döndürür. Auth status "configured" görünür, diğer notebook işlemleri çalışır.
- **Neden:** YouTube URL'leri NotebookLM'in MCP client'ı üzerinden her zaman eklenemez. Sebep genellikle sunucu tarafında (Google altyapısı), client'ta değil. Retry genelde işe yaramaz.
- **Çözüm (Fallback):** Transkripti `source_type="text"` ile text source olarak ekle:
  ```
  mcp_notebooklm_mcp_add_source(type="text", notebook_id="FULL_UUID",
    title="Video Adı - Kanal Adı (transkript)",
    content="Video: ...\nTRANSCRIPT:\ntemiz_transkript_metni")
  ```
  Text source ekleme URL source'tan farklı bir endpoint kullanır ve her zaman çalışır. NotebookLM yine de transkripti işler, podcast/quiz üretebilir.
- **Not:** Önce yine de URL source'u dene — çalıştığı zaman NotebookLM kendi daha temiz transcript'ini çeker. Sadece başarısız olursa fallback'e geç.
- **Alternatif:** Yeni bir notebook oluşturup o notebook'a text source eklemeyi dene (mevcut notebook bozuk olabilir).

**6. NotebookLM auth desync — nb_keepalive OK ama MCP authenticated=false (YENİ — 5 Tem 2026)**
- **Belirti:** `nb_keepalive.py` "CDP login OK" döndürür, `get_health` ise `authenticated: false` raporlar. `total_notebooks` beklenenden az olabilir (örn. 1 yerine 37+).
- **Neden:** nb_keepalive Chrome CDP üzerinden cookie enjekte eder, MCP server ise kendi Chrome profili üzerinden auth kontrolü yapar. İkisi arasında cookie/Chrome-profile senkronizasyonu kopmuş olabilir. MCP server farklı bir Chrome profili veya data dizini kullanıyor olabilir.
- **Çözüm 1 (Önce dene — skip):** YouTube transkripti başarıyla alındıysa ve sadece NotebookLM kaydı kaldıysa, NotebookLM'i tamamen atla ve sadece wiki kaydıyla yetin. Kullanıcı özellikle sormadıkça auth sorununu debug etmek için dakikalar harcama.
- **Çözüm 2 (Soft reset):** MCP server'ı yeniden başlat. Bu, nb_keepalive'ın yazdığı cookie'leri yeniden okumasını sağlar.
- **Çözüm 3 (Clean slate):** `cleanup_data(confirm=true, preserve_library=true)` ile browser profilini temizle, ardından `setup_auth` çalıştır.
- **Çözüm 4 (Hard reset):** `re_auth` ile komple yeniden Google login yap. Öncesinde `cleanup_data(confirm=true, preserve_library=true)` önerilir.
