---
name: notebooklm-studio
description: "NotebookLM Studio ile otomatik çalışma materyali üretimi — Briefing Doc, Audio Overview, Quiz, Flashcards, Slide Deck, Mind Map, Infographic. Kaynak seçimi, artifact oluşturma ve Duolingo-tarzı kolay çalışma planları."
category: media
tags:
  - notebooklm
  - studio
  - study-guide
  - quiz
  - flashcard
  - audio-overview
  - video-overview
  - infographic
  - slide-deck
  - mind-map
  - briefing-doc
  - keepalive
  - watermark
  - duolingo-style
  - automated-study
  - karusel-pipeline
  - instagram-carousel
  - slide-deck-pipeline
triggers:
  - kolay çalışma
  - duolingo gibi
  - 10 dakikalık ders
  - çalışma planı kolaylaştır
  - notebooklm studio
  - briefing doc oluştur
  - infographic oluştur
  - mind map oluştur
  - slide deck oluştur
  - nlm studio
  - çalışma materyali üret
  - otomatik çalışma
  - hiçbir şey yapmadan çalış
  - pasif çalışma
  - dinleyerek çalış
  - quiz oluştur
  - flashcard oluştur
  - audio overview çalışma
  - sınav tekrar planı
  - günlük çalışma programı
  - video overview
  - video sunum
  - sesli slayt
  - filigran kaldır
  - keepalive
  - notebooklm bakım
  - sınav tekrar planı
  - günlük çalışma programı
  - karusel görsel
  - instagram karusel
  - karusel pipeline
  - slide deck karusel
---

# NotebookLM Studio — Otomatik Çalışma Materyali Üretimi

Bu skill, mevcut NotebookLM notebook'larındaki kaynakları kullanarak Studio aracılığıyla otomatik çalışma materyali üretmeyi ve Duolingo-tarzı kolay çalışma planları tasarlamayı kapsar.

**Temel felsefe:** Kullanıcı sadece tüketir, AI tüm üretimi yapar. Hiçbir şey yazmak/okumak/üretmek zorunda değildir.

---

## 1. Kullanılabilir Studio Artifact Türleri

| Tür | Komut | En İyi Kullanım | Süre |
|-----|-------|-----------------|------|
| **Briefing Doc** | `nlm report create <notebook_id> -f "Briefing Doc"` | Yeni konuya ilk giriş | 5 dk okuma |
| **Study Guide** | `nlm report create <notebook_id> -f "Study Guide"` | Soru-cevap formatında çalışma | 5-10 dk |
| **Audio Overview** | `nlm audio create <notebook_id> -f brief -l short -s \"id1,id2\" -y` | Pasif dinleme, yürüyüş/araç | 10 dk |
| **Video Overview** | `nlm video create <notebook_id> --format explainer --style whiteboard --language tr -y` | Görsel+sesli anlatım | 2-10 dk |
| **Quiz** | `nlm quiz create <notebook_id> -c 5 -d 3 --focus \"konu\" -y` | Kendini test etme | 5-10 dk |
| **Flashcards** | `nlm flashcards create <notebook_id> -d medium --focus \"konu\" -y` | Ezber ve aktif hatırlama | 5-10 dk |
| **Slide Deck** | `nlm slides create <notebook_id> -f presenter_slides -l short --focus \"konu\" -y` | Görsel tekrar/sunum | 5 dk |
| **Mind Map** | `nlm mindmap create <notebook_id> --focus \"konu\" -y` | Kavram ilişkileri | 5 dk |
| **Infographic** | `nlm infographic create <notebook_id> -o portrait -d concise --focus \"konu\" -y` | Görsel özet | 5 dk |

---

## 2. Kullanım Adımları

### 2.1 Notebook'u Belirle

```bash
nlm notebook list
```

İlgili konuyu kapsayan bir notebook seç. Kaynak sayısı yüksek olanlar (50+) daha kapsamlı sonuç verir.

### 2.2 Kaynakları Seç

