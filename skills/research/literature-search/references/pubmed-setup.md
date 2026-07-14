# PubMed Entrez + Biopython Setup

## Kurulum (WARP Pitfall'ı)

Oracle Cloud sunucusunda WARP SOCKS5 proxy **PyPI bağlantısını keser**. Biopython kurmak için:

```bash
ALL_PROXY="" pip3 install biopython --break-system-packages -q
```

`--break-system-packages` gerekli çünkü sistem Python'u PEP 668 korumalı.

## Doğrulama

```bash
ALL_PROXY="" python3 -c "from Bio import Entrez; print('OK')"
```

## PubMed Araması

```python
from Bio import Entrez
Entrez.email = 'ulucanberkcan@gmail.com'  # NCBI rate-limit için zorunlu

# Anahtar kelime araması
handle = Entrez.esearch(db='pubmed', term='cognitive behavioral therapy anxiety RCT', retmax=20)
record = Entrez.read(handle)
# record['IdList'] → PMID listesi
# record['Count'] → toplam sonuç

# Makale detayları
handle = Entrez.efetch(db='pubmed', id=','.join(id_list), rettype='abstract', retmode='xml')
```

## Rate Limit

- API key OLMADAN: 3 istek/saniye (yeterli)
- API key İLE: 10 istek/saniye
- `Entrez.email` zorunlu — NCBI takip için

## Pitfall: WARP Proxy

PubMed Entrez API'ye **WARP'sız** bağlanılmalı. WARP üzerinden NCBI erişimi yok.

```bash
# PubMed: WARP'sız
ALL_PROXY="" python3 -c "..."

# Semantic Scholar: WARP'lı (browser scraping için)
# browser_navigate ile WARP otomatik
```
