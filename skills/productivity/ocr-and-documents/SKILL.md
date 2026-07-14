---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, marker-pdf)."
version: 2.4.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **easyocr** (~1-2GB) | ❌ | ✅ (80+ languages) |
| **Features / Install** | | |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) | ~1-2GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) | ~2-5s/image (CPU), GPU varsa hızlı |
| **Binary gerekmez** | ✅ | ❌ (PyTorch) | ✅ (sadece pip) |
| **Türkçe OCR** | ❌ | ✅ (90+ dil) | ✅ (Türkçe dahil 80+ dil) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

- **OCR ihtiyacın varsa ve sistemde GPU yoksa** → marker-pdf dene (daha doğru ama ağır)
- **Hızlı OCR lazımsa ve PyTorch varsa** → easyocr dene (binary gerekmez, `pip install easyocr`)
- **Sistemde zaten tesseract-ocr kuruluysa** → pytesseract kullan (en hafif OCR)

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)

## easyocr (Lightweight OCR, Binary Gerekmez)

`easyocr` PyTorch üzerine kurulu, ayrı bir binary (tesseract) gerektirmez. Türkçe dahil 80+ dil desteği var.

```bash
pip install easyocr
```

**Kullanım:**
```python
import easyocr
reader = easyocr.Reader(['tr', 'en'])  # Türkçe + İngilizce
results = reader.readtext('foto.png', detail=1)

for (bbox, text, confidence) in results:
    print(f"{text} ({confidence:.2f})")
```

**Parametreler:**
- `detail=0` → sadece metin listesi
- `paragraph=True` → paragraf birleştirme
- `min_size=10` → küçük metinleri atla
- `text_threshold=0.7` → güven eşiği

**Avantaj:** Binary gerekmez, `pip install ile çalışır.`
**Dezavantaj:** İlk çalıştırmada model indirir (~1-2GB).

## tesseract-ocr (Sistem Binary'si, En Hafif)

```bash
sudo apt install tesseract-ocr tesseract-ocr-tur
pip install pytesseract
```

```python
from PIL import Image
import pytesseract
text = pytesseract.image_to_string(Image.open('foto.png'), lang='tur')
```

**Not:** `mcp_local_secure_secure_vision` tesseract binary'sini kullanır. Binary yoksa çalışmaz.

## Türkçe OCR Araştırması — PaddleOCR 🏆

**OCRTurk benchmark** (arXiv 2602.03693, Şubat 2026) 7 modeli 180 Türkçe belge üzerinde test etti:

| Model | Türkçe Doğruluk | Binary Gerekli | pip ile Kurulum |
|-------|----------------|----------------|-----------------|
| **PaddleOCR** | 🥇 **En yüksek** (eğri metin %88.7) | Hayır | `pip install paddlepaddle paddleocr` |
| EasyOCR | 🥈 Orta-yüksek (80+ dil) | Hayır | `pip install easyocr` |
| Tesseract | 🥉 Düşük (eğri metin %52.1) | **Evet** (apt) | `sudo apt install tesseract-ocr tesseract-ocr-tur` + `pip install pytesseract` |

**PaddleOCR avantajları:**
- Kavisli/eğri metinlerde çok başarılı (%88.7 vs Tesseract %52.1)
- Slayt görselleri, karmaşık düzenler ve gürültülü taramalarda lider
- Binary gerekmez (PyTorch üzerinde çalışır)
- 80+ dil desteği (Türkçe dahil)

**Slayt/screenshot analizi için öneri:** PaddleOCR > EasyOCR > Tesseract

### OCR Karar Ağacı (Güncellenmiş)

```
OCR lazım mı?
├── URL var mı? → web_extract(url) dene
├── En yüksek doğruluk mu gerekli?
│   └── PaddleOCR (pip install paddlepaddle paddleocr)
├── Binary yok, hızlı kurulum mu?
│   └── easyocr (pip install easyocr)
├── tesseract var mı? → pytesseract (en hafif)
└── Hiçbiri → pymupdf (text-based PDF'ler için)
```

## Pitfalls

### ctx_execute_file binary PDF'lerde çalışmaz

`ctx_execute_file`, dosyayı UTF-8 olarak decode etmeye çalışır. PDF gibi binary dosyalarda `UnicodeDecodeError` verir. **Çözüm:** terminal ile `pdftotext` veya `python3 -c "import pymupdf..."` kullan.

```bash
# En hızlısı — sistemde pdftotext varsa:
pdftotext "/path/to/file.pdf" -

# Alternatif — pymupdf ile:
python3 -c "
import pymupdf
doc = pymupdf.open('/path/to/file.pdf')
for page in doc:
    print(page.get_text())
"
```
