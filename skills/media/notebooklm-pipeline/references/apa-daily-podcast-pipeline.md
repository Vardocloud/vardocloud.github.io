# APA Daily Podcast Pipeline

> **Use case:** Cron-driven daily pipeline: scrape APA newsletters → add to NotebookLM → generate Audio Overview podcast.
> **Origin:** 2026-06-25, Edel's request for daily APA podcast at end of day.
> **Cron job:** `d4e5348f059f` (APA Günlük İçerik Kontrolü)

## Architecture

```
Sabah (09:15):  Scrape APA → Extract content → Add sources to NotebookLM
                                        ↓
Öğlen (15:15):  Check for new content (same day additions)
                                        ↓
Akşam (22:15):  Collect day's sources → Generate Audio Overview → Deliver link
```

## Dual-Cron Workflow

### Sabah Cron (09:15) — Collect & Add Sources
1. Tarama: Gmail (APA bültenleri) + APA Monitor + Press Releases + Events + Podcast
2. İçerik çıkar: her makale için yapılandırılmış özet
3. NotebookLM'deki "APA Günlük" notebook'una **source ekle**:
   - `source_add(type="url")` — doğrudan makale URL'si
   - `source_add(type="text")` — extracted text (Gmail içeriği için)
4. Duplicate kontrol: notebook'ta zaten varsa atla
   - `notebook_get()` ile mevcut kaynakları listele
   - URL veya title match ile dedup

### Akşam Cron (22:15) — Generate Podcast
1. Gün içinde eklenen yeni kaynakları tespit et
2. Eğer yeni kaynak varsa:
   - `studio_create(notebook_id, artifact_type="audio")` ile Audio Overview başlat
   - `studio_status()` ile tamamlanmasını bekle
   - `download_artifact()` ile MP3/MP4'ü indir
   - MEDIA: ile Edel'e gönder
3. Yeni kaynak yoksa → `[SILENT]` (podcast oluşturma)

## Content Presentation Guidelines (Edel's Preferences)

### Article Type → Length Mapping

| Article Type | Length | Structure |
|---|---|---|
| Short news/bulletin item | 3-5 cümle | What → So what |
| Standard article (1-2 pages) | 5-10 cümle, 2 paragraf | Question → Findings → Clinical meaning |
| Long article/review (3+ pages) | 10-15 cümle, 3-4 paragraf | Core question → Method → Findings → Clinical meaning → Broader implications |

### Per-Article Structure (her tipte aynı akış)
1. **Ne anlatıyor?** — Yazının özü, temel araştırma sorusu veya konusu
2. **Ne diyor?** — Bulgular, argümanlar, yazarın ulaştığı sonuç
3. **Bunun anlamı ne?** — Klinik/pratik çıkarım, "Yani..." ile bağlanan cümle

### Anlatım Biçimi
- ✅ Anlaşılır Türkçe — akademik jargonu sadeleştir
- ✅ "Yani..." ile bağla — bulguyu günlük dile çevir
- ✅ Başlıklar halinde yapılandır (kategorilere ayır)
- ✅ APA yazısının temel sorusuna ilk cümlede değin
- ❌ Gereksiz metodolojik detay (örneklem büyüklüğü, p değeri sadece çarpıcıysa)
- ❌ Uzun, akışı olmayan paragraflar
- ❌ Copy-paste özet (kendi cümlelerinle yeniden yaz)

### Podcast Metni vs Yazılı Özet Farkı
- **Podcast'te:** Daha konuşma dili, doğal akış, "şimdi gelelim..." gibi geçişler
- **Yazılı özette:** Daha yapılandırılmış, başlıklar ve maddeler halinde
- İkisi de aynı içeriği farklı formatta sunar

## Notebook Setup

### "APA Günlük" Notebook
- Amaç: Günlük APA içeriklerinin toplandığı ana notebook
- Her gün yeni APA makaleleri source olarak eklenir
- Akşam podcast'i bu notebook'taki o günün kaynaklarından oluşturulur
- Eski kaynaklar silinmez (birikir) — podcast sadece o gün eklenenlerle sınırlı

### Duplicate Source Detection
```python
notebook = notebook_get(notebook_id)
existing_urls = [s['url'] for s in notebook['sources'] if s.get('url')]
existing_titles = [s['title'] for s in notebook['sources']]
# Check if URL or fuzzy title match exists before adding
```

### Source Cleanup
- Kaynaklar biriktikçe NotebookLM'in limitlerine takılabilir
- Haftada bir: 7+ günlük kaynakları temizle (`source_delete`)
- Veya aylık yeni notebook oluştur (ör: "APA Haziran 2026")

## Learning Integration

Çıkarılan bilgiler sadece Edel'e sunulmaz, aynı zamanda:
- `~/wiki/apa-articles/YYYY-MM-<slug>.md` — İngilizce wiki dosyası (yapılandırılmış: önemli kavramlar, kaynakça)
- `llm-wiki` skill'ini kullanarak wiki'ye kaydet
- Index kontrolü: `~/wiki/apa-articles/index.md`'de duplicate kontrolü

## Troubleshooting

### "No authentication found" / Permission denied on cookies.json
```bash
# Sorun: ~/.notebooklm-mcp-cli/ dizini root:root sahibi
# Çözüm: Container dışından chown gerekir
docker exec -u root vanitas-hermes chown -R ubuntu:ubuntu /home/ubuntu/.notebooklm-mcp-cli/

# Alternatif: nlm login --provider openclaw --cdp-url ws://host.docker.internal:9222
# (Windows Chrome debug modda açık olmalı)
```

### Studio create fails / Auth expired
Bkz: `references/nlm-auth-repair-workflow.md` (Yöntem 1: Headless Playwright)
