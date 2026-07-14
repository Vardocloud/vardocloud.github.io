---
name: paper-extraction
description: "Akademik makalelerden yapılandırılmış veri çıkarma — PDF/HTML/XML'den metodoloji, bulgular, örneklem, istatistik otomatik tablolama."
version: 1.0.0
metadata:
  hermes:
    tags: [research, extraction, papers, pdf, structured-data, tabulation]
    category: research
---

# Paper Extraction — Makalelerden Yapılandırılmış Veri Çıkarma

Araştırma makalelerinden (PubMed XML, Semantic Scholar, PDF) sistematik veri çıkarma.
Psikoloji/psikiyatri alanındaki RCT'ler, meta-analizler ve kalitatif çalışmalar için optimize.

## Trigger

Edel "makaleyi çıkar", "tablo yap", "veri çıkar", "bulguları özetle", "metodolojiyi çıkar"
veya "extraction table" dediğinde yüklenir.

---

## Çıkarım Şablonu (Psikoloji RCT)

Her makale için şu alanlar çıkarılır:

| Alan | Açıklama | Öncelik |
|------|----------|---------|
| **Yazar(lar) + Yıl** | APA formatı | Zorunlu |
| **Başlık** | Tam başlık | Zorunlu |
| **DOI** | Varsa | Önerilen |
| **Çalışma Tasarımı** | RCT / Kohort / Vaka-kontrol / Kalitatif | Zorunlu |
| **Popülasyon** | N, yaş (M±SD), cinsiyet dağılımı, tanı | Zorunlu |
| **Müdahale** | Terapi türü, seans sayısı, süre | Zorunlu |
| **Karşılaştırıcı** | Kontrol grubu, TAU, bekleme listesi | Zorunlu |
| **Birincil Sonuç** | Ölçek(ler), etki büyüklüğü (d/η²), p değeri | Zorunlu |
| **İkincil Sonuç** | Diğer ölçümler | İsteğe bağlı |
| **Dropout** | Kayıp oranı, nedenleri | Önerilen |
| **Ülke** | Çalışmanın yapıldığı ülke | Önerilen |
| **Kalite Puanı** | Jadad / ROB-2 / AMSTAR | İsteğe bağlı |
| **Ana Bulgu (1 cümle)** | Türkçe özet | Zorunlu |

---

## Veri Kaynaklarına Göre Çıkarım Stratejisi

### Kaynak 1: PubMed XML (En İyi)

```python
from Bio import Entrez
Entrez.email = 'ulucanberkcan@gmail.com'

# Makale detaylarını XML olarak çek
handle = Entrez.efetch(db='pubmed', id=pmid, rettype='xml')
record = Entrez.read(handle)

# Yapılandırılmış alanlar:
# - ArticleTitle → Başlık
# - Abstract/AbstractText → Özet (Label="BACKGROUND","METHODS","RESULTS","CONCLUSIONS")
# - AuthorList → Yazarlar
# - PublicationType → "Randomized Controlled Trial" kontrolü
# - MeshHeadingList → MeSH terimleri
```

### Kaynak 2: Semantic Scholar (Browser)

```python
# browser_navigate → makale sayfası
# browser_snapshot → yapılandırılmış veri:
#   - Başlık, yazarlar, yıl
#   - Atıf sayısı (.citation-count)
#   - Abstract (truncated)
#   - DOI
# browser_click → References/Citations sekmeleri
```

### Kaynak 3: PDF (web_extract ile)

```python
# PDF URL'sini direkt web_extract'e ver
web_extract(urls=[pdf_url])
# → Markdown formatında döner, yapılandırılmış çıkarım için:
# - Metodoloji bölümünü regex ile bul: r"(?i)methods?\b.*?(?=\bresults?\b)"
# - N değerini bul: r"(?i)n\s*=\s*(\d+)"
# - Etki büyüklüğü: r"(?i)(cohen'?s?\s*d|hedges'?\s*g|η[²2])\s*=\s*(0?\.\d+)"
```

---

## Çıktı Formatı

### Markdown Tablosu
```markdown
| # | Yazar (Yıl) | Tasarım | N | Müdahale | Karşılaştırıcı | Etki (d) | Ana Bulgu |
|---|------------|---------|---|----------|---------------|----------|-----------|
| 1 | Smith (2023) | RCT | 120 | CBT (12 seans) | TAU | 0.72 | CBT anksiyetede etkili |
```

### CSV (Data Analizi İçin)
```csv
id,author_year,design,n,intervention,comparator,effect_size,p_value,main_finding
1,"Smith (2023)","RCT",120,"CBT (12 seans)","TAU",0.72,0.001,"CBT anksiyetede etkili"
```

---

## Paralel Çıkarım (delegate_task)

5+ makale varsa paralel çıkarım yap:

```python
delegate_task(tasks=[
    {"goal": "Makale 1-5 çıkar", "context": "PMID'ler: ..."},
    {"goal": "Makale 6-10 çıkar", "context": "PMID'ler: ..."},
    {"goal": "Makale 11-15 çıkar", "context": "PMID'ler: ..."}
])
# Sonra birleştir: terminal("cat ~/research_XXX/extraction_*.md > final_table.md")
```

---

## Kalite Değerlendirmesi

RCT'ler için **Jadad skoru** (hızlı):
1. Randomizasyon var mı? (+1)
2. Uygun randomizasyon? (+1)
3. Körleme var mı? (+1)
4. Uygun körleme? (+1)
5. Dropout raporlanmış mı? (+1)

Toplam: 0-5 (≥3 = kaliteli)

---

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| PubMed XML parse başarısız | `rettype='abstract'`, `retmode='text'` fallback |
| Abstract yok | Tam metin gerekli — Edel'e sor "tam metin var mı?" |
| Etki büyüklüğü raporlanmamış | Mean/SD'den hesapla: `d = (M1-M2)/SD_pooled` |
| PDF parse hatalı | OCR gerekebilir — `pymupdf` alternatifi |
| Türkçe makale | Tr dizinlerden ekle (DergiPark, TRDizin) |