```bash
# Notebook kaynaklarını listele
nlm source list <notebook_id>

# İlgili kaynakların tam ID'lerini al
nlm source list <notebook_id> | python3 -c "
import json, sys
data = json.load(sys.stdin)
for s in data:
    if 'anahtar_kelime' in s.get('title','').lower():
        print(f'{s[\"id\"]} | {s.get(\"title\",\"\")}')
"
```

**Kaynak seçimi stratejisi:**
- **Dar odak (tek konu):** 1-3 spesifik kaynak (örn: sadece DSM-5 ilgili bölümü)
- **Geniş kapsam (konu paketi):** 3-5 kaynak (DSM + vaka örnekleri + konu anlatımı)
- **Karma (tekrar/test):** 5-8 kaynak (tüm ilgili materyaller)

### 2.3 Artifact Oluştur

> ⚠️ **CLI Syntax:** Doğru kullanım `nlm <tür> create` şeklindedir. `nlm create <tür>` ÇALIŞMAZ.

**Briefing Doc / Study Guide:**
```bash
nlm report create <notebook_id> \
  -f "Briefing Doc" \
  -s "id1,id2,id3" \
  -y
```

**Audio Overview:**
```bash
nlm audio create <notebook_id> \
  -f brief \
  -l short \
  --language "tr" \
  -s "id1,id2" \
  -y
```

| Parametre | Değerler | Varsayılan |
|---|---|---|
| `-f` / `--format` | `deep_dive`, `brief`, `critique`, `debate` | `deep_dive` |
| `-l` / `--length` | `short`, `default`, `long` | `default` |
| `--language` | BCP-47 kodu (`tr`, `en`, `de`, `fr`, `es`, `ja`) | NotebookLM varsayılanı |

**Video Overview:**
```bash
nlm video create <notebook_id> \
  --format "explainer" \
  --style "whiteboard" \
  --language "tr" \
  -y
```

| Parametre | Değerler | Varsayılan |
|---|---|---|
| `--format` | `explainer`, `brief`, `cinematic` | `explainer` |
| `--style` | `auto_select`, `custom`, `classic`, `whiteboard`, `kawaii`, `anime`, `watercolor`, `retro_print`, `heritage`, `paper_craft` | `auto_select` |
| `--language` | BCP-47 kodu | NotebookLM varsayılanı |
| `--style-prompt` | Özel stil açıklaması (implies `--style custom`) | — |

**Quiz:**
```bash
nlm quiz create <notebook_id> \
  -c 5 \
  -d 2 \
  --focus "konu adı" \
  -s "id1,id2" \
  -y
```

**Flashcards:**
```bash
nlm flashcards create <notebook_id> \
  -d "medium" \
  --focus "konu adı" \
  -s "id1,id2" \
  -y
```

**Slide Deck:**
```bash
nlm slides create <notebook_id> \
  -f "presenter_slides" \
  -l "short" \
  --focus "konu adı" \
  -y
```

**Infographic:**
```bash
nlm infographic create <notebook_id> \
  -o "portrait" \
  -d "concise" \
  --focus "konu adı" \
  -y
```

### 2.4 Durumu Kontrol Et

```bash
nlm studio status <notebook_id>
```

### 2.5 Artifact'i İndir

⚠️ `nlm download` bir **COMMAND GROUP**'tur. Doğru syntax: `nlm download <type> <notebook_id> --id <artifact_id> --output <path>`

```bash
nlm download report <notebook_id> --id <artifact_id> -o /tmp/output.md
nlm download audio <notebook_id> --id <artifact_id> -o /tmp/audio.m4a
nlm download video <notebook_id> --id <artifact_id> -o /tmp/video.mp4
nlm download slide-deck <notebook_id> --id <artifact_id> -o /tmp/slides.pdf
nlm download quiz <notebook_id> --id <artifact_id> -o /tmp/quiz.md
nlm download flashcards <notebook_id> --id <artifact_id> -o /tmp/cards.md
nlm download infographic <notebook_id> --id <artifact_id> -o /tmp/chart.png
```

YANLIŞ:
```
nlm download <artifact_id>              # ❌
nlm download audio <artifact_id>        # ❌ (notebook_id gerekli)
```

### 2.6 Instagram Karusel Pipeline

