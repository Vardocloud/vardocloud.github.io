---
name: markitdown-mcp
description: "MarkItDown MCP — 29+ dosya formatını Markdown'a çevir. PDF, DOCX, PPTX, XLSX, EPUB, ZIP, HTML → temiz Markdown. %70 token tasarrufu."
version: 1.1.0
metadata:
  hermes:
    tags: [mcp, markitdown, file-conversion, token-saving, microsoft]
    category: devops
---

# MarkItDown MCP

Microsoft MarkItDown kütüphanesi tabanlı MCP server. 29+ dosya formatını temiz Markdown'a çevirir. Claude'da token kullanımını %70'e kadar düşürür.

**Repo:** https://github.com/trsdn/markitdown-mcp
**Binary:** `/home/ubuntu/.local/bin/markitdown-mcp`

## Kurulum

```bash
cd /tmp && git clone https://github.com/trsdn/markitdown-mcp.git
cd markitdown-mcp && pip install -e ".[all]"

# Hermes'e ekle:
echo "y" | hermes mcp add markitdown --command /home/ubuntu/.local/bin/markitdown-mcp
```

## Araçlar

| Araç | Açıklama |
|------|----------|
| `convert_file` | Tek dosyayı Markdown'a çevir. file_path parametresi. |
| `convert_directory` | Klasördeki tüm desteklenen dosyaları tara ve Markdown'a çevir. |
| `list_supported_formats` | Desteklenen tüm formatları listele. |

## Desteklenen Formatlar (29+)

| Kategori | Uzantılar |
|----------|-----------|
| Office | .pdf, .docx, .pptx, .xlsx, .xls |
| Görsel | .jpg, .png, .gif, .bmp, .tiff, .webp (EXIF metadata) |
| Ses | .mp3, .wav (speech-to-text transkripsiyon) |
| Web | .html, .htm, .xml, .json, .csv |
| Kitap | .epub |
| Arşiv | .zip (auto-extract) |
| Metin | .txt, .md, .rst |

## Kullanım Örnekleri

```python
# PDF'yi Markdown'a çevir
mcp_markitdown_convert_file(file_path="/tmp/belge.pdf")

# Tüm klasörü tara
mcp_markitdown_convert_directory(input_directory="/tmp/dosyalar", output_directory="/tmp/markdown")
```

## Ne Zaman Kullanılır (Triggers)

**Bu skill'i ŞU DURUMLARDA otomatik yükle ve kullan:**

| Durum | Örnek | Aksiyon |
|-------|-------|---------|
| 📄 Edel forward/link olarak dosya gönderdiğinde | PDF, DOCX, PPTX, XLSX, EPUB | `convert_file` ile Markdown'a çevir, sonra oku |
| 📚 Sınav/ders belgeleri geldiğinde | PTE Academic PDF'leri, ders notları, APA raporları | Önce Markdown'a çevir, token ~%70 tasarruf |
| 🔗 Web sayfası içeriği okunacağında | HTML sayfaları, blog yazıları | `convert_file` ile temiz Markdown al |
| 📦 ZIP ile gelen belgelerde | Arşiv içindeki dokümanlar | Arşivi extract et, sonra convert |

**Kritik kural (bkz. sohbet SIN #15):** Bir dosyayı okumam gerektiği an, aklıma gelen İLK araç MarkItDown olmalı. `read_file` / `terminal cat` / `vision_analyze` SONRAKİ seçenektir.

### Özel Akış: PTE Academic / Sınav Belgeleri

Edel'in PTE Academic hazırlık belgeleri (PDF'ler, DOC dosyaları, sınav notları) için:

```
1. Dosyayı al (forward/link/download)
2. markitdown-mcp convert_file ile Markdown'a çevir
3. Çıktıyı kontrol et — metadata korunmuş mu?
4. Temiz metni NotebookLM'e kaynak olarak ekle veya doğrudan oku
```

Bu akış:
- ~%70 token tasarrufu sağlar
- NotebookLM'e eklerken format sorunlarını önler
- Özellikle Prediction Questions, Essay Repeated, Speaking Notes gibi PTE dokümanlarında kritiktir

## Pipeline Entegrasyonu

Instagram karusel / LinkedIn içerik üretiminde:

```
Kaynak PDF/PPTX → markitdown convert_file → temiz Markdown → NotebookLM'e kaynak olarak ekle
```

Bu sayede NotebookLM, format bozukluklarıyla uğraşmaz, sadece içeriğe odaklanır.

## Otomatik Kullanım Kuralı (ZORUNLU)

Bir dosya okumam gerektiğinde:
1. `skill_view(name='markitdown-mcp')` — skill'i yükle
2. `mcp_markitdown_convert_file(file_path=...)'` ile Markdown'a çevir
3. Çıktıyı oku — token tüketimi ~%70 daha az

**Tetikleyici:** Edel Telegram'da PDF, DOCX, PPTX, XLSX, EPUB, ZIP, HTML, JSON, CSV dosyası gönderdiğinde veya forwardladığında — direkt read_file/terminal/vision kullanma, önce MarkItDown'ı dene.

**İstisna:** Görsel ağırlıklı PDF'ler (taranmış belge) MarkItDown'da metin çıkarmaz — alternatif olarak vision_analyze kullan.

## Güvenlik Uyarısı

⚠️ URI validasyonu yok — herhangi bir URI'yi çağırabilir. SADECE local dosyalarla kullan. Uzak URI'lere erişimi kısıtla. Reddit'te raporlanan güvenlik açığı: `microsoft/markitdown` MCP server'ı URI validation yapmıyor.

## Pitfalls

- **UNUTKANLIK TUZAĞI (1 Tem 2026):** Dosya okurken direkt read_file/terminal/vision'a atlama alışkanlığı var. Bunu kırmak için: bir dosya geldiği an kendine sor — "Bu dosyayı MarkItDown ile Markdown'a çevirebilir miyim?" Cevap evetse, önce MarkItDown kullan.
- Dosya büyükse (>50MB) dönüşüm uzun sürebilir
- PDF'lerde image-based içerik varsa Markdown'a metin olarak çıkmaz, vision gerekir
- Ses transkripsiyonu için `markitdown[all]` kurulu olmalı (speechrecognition + pydub)
- ZIP arşivleri otomatik extract edilir, iç içe ZIP'ler desteklenmez