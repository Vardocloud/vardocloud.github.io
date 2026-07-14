---
name: literature-search
description: "Sistematik literatür taraması — PubMed API, Semantic Scholar browser scraping, PRISMA pipeline. Psikoloji/psikiyatri odaklı."
version: 1.0.0
metadata:
  hermes:
    tags: [research, literature, pubmed, semantic-scholar, prisma, systematic-review]
    category: research
---

# Literature Search — Sistematik Literatür Taraması

PubMed Entrez API (ücretsiz) ve Semantic Scholar browser scraping ile PRISMA uyumlu
sistematik literatür taraması. Psikoloji/psikiyatri alanı için optimize edilmiştir.

## Trigger

Edel "literatür tara", "makale ara", "PRISMA", "sistematik derleme", "literature search"
veya "kaynak taraması" dediğinde bu skill yüklenmelidir.

---

## Phase 1: Araştırma Sorusu Netleştirme

Araştırmaya başlamadan önce 3 soruyla kapsamı daralt:

1. **PICO formatı:** Population (kim?), Intervention (ne?), Comparison (neyle karşılaştırılacak?), Outcome (sonuç ne?)
2. **Zaman aralığı:** Son 5 yıl? 10 yıl? Tüm zamanlar?
3. **Çalışma tipi:** Sadece RCT? Meta-analiz dahil? Kalitatif çalışmalar?

Bu soruları sormadan araştırmaya başlama.

---

## Phase 2: PubMed Entrez API (Ücretsiz)

### Kurulum (ilk kullanımda)
```bash
ALL_PROXY="" pip3 install biopython --break-system-packages -q
```

### Temel Arama
```python
from Bio import Entrez
Entrez.email = 'ulucanberkcan@gmail.com'  # NCBI için zorunlu

# Anahtar kelime araması
handle = Entrez.esearch(db='pubmed', term='cognitive behavioral therapy anxiety RCT', retmax=20, sort='relevance')
record = Entrez.read(handle)
id_list = record['IdList']  # PMID'ler
total = record['Count']     # Toplam sonuç

# Makale detaylarını çek
handle = Entrez.efetch(db='pubmed', id=','.join(id_list), rettype='abstract', retmode='xml')
```

### Psikoloji Filtreleri
```
# RCT filtreleme
term + " AND (randomized controlled trial[Publication Type] OR clinical trial[Publication Type])"

# Meta-analiz
term + " AND meta-analysis[Publication Type]"

# Türkçe yayınlar (Türkiye'den)
term + " AND Turkey[Affiliation]"

# Son 5 yıl
term + " AND (\"2020\"[Date - Publication] : \"3000\"[Date - Publication])"
```

### Rate Limit
- API key olmadan: saniyede 3 istek
- API key ile: saniyede 10 istek
- `Entrez.email` zorunlu (rate limit için NCBI takip eder)