Bu pipeline, NotebookLM Studio slide_deck'ini kullanarak Instagram karusel (carousel) görselleri üretir.

**Tam akış:**
```
📝 Karusel metni (slayt içerikleri hazır)
   ↓
📁 Yeni notebook oluştur → metni pasted_text olarak ekle
   ↓
📊 NotebookLM Studio → Slide Deck (presenter_slides)
   ↓
📄 PDF indir → PyMuPDF ile PNG'ye dönüştür
   ↓
☁️ Catbox/0x0.st → Görsel URL'leri
   ↓
🤖 Instagram Graph API → Karusel Container
   ↓
🔥 Onay bekle → Publish
```

**Adım adım:**

```bash
# 1. Karusel metni için yeni notebook oluştur
nlm notebook create "Karusel: <Konu Başlığı> (<tarih>)"

# 2. Karusel metnini pasted_text olarak ekle (slayt içerikleriyle birlikte)
nlm source add <notebook_id> --text "$(cat ~/instagram_karusel/<klasor>/karusel_metni.md)" --title "<Konu> - Karusel Metni" -w

# 3. Slide deck oluştur — presentasyon formatında
nlm slides create <notebook_id> \
  -f "presenter_slides" \
  -l "short" \
  --focus "<konu, slayt sayısı, Instagram karusel formatı>" \
  -y

# 4. Durumu kontrol et
nlm studio status <notebook_id>

# 5. Tamamlanınca PDF'yi indir
nlm download slide-deck <notebook_id> \
  --id <artifact_id> \
  -o /tmp/karusel_konu.pdf

# 6. PDF → PNG (PyMuPDF ile her sayfa ayrı PNG)
python3 << 'EOF'
import fitz, os, pathlib
pdf = fitz.open("/tmp/karusel_konu.pdf")
out_dir = pathlib.Path("<output_klasörü>")
out_dir.mkdir(parents=True, exist_ok=True)
for i, page in enumerate(pdf):
    pix = page.get_pixmap(dpi=200)
    pix.save(str(out_dir / f"{i+1:02d}_{i}.png"))
pdf.close()
print(f"{len(pdf)} slayt PNG'ye dönüştürüldü")
EOF
```

**Notlar:**
- Slayt içeriklerinin metne sadık kalması için **karusel metnini notebook'a kaynak olarak ekle** — mevcut notebook'lardaki kaynaklar farklı içerik üretebilir
- `--focus` parametresine slayt sayısı ve renk tercihlerini de ekle (örn: "9 slayt, pastel renkler, Türkçe, Instagram karusel")
- Çıktı klasörü: `~/instagram_karusel/<tarih>_<konu>/`
- PNG çözünürlüğü: 200 DPI Instagram için yeterli

**Arşiv takibi:**
Her karusel `~/.hermes/data/karusel_arsiv.json` dosyasına kaydedilir:
```json
{
  "id": "<tarih_konu>",
  "tarih": "2026-07-01",
  "konu": "<başlık>",
  "slayt_sayisi": 9,
  "klasor": "~/instagram_karusel/<klasör>",
  "status": "draft_metin_hazir|notebooklm_slide_deck_hazir|pending_approval|posted",
  "gorseller_hazir": false,
  "onay": false
}
```

**Doğrulanmış çalışma (10 Tem 2026):** "Belirsizlik Çağı ve Kaygı" karuseli (9 slayt) jacob-bd MCP ile başarıyla oluşturuldu. Slide deck oluşturma ~4 dk, PDF indirme ~2sn, PDF→PNG dönüşümü ~3sn sürdü. Tüm adımlar `nlm` CLI ile çalıştı.

**Otomasyon ipucu:** Uzun süren slide_deck oluşturma için cron tetikleyici kullan (bkz. Async Monitoring) — elle poll yapma, kullanıcı "sürekli çıktı yapma" der.

---

## 3. Duolingo-Tarzı Çalışma Planı Tasarlama

### 3.1 İlkeler

