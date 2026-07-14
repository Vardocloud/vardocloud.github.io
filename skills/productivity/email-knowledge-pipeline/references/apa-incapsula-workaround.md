# APA Incapsula Workaround

APA websitesi (`apa.org`) Incapsula WAF kullanır — Oracle Cloud IP'sinden direkt erişimi engeller.

## Sorun
- `NotebookLM source_add` → Incapsula hatası (Request unsuccessful)
- Sunucu IP'si datacenter olarak algılanır → block
- WARP SOCKS5 proxy de her zaman çalışmaz (Incapsula daha agresif filtreler)

## Workaround (3 Katmanlı)

### Katman 1: web_extract
```python
web_extract(urls=["https://www.apa.org/monitor/2026/04-05/..."])
```
- İlk 5000 karakteri alır (genelde yeterli)
- LLM timeout olursa içerik truncate olur ama ana fikir alınır

### Katman 2: Pollinations webSearch
```python
mcp_pollinations_webSearch(query="APA Monitor 'makale başlığı' yazar 2026 key findings")
```
- Perplexity tabanlı, Incapsula'dan etkilenmez
- Makalenin ana bulgularını yapılandırılmış şekilde döner

### Katman 3: Elle birleştir
- web_extract'ten gelen giriş + Pollinations'tan gelen bulgular
- Türkçe özet formatında birleştir (ANA FİKİR, KRİTİK BULGULAR, KLİNİK ÇIKARIMLAR)

## APA Makale Özet Formatı

```markdown
## 🎮 [Makale Başlığı - Türkçe anlamlı]

**Yazar:** [isim] | **APA Monitor,** [tarih] | [süre] dk okuma

### 🧠 ANA FİKİR
[1-2 cümle]

### 🔑 KRİTİK BULGULAR
- [Madde 1]
- [Madde 2]

### 👥 ÖNE ÇIKAN İSİMLER VE YAPTIKLARI
| İsim | Rolü | Ne Yapıyor |

### 🇹🇷 TÜRKİYE'DEKİ PSİKOLOG İÇİN ÇIKARIMLAR
1. [Pratik uygulama]
2. [İçerik fikri]
```

## Örnek
Bkz. 30 Mayıs 2026: "How psychologists are shaping esports" — web_extract ilk 5K + Pollinations webSearch → Türkçe özet.
