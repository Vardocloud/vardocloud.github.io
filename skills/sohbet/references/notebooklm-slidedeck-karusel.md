# NotebookLM Slide Deck Üretimi (Karusel Görselleştirme)

## Özet
Instagram karusel içeriğini NotebookLM slide_deck artifact'i ile PDF olarak görselleştirme.
BDT notebook'u (a4fe729d) shared_with_me olmasına rağmen studio_create slide_deck ÇALIŞIYOR.
APA Bilgi notebook'u (c44469fe) da çalışıyor.

## Workflow
```bash
# 1. Slide deck oluştur (MCP)
mcp_notebooklm_mcp_studio_create(
    notebook_id="c44469fe-...",
    artifact_type="slide_deck",
    slide_format="detailed_deck",
    detail_level="standard",
    language="tr",
    focus_prompt="...8 slayt, pastel renkler, Türkçe...",
    confirm=True
)

# 2. BekleME — cron tetikleyici kur, 10 dk sonra kontrol et
cronjob(action='create', schedule='10m', name='slide_deck_kontrol', repeat=1,
    prompt='studio_status kontrol et, hazırsa download et...',
    deliver='origin')

# 3. Download (MCP)
mcp_notebooklm_mcp_download_artifact(
    notebook_id="...",
    artifact_type="slide_deck",
    artifact_id="...",
    output_path="/tmp/karusel.pdf",
    slide_deck_format="pdf"
)

# 4. PNG'ye çevir + Instagram boyutuna resize et
python3 -c "
import fitz
from PIL import Image
doc = fitz.open('/tmp/karusel.pdf')
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=200)
    pix.save(f'/tmp/slayt_{i+1:02d}.png')
    img = Image.open(f'/tmp/slayt_{i+1:02d}.png')
    img = img.resize((1080, 1350), Image.LANCZOS)
    img.save(f'/tmp/slayt_{i+1:02d}.jpg', 'JPEG', quality=85)
"
```

## Pitfalls (28 Haz 2026)

### ⏱ Studio generation ~3-7 dk sürer
"1-3 dk" beklentisi yanlış. Genelde 5-7 dk sürüyor. Sakın poll'layarak bekleme — cron tetikleyici kur, o hazır olunca uyan.

### 🔐 Auth stale → download hatası
studio_status "completed" gösterse bile MCP download_artifact "Download failed" dönebilir.
curl ile indirirsen Google login sayfası gelir (auth cookie'si stale).
**Çözüm:**
```bash
python3 ~/.hermes/scripts/nb_keepalive.py   # CDP+BWS ile auto-login
mcp_notebooklm_mcp_refresh_auth              # MCP'ye yeni tokenları yükle
# Sonra tekrar download dene
```

### 📐 PDF landscape çıkar (3823x2134)
Studio slide_deck landscape (16:9) üretir. Instagram karusel portrait (4:5 = 1080x1350) gerektirir.
PNG'ye çevirdikten sonra PIL ile resize et.

### 🖼 Image-based PDF
Studio image-based PDF üretir — metin çıkarılamaz (page.get_text() boş döner).
Doğrulama için vision_analyze gerekir (ama Pollinations vision auth sorunu verebilir).

### 🔄 Otomatik başlık
Studio focus_prompt'ta net başlık versen bile kendi başlığını koyabilir.
APA Bilgi notebook'unda "Shapes of Connection" başlığını kendi koydu.
Sorun değil — karusel içeriği doğru oluyor, başlık sadece PDF'in adını etkiliyor.

### 👁 Vision doğrulama
Pollinations vision API bazen 401 auth hatası verebilir. Fallback:
- Dosya boyutuna bakarak slaytları eşleştir (önceden bilinen boyutlar varsa)
- Veya kullanıcıya gösterip manuel onay al

## Çalışan Notebooklar
- **BDT** (a4fe729d-c561-4238-9bea-81bea8e3dcbc) — 256 kaynak, shared_with_me ✅
- **APA Bilgi** (c44469fe-a69a-4a86-8dd8-756c2f365109) — 28 kaynak, owned ✅
- slide_deck her ikisinde de çalışıyor