1. **10 dakika max** — her ders süresi, kullanıcının dikkat sınırı
2. **Sıfır üretim** — kullanıcı yazmaz, analiz etmez, sadece tüketir
3. **Format rotasyonu** — her gün farklı artifact türü (monotonluk kırmak için)
4. **Tek tık erişim** — bildirim → linke tıkla → 10 dk → bitti
5. **Mevcut kaynakları kullan** — sıfırdan yükleme yapma, zengin notebook'ları değerlendir

### 3.2 Plan Şablonu (10 Gün × 2 Oturum)

**İleri seviye:** Her gün 2 oturum (öğlen + akşam) ile konuyu hem işle hem pekiştir.

| Gün | Öğlen (12:00) | Akşam (18:00) |
|:----|:--------------|:--------------|
| 1 | Briefing Doc (yeni konu) | Quiz (5 soru) |
| 2 | Flashcards (vaka) | Infographic (özet) |
| 3 | Audio Overview (dinle) | Quiz (vaka) |
| 4 | Briefing Doc (ayırıcı tanı) | Quiz (karma) |
| 5 | Mind Map (karşılaştırma) | Quiz (10 soru) |
| 6 | Slide Deck (model) | Flashcards (kavram) |
| 7 | Audio Overview (formülasyon) | Quiz (vaka) |
| 8 | Briefing Doc (yeni blok) | Flashcards (semptom) |
| 9 | Infographic (şiddet) | Quiz (vaka) |
| 10 | Audio Overview (genel tekrar) | Full Karma Quiz (20 soru) |

**Format rotasyonu prensibi:** Aynı format arka arkaya gelmez. Her gün farklı bir türle çalışmak monotonluğu kırar.

### 3.3 Google Calendar Entegrasyonu

Çalışma planını takvime işlemek için doğrudan Python API kullan:

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = '/home/ubuntu/.hermes/google_token.json'
creds = Credentials.from_authorized_user_file(
    TOKEN, ['https://www.googleapis.com/auth/calendar'])
service = build('calendar', 'v3', credentials=creds)

event = {
    'summary': '📖 YAB: DSM-5 Tanı Kriterleri',
    'description': 'Briefing Doc ile çalış. 10 dk.',
    'start': {'dateTime': '2026-07-02T12:00:00+03:00', 'timeZone': 'Europe/Istanbul'},
    'end': {'dateTime': '2026-07-02T12:10:00+03:00', 'timeZone': 'Europe/Istanbul'},
    'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'popup', 'minutes': 120},
            {'method': 'popup', 'minutes': 30}
        ]
    }
}
result = service.events().insert(calendarId='primary', body=event).execute()
```

**Önemli:** Token dosyası bazen root sahipliğinde olabilir. Alternatif yol: `google_token_ubuntu.json` varsa onu kullan veya kopyala:
```bash
cp /home/ubuntu/.hermes/google_token_ubuntu.json /home/ubuntu/.hermes/google_token.json
```

### 3.4 Teslimat Akışı

En iyi yöntem: **Her günün artifact'ini bir önceki gece cron ile oluştur, sabah bildirimle gönder.**

Veya:
1. Tüm artifact'leri önceden oluştur
2. Her gün bir tanesini bildirimle teslim et
3. Kullanıcı sadece tıklar ve tüketir

---

## 4. Pitfall'lar ve İpuçları

### ❌ Source ID truncation
`nlm source list` çıktısındaki ID'ler 8 karakter gösterir. Tam ID'yi almak için Python ile full JSON çek:
```bash
nlm source list <notebook_id> | python3 -c "
import json, sys
data = json.load(sys.stdin)
for s in data:
    print(s['id'], '|', s.get('title',''))