### Kurulum Püf Noktası (WARP Tuzağı)
WARP SOCKS5 proxy, PyPI bağlantısını keser (`Connection reset by peer`). Biopython kurulumu için:
```bash
ALL_PROXY="" pip3 install biopython --break-system-packages -q
```
Ardından test: `ALL_PROXY="" python3 -c "from Bio import Entrez; print('OK')"`
PubMed sorguları için her seferinde `ALL_PROXY=""` kullan (NCBI direkt bağlantı ister, WARP'ta timeout).

---

## Phase 3: Semantic Scholar (Browser Scraping)

API key alınamıyorsa browser scraping kullanılır.

### Arama URL Formatı
```
# Temel arama
https://www.semanticscholar.org/search?q={URL_ENCODED_QUERY}&sort=relevance

# Yıl filtreli (test edildi ✅ — 29 May 2026)
https://www.semanticscholar.org/search?q={QUERY}&sort=relevance&year%5B%5D={START}&year%5B%5D={END}
# Örnek: ...&year%5B%5D=2021&year%5B%5D=2026

# Diğer filtreler (URL'e eklenebilir):
# &pdf%5B%5D=true → sadece PDF'i olanlar
# &fieldsOfStudy%5B%5D=Psychology → alan filtresi
```

### Browser Scraping Stratejisi
1. `browser_navigate` → arama sonuç sayfası
2. `browser_snapshot` → ilk 10 sonucu oku
3. `browser_click` → her makaleye tıkla, detayları al
4. `browser_vision` → gerekirse CAPTCHA/engel kontrolü

### Çıkarılacak Veriler
- Başlık, yazarlar, yıl, dergi
- Atıf sayısı, etkili atıf sayısı
- Özet (truncated olabilir)
- DOI (varsa)
- Semantic Scholar ID

### Anti-Bot Önlemleri
- Her istek arası 2-3 saniye bekle
- Session başına maksimum 15-20 makale
- 429 alınırsa 5 dakika bekle, session'ı sıfırla
- BrowserBase yerine Playwright tercih et (CloudFront daha az agresif)

---

## Phase 4: PRISMA Pipeline

```
┌─────────────────────────────────────────────┐
│  IDENTIFICATION (PubMed + Semantic Scholar) │
│  Toplam: N makale                           │
├─────────────────────────────────────────────┤
│  SCREENING (Başlık + Özet taraması)         │
│  Kalan: N1 makale (duplikasyon çıkarıldı)   │
├─────────────────────────────────────────────┤
│  ELIGIBILITY (Tam metin değerlendirme)       │
│  Kalan: N2 makale                           │
├─────────────────────────────────────────────┤
│  INCLUDED (Final sentez)                    │
│  Sonuç: N3 makale                           │
└─────────────────────────────────────────────┘
```

### PRISMA Akış Diyagramı Çıktısı
Araştırma sonunda şu formatta rapor:
```markdown
## PRISMA Akış Diyagramı

- **Identification:** PubMed'den X, Semantic Scholar'dan Y → Toplam Z
- **Screening:** Duplikasyon çıkarıldı → W makale
- **Eligibility:** Başlık/özet taraması → V makale
- **Included:** Tam metin değerlendirme → U makale

## Hariç Tutma Nedenleri
- Yanlış popülasyon: N
- Yanlış müdahale: N
- Tam metin yok: N
```

---

## Phase 5: Entegrasyon

### Tek Komutla Çalıştırma
Araştırma bir cron job veya delegate_task ile şu şekilde başlatılır:

```
delegate_task:
  goal: "PubMed ve Semantic Scholar'da PRISMA pipeline ile [konu] tara"
  context: "ARAŞTIRMA SORUSU: ... / FİLTRELER: son 5 yıl, RCT, meta-analiz"
  toolsets: ["terminal", "web", "browser", "file"]
```

### Çıktı Dosyaları
```
~/research_XXX/
├── prisma_diagram.md         # PRISMA akış şeması
├── pubmed_results.md         # PubMed'den gelenler
├── semantic_scholar_results.md  # Semantic Scholar'dan gelenler
├── included_papers.md        # Final dahil edilen makaleler
└── extraction_table.md       # Makale çıkarım tablosu
```

---

## Avantajlar & Sınırlamalar

| Özellik | PubMed | Semantic Scholar |
|---------|--------|-----------------|
| Erişim | Ücretsiz API ✅ | Browser scraping (rate-limit riski) |
| Kapsam | Biyomedikal | Tüm disiplinler |
| Atıf verisi | Yok | Var (etkili atıf) |
| Tam metin | Abstract sadece | Abstract sadece |
| Hız | Yüksek (API) | Düşük (browser) |

---

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| PubMed rate-limit aşımı | Saniyede 3 istek sınırında kal, `time.sleep(0.34)` |
| Semantic Scholar 429 | 5 dk bekle, session sıfırla |
| BrowserBase timeout | Playwright fallback kullan |
| Cookie banner engeli | İlk navigate'te "Cookie Preferences" butonu çıkar → `browser_click` ile kapat |
| Çok geniş arama → binlerce sonuç | PICO formatıyla daralt, filtre ekle |
| PubMed'e erişim yok (WARP) | `ALL_PROXY=""` ile direkt bağlan. Detay: `references/pubmed-setup.md` |
| PubMed'e erişim yok (WARP) | `ALL_PROXY=""` ile direkt bağlan. WARP SOCKS5 Google/NCBI API'lerini blokluyor |
| Duplikasyon temizliği | DOI + başlık benzerliği ile kontrol et |
| BioPython import hatası | Sistem Python'una kur: `ALL_PROXY="" pip3 install biopython --break-system-packages` |
