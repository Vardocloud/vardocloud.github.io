# Read Hierarchy — Gerçek Kullanım vs Teorik (23 Tem 2026)

## Keşif

Edel'in 23 Tem 2026 sorusu: "NotebookLM'e aktarılan bilgiler verdiğim sorgularda inceleniyor mu?" Cevap: Hayır.

## 6 Katmanlı Hiyerarşi — Pratik Tablo

| Katman | Teorik Durum | Pratik Durum | Gecikme |
|--------|-------------|--------------|---------|
| 1. MEMORY.md + USER.md | Her zaman | ✅ Her tur injekte edilir | ~5ms |
| 2. session_search | Sık | ✅ Etkin kullanılır | ~50ms |
| 3. Skills | Otomatik | ✅ Skill eşleşirse yüklenir | ~100ms |
| 4. wiki_fts | Var | ⏳ Ara sıra sorgulanır | ~10ms |
| 5. messages_fts | Asıl FTS | ✅ session_search içinde | ~50ms |
| 6. NotebookLM | Derin arşiv | ❌ Neredeyse hiç sorgulanmaz | 10-30s |

## Layer 6 Gap — Nedenleri

1. **Gecikme farkı:** session_search 50ms, NotebookLM 10-30s — 200-600x yavaş
2. **Auth kırılganlığı:** Keepalive çalışsa bile cookie her an expire olabilir
3. **Tool zinciri:** NotebookLM sorgusu havadan (async HTTP) yanıt bekler, session_search yerel SQLite
4. **Alışkanlık:** session_search ilk akla gelen, NotebookLM 6. sırada

## İmplikasyonlar

- **Wiki (Layer 4) asıl arşivdir.** NotebookLM'e atılan bilgi görünmez.
- **Wiki'ye yazılan her şey okunabilir kalmalı.** Bilgiyi wiki'ye koyup "NotebookLM'de de var" diye varsayma.
- **NotebookLM = Studio üretim aracı, arşiv değil.** Audio/quiz/video/slide deck üretimi için idealdir. Referans sorgulama için değil.
- **Wiki_fts'yi güçlendirmek** (trigram geçişi, index rebuild) Layer 6'yı aktive etmekten daha önceliklidir.

## Ne Zaman NotebookLM Sorgulanmalı

1. Wiki_fts'de hiç sonuç yoksa (trigram ile de)
2. Studio içeriği (audio/video) lazımsa
3. Multimodal arama gerekiyorsa (Drive'daki PDF'ler, görseller)
4. Edel özellikle "NotebookLM'de ara" derse

Aksi durumda: session_search + wiki_fts yeterlidir.