"
```

### ❌ `--focus` parametresi tüm türlerde çalışmaz
- **Çalışır:** `nlm audio create`, `nlm quiz create`, `nlm flashcards create`, `nlm slides create`, `nlm infographic create`
- **Çalışmaz:** `nlm report create` (Briefing Doc/Study Guide)
- **Çözüm:** Report için source ID'leri özenle seçerek içeriği yönlendir

### ❌ Dil desteği
Audio Overview: `en, es, fr, de, ja`. Diğer dillerde parametre verme — varsayılanı kullan.

### ❌ Generation süresi (slide_deck çok yavaş olabilir)
Büyük kaynaklarda 10-60 saniye arası. Yeni notebook + pasted_text kaynakla slide_deck oluşturma **3+ dakika** sürebilir. Kullanıcı bekletilmemeli:
- Cron tetikleyici kur (bkz. Async Monitoring)
- Kullanıcıya "slide deck oluşuyor, tamamlanınca haber veririm" de

### ❌ Download failed for slide_deck
Eski artifact'ler (birkaç gün önce oluşturulmuş olanlar) `nlm download slide-deck` ile "Download failed" hatası verebilir. Bu NotebookLM tarafındaki bir kısıtlama — artifact silinmiş veya erişilemez olmuştur. Çözüm: Yeni bir slide deck oluştur.

### ❌ Watermark kaldırma çabası — önerilmez
Slide deck PDF'lerinde NotebookLM watermark'ı vardır. Bunu kaldırmaya çalışmak verimli değildir:
- **Crop**: Görsel kompozisyonunu bozar
- **Inpainting**: Büyük alanlarda bulanıklık yapar
- **Clone stamp**: Source bölge de watermark içerebilir
- **Column-by-column sampling**: İnce çizgili (stripe) artifact bırakır
- **Seamless cloning**: Source içeriğini taşır
**Tavsiye:** Watermark'ı kaldırmaya çalışma. NotebookLM'in kendi branding'i olarak kabul et.

### ✅ En iyi kaynak kombinasyonu
**Hedef konu kaynağı** + **DSM-5/Tanı kitabı** + **Vaka örnekleri** = en kapsamlı sonuç. Sadece tek kaynak seçmek dar içerik üretir.

### ❌ Audio rate limit (RESOURCE_EXHAUSTED)
Audio Overview oluşturma hızla rate limit'e takılır. Bir oturumda **maksimum 2-3 audio** oluşturulabilir. Sonrasında 5+ dakika beklemek gerekir.
- **Çözüm:** Önce diğer artifact türlerini (report, quiz, flashcards) oluştur, audioları en sona bırak
- **Ya da:** Önceden oluşturulmuş mevcut audio artifact'lerini kullan (nlm studio status ile kontrol et)
- **Alternatif:** Audio Overview yerine Briefing Doc + Quiz kombinasyonu kullan

### ❌ Source türü uyumsuzluğu (INVALID_ARGUMENT)
Bazı artifact türleri belirli source türleriyle çalışmaz:
- **Flashcards:** `word_doc`, `uploaded_file` türü kaynaklarla INVALID_ARGUMENT hatası verir. Sadece `pdf` ve `pasted_text` türleriyle çalışır.
- **Audio:** `word_doc` kaynaklar bazen INVALID_ARGUMENT'a sebep olur. PDF ve transcript kaynakları daha güvenilir.
- **Genel kural:** PDF ve `pasted_text` türleri tüm artifact türleriyle uyumludur.

### ❌ Büyük kaynak domine etme
DSM-5 gibi çok büyük bir kaynak seçildiğinde, Studio çıktısı o kaynağın genel içeriğine odaklanır ve hedef konuyu ıskalayabilir.
- **Çözüm:** Büyük kaynağı tek başına kullanma — hedef konuya spesifik kaynaklarla birlikte kullan
- Büyük kaynak + spesifik kaynak(lar) = dengeli sonuç

### ❌ Rate limit: artifact oluşturma hızı
Art arda hızlı artifact oluşturma rate limit'e (RESOURCE_EXHAUSTED) takılabilir.
- **Çözüm:** Her artifact arasında 10-15 saniye bekle
- Batch oluşturma: 3-4 artifact → 15-20sn bekle → 3-4 artifact daha
- En hızlı: quiz, flashcards (~5sn)
- En yavaş: audio, slide deck, video (~20-60sn)

### ❌ Audio rate limit kalıcı olabilir
Aynı oturumda 3+ audio denemesi rate limit'in 5+ dakika boyunca devam etmesine yol açar.
- **Çözüm:** Kullanıcıya audio sunmak yerine mevcut audio artifact'lerini kullan
- `nlm studio status <notebook>` ile mevcut completed audioları listele
- En uygun olanı seç ve indir: `nlm download audio <notebook_id> --id <artifact_id> -o /tmp/audio.m4a`
### ❌ Auth expiry: `nlm studio status` hata verirse

`nlm studio status` komutu "Could not retrieve studio status" veya boş JSON döndürürse **auth expire olmuş olabilir**. Hemen keepalive çalıştır:

```bash
# Yöntem 1: Keepalive script (CDP)
python3 ~/.hermes/scripts/nb_keepalive.py

# Yöntem 2: nlm CLI ile CDP üzerinden auth yenile (keepalive Chrome kullanır)
nlm login --cdp-url http://127.0.0.1:18800

# Yöntem 3: nlm CLI ile manuel login (tarayıcı açar)
nlm login
```

Auth yenilendikten sonra status kontrolü tekrar dene.

### ❌ Server 502 hatası (slide_deck oluşturma)
Slide deck oluştururken "Server error 502" alınırsa CLI otomatik retry yapar (genelde 1. denemede düzelir). Manuel müdahale gerekmez.

### ❌ word_doc source'ları için özel durum
NotebookLM'e Google Docs/Word dosyası olarak yüklenen kaynaklar (`word_doc` türü):
- Studio'da quiz/flashcards oluştururken INVALID_ARGUMENT döndürebilir
- Çözüm: Bu kaynakları `--source-ids` ile seçme, onun yerine PDF versiyonlarını kullan

---

## 5. POST-PROCESSING & BAKIM

### NotebookLM Filigranı Kaldırma (Slide Deck)

Slide deck PDF'lerinde NotebookLM watermark'ı vardır. Bunu programatik olarak kaldırmak önerilmez — denenmiş tüm yöntemler bir şekilde görsel kaliteyi bozuyor. Detaylı analiz: `references/notebooklm-watermark-removal.md`

**Tavsiye:** Watermark'ı kaldırmaya çalışma. NotebookLM'in kendi branding'i olarak kabul et.

### NotebookLM Filigranı Kaldırma (Video)

Video overview'larda sağ alt köşede NotebookLM filigranı olur. En temiz yöntem crop:

```bash
# 1280x720 video için: sağdan 150px, alttan 40px kırp
ffmpeg -i input.mp4 -vf "crop=iw-150:ih-40:0:0" -c:v libx264 -crf 28 -preset fast -c:a copy output.mp4
```

Siyah bant kapatma önerilmez — görüntü bütünlüğünü bozar.

### Video Boyut Küçültme (Telegram İçin)

Telegram video limiti ~50MB. Aşan videolar için:

```bash
ffmpeg -i input.mp4 -vcodec libx264 -crf 28 -preset fast -acodec aac -b:a 64k output-compressed.mp4
```

### Auth Keepalive

NotebookLM auth ~20dk içinde expire olabilir. Keepalive cron her saat başı çalışır:

- Cron: `nb_keepalive_2h` (job ID), schedule: `0 * * * *`
- Script: `~/.hermes/scripts/nb_keepalive.py` (CDP + BWS ile auto-login)

Manuel auth yenileme:
```bash
python3 ~/.hermes/scripts/nb_keepalive.py
```

### Async Monitoring (Cron Tabanlı)

Uzun süren Studio generation'ları için **tek seferlik cron tetikleyicisi** — poll döngüsü kurma:

```bash
cronjob action=create schedule="5m" repeat=1 \
  prompt="nlm studio status <notebook_id> ile kontrol et, completed ise indir ve MEDIA: ile gönder"
```

### MEDIA Teslimatı

MEDIA tag'i normal response içinde çalışır. `send_message` ile "origin" kullanma — çalışmaz.

---

## 6. İlgili Skill'ler

- `notebooklm-mcp` — **PRIMARY**: jacob-bd/notebooklm-mcp-cli (39 tool, tüm Studio desteği). CLI: `nlm`, MCP: `notebooklm-mcp`
- `notebooklm-pipeline` — NotebookLM auth, kaynak yükleme, transkript → audio pipeline
- `cdp-notebooklm` — **FALLBACK**: CDP tabanlı NotebookLM client (sadece yeni MCP çalışmadığında kullan)
