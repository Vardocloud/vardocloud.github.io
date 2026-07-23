---
name: compress
description: "/compress — context-mode MCP ile konuşma geçmişini FTS5+BM25 indeksle, aranabilir hale getir. LLM özeti yerine searchable index. Sistem yapılandırması: context engine, compression threshold, hook script."
category: system
triggers:
  - /compress
  - compress
  - compaction
  - context compaction
  - context-mode
  - context engine
  - compression threshold
  - otomatik sıkıştırma
---

# /compress — Context-Mode Indexing & Sistem Altyapısı

`/compress` çağrıldığında, mevcut konuşma geçmişi context-mode MCP'nin
`ctx_index` aracı ile indekslenir. LLM tabanlı özetleme YERİNE,
FTS5 + BM25 ile aranabilir bir indeks oluşturulur.

## Sistemde Context-Mode Nasıl Çalışır

Context-mode Hermes'te iki seviyede yapılandırılmıştır:

| Seviye | Ne Yapar |
|--------|----------|
| **Context Engine** | Ana context engine olarak context-mode kullanılır — tüm session yönetimi onun üzerinden |
| **Compression Motoru** | Otomatik sıkıştırma aktif; eşik %20 (~200K token) |
| **Hook Script** | Her tool call öncesi çalışır — context-mode durumunu kontrol eder, loglar |
| **Head Koruması** | İlk 3 mesaj sıkıştırmadan korunur (system prompt + başlangıç) |
| **Tail Koruması** | Son 20 mesaj sıkıştırmadan korunur (konuşma akışını kaybetme) |
| **Hedef Oran** | Sıkıştırma sonrası context hedef boyutu %20 |
| **Sıkıştırma Modeli** | Hafif bir yardımcı model (Pollinations gemma) sıkıştırma özeti için |

## Otomatik vs Manuel

| Mekanizma | Ne Zaman | Nasıl |
|-----------|----------|-------|
| 🔄 **Otomatik (compression engine)** | Threshold %20 aşıldığında | Hermes kendi compression engine'i ile aradaki mesajları otomatik sıkıştırır. Vanitas müdahalesi gerekmez. |
| 🛡️ **Hook Script (otomatik)** | Her tool call öncesi | Context-mode hook'u sessizce çalışır, durumu kontrol eder |
| ✋ **Manuel — System Prompt Kuralı** | Context %20'ye yaklaştığında | Vanitas ZORUNLU olarak ctx_batch_execute veya /compress ile manuel sıkıştırma yapar |
| ⌨️ **Manuel — `/compress`** | İstenildiğinde | Tam indeksleme + search doğrulama + context temizleme |

**⚠️ Kritik:** Otomatik engine ayarlanmış olsa da, SOUL.md/system prompt'ta Vanitas'ın manuel olarak da sıkıştırma yapması ZORUNLU kuraldır. Otomatik engine yedek güvencedir, birincil mekanizma değil.

## System Prompt Kuralı (ZORUNLU)

```
Oturum sıkıştırma (ZORUNLU): Context %20 dolduğunda (200K token) 
oturum context-mode MCP ile sıkıştırılır. Sıkıştırılan oturumlar 
context-mode MCP üzerinden search edilir.
```

Bu kural şu anlama gelir:
- Context yaklaşık %20 dolduğunda dur ve sıkıştır
- `/compress` kullan veya doğrudan ctx_index + ctx_search + context temizle
- Sıkıştırılmış oturumları ctx_search ile sorgula
- Otomatik engine'e güvenme — kendin de kontrol et

## Ne Zaman Kullanılır

- `/compress` — konuşmayı indeksle
- `/compress <konu>` — belirli bir konuya odaklanarak indeksle (focus_topic)
- Context %20'ye yaklaştığında — sistem kuralı gereği manuel sıkıştır
- Uzun oturumlarda (50+ tool call) — proaktif sıkıştır
- Çoklu komut + sorgu gereken durumlarda ctx_batch_execute tercih et

## Nasıl Çalışır

### Adım 1: Konuşma geçmişini topla

Mevcut mesaj listesinden sistem mesajını ve son N mesajı AYIR.
Ortadaki tüm mesajları (user + assistant + tool) düz metin olarak birleştir.

Son 20 mesaj (tail) ve ilk sistem mesajı + ilk 3 mesaj (head) KORUNUR.
Sadece aradaki mesajlar indekse gönderilir.

### Adım 2: ctx_index veya ctx_batch_execute ile indeksle

**ctx_index (tek indeksleme):**
```python
mcp_context_mode_ctx_index(
    content=conversation_text,
    source=f"session-compaction-{timestamp}"
)
```

**ctx_batch_execute (çoklu komut + sorgu tek seferde):**
```python
mcp_context_mode_ctx_batch_execute(
    commands=[
        {"label": "Context Review", "command": "echo 'session analysis'"}
    ],
    queries=[
        "son aktif görev nedir?",
        "kullanıcının son isteği ne?",
        "hangi dosyalar değiştirildi?"
    ]
)
```

**ÖNEMLİ:** `ctx_index` sonrası `ctx_search` ile indeksin çalıştığını doğrula:
```python
mcp_context_mode_ctx_search(
    queries=["son konuşulan konu", "aktif görev"]
)
```

### Adım 3: Özet mesajı oluştur

Aşağıdaki formatta bir mesaj ile context'e geri dön:

```
[CONTEXT COMPACTION — CONTEXT-MODE INDEXED] Earlier turns were indexed
into context-mode MCP (FTS5 + BM25). Use ctx_search to retrieve.

## Active Task
[son kullanıcı mesajından çıkarılan görev]

## Index Info
- Source: session-compaction-{timestamp}
- Messages indexed: {count}
- Search: ctx_search(queries=["..."], source="session-compaction-{timestamp}")
```

### Adım 4: Eski mesajları context'ten çıkar

Head (system + ilk 3) ve tail (son 20) mesaj kalacak şekilde,
ortadaki indekslenmiş mesajları context'ten çıkar.
Yerine Adım 3'teki özet mesajını koy.

## Örnek Akış

```
Kullanıcı: /compress
→ ctx_index(content="...", source="session-compaction-20260531")
→ ctx_search(queries=["aktif görev"]) → doğrulandı
→ "[CONTEXT COMPACTION — CONTEXT-MODE INDEXED] ..." mesajı context'e eklendi
→ 127 mesaj indekslendi, context ~90% küçüldü
```

## Pitfalls

- **Tail mesajları KORU:** Son 20 mesaj her zaman verbatim context'te kalır.
  Aksi halde konuşma akışı kopar.
- **System prompt'u koru:** Sistem mesajı ASLA indekse dahil edilmez,
  her zaman context'te kalır.
- **İndeks doğrulaması yap:** `ctx_index` sonrası MUTLAKA `ctx_search` ile test et.
- **Focus topic kullan:** `/compress <konu>` ile odaklı indeksleme yap.
- **Session ID tutarlılığı:** Aynı oturumda birden çok sıkıştırma yapılırsa,
  aynı source ID'yi kullan — indeksler birikir.
- **Otomatik engine'e güvenme:** Config'de threshold 0.2 olması her zaman
  çalışacağı anlamına gelmez. System prompt kuralı ZORUNLU.
- **ctx_batch_execute büyük işler için:** Birden çok komut ve sorguyu tek
  seferde batch_execute ile yapmak daha verimlidir.
- **ctx_doctor ile durumu kontrol et:** Sıkıştırma öncesi `mcp_context_mode_ctx_doctor()`
  çalıştırarak context-mode'un sağlıklı olduğunu doğrula.

### session_search FTS5 Turkish Text Gap (19 Tem 2026)

`session_search` tool'u bazen var olan session'ları bulamaz. FTS5 index'te veri vardır
(direct SQLite sorgusu ile doğrulanabilir) ama FTS5 tokenizer Türkçe metinlerde
şu durumlarda takılır:

| Sorgu Tipi | Sorun | Örnek |
|-----------|-------|-------|
| **Kesme işareti** (`'`) | FTS5 "pc'de"yi iki token'a böler: "pc" + "de" | `lokal pc'de güvenli` → eşleşmez |
| **Uzun AND sorguları** (5+ kelime) | Her token ayrı ayrı eşleşmeli, biri kaçarsa sonuç boş | `lokal PC taşıma konuşma geçmişi silme` → çok fazla koşul |
| **Türkçe/İngilizce karışık** | Tokenizer beklendiği gibi çalışmayabilir | `qubernet sistemi gibi lokal pc'de` |

**Belirti:** `session_search(query="belirli_kelime")` boş döner ama:
```sql
-- Direct SQLite sorgusu çalışır:
SELECT count(*) FROM messages_fts WHERE messages_fts MATCH 'belirli_kelime';
```

#### Troubleshooting Akışı

session_search boş döndüğünde şu sırayı izle:

**1. Alternatif anahtar kelimeler dene** — Tek kelimeyle başla, yavaşça genişlet.
   `karanlık` → çalıştı mı? → `karanlık ikiz` → çalıştı mı?

**2. Wiki Session Index'e bak** — `~/wiki/references/session-index.md`
   Önemli konuşmalar etiket+session ID ile indekslenir. Bu dosyayı `grep` ile
   veya `search_files` ile tara:

```bash
search_files(pattern="etiket1 OR etiket2", path="~/wiki/references", file_glob="*index*")
```

**3. Direct SQLite sorgusu ile doğrula:**
```bash
# Session'ı bul (user mesajlarında ara — tool output'ları gürültü yapar)
sqlite3 ~/.hermes/state.db "SELECT s.id, s.title FROM messages m 
JOIN sessions s ON m.session_id = s.id 
WHERE m.content LIKE '%kelime%' AND m.role='user' 
GROUP BY s.id LIMIT 5;"

# Session içeriğini oku
sqlite3 ~/.hermes/state.db "SELECT m.role, substr(m.content,1,300) 
FROM messages m WHERE m.session_id='SESSION_ID' ORDER BY m.id;"
```

**4. Bulunan session'ı session_search ile session_id'den oku:**
```
session_search(session_id="BULUNAN_ID")
```

**5. Eğer önemli bir konuşma sürekli bulunamıyorsa → session-index.md'ye ekle.**

#### Known Affected Sessions

| Session | Tarih | Mesaj | Sebep |
|---------|-------|-------|-------|
| `20260711_123750_3bff2c24` (sohbethakkındahersey11T) | 11 Tem 2026 | 46 | Kimlik/lokal PC planı. FTS5'te "karanlık" var (5 satır), "kimlik" (329 satır) ama uzun sorgularla bulunamadı. `karanlık` tek başına çalışır. |

Veri kaybı DEĞİL, arama sınırlaması — tüm session'lar state.db'de sağlam.

### FTS5 Trigram Architecture (23 Tem 2026)

state.db'de iki FTS5 tablosu var, biri kullanilmiyor:

| Tablo | Tokenizer | Satir | Kullanim |
|-------|-----------|-------|----------|
| messages_fts | unicode61 | ~45K | session_search'un kullandigi |
| messages_fts_trigram | trigram | ~45K | VAR AMA KULLANILMIYOR |

#### wiki_fts_trigram — Cozum (24 Tem 2026)

`session_search` tool'unu degistiremem ama **wiki_fts** icin trigram index olusturdum:

```bash
# state.db'de olusturulan tablo (872 wiki dosyasi):
python3 ~/.hermes/scripts/wiki_trigram_reindex.py
# 872 dosya indeklendi, 0 hata (24 Tem 2026)
```

**Turkce kok bulma basarimi karsilastirmasi (wiki_fts vs wiki_fts_trigram):**

| Kelime | unicode61 | trigram | Fark |
|--------|:--------:|:-------:|:----:|
| arastirma | 51 | **89** | **+%75** |
| degerlendirme | 23 | **42** | **+%83** |
| basvuru | 6 | **14** | **+%133** |
| konustuk | **0** | **1** | unicode61 bulamadi |
| klinik | 40 | **42** | +%5 |
| calisiyor | 26 | **28** | +%8 |

**Script:** `~/.hermes/scripts/wiki_trigram_reindex.py` — 872 .md dosyayi okur, her birini trigram ile indeksler.
**Cron:** `📚 Wiki Trigram Reindex (Gunluk)` — her gece 02:30'da calisir.
**Sinirlama:** Trigram minimum 3 karakter. 2 harfli sorgular dogrudan calismaz.

### Okuma Hiyerarsisi - Pratik Kullanim

6-katmanli okuma hiyerarsisinde NotebookLM teoride var ama pratikte sorgulanmaz:

| Katman | Kullanim | Gecikme |
|--------|----------|---------|
| MEMORY.md + USER.md | Her tur injekte edilir | ~5ms |
| session_search | Sik kullanilir | ~50ms |
| Skills | Skill eslesirse yuklenir | ~100ms |
| wiki_fts / wiki_fts_trigram | Ara sira | ~10ms |
| NotebookLM | NEREDEYSE HIC KULLANILMAZ | 10-30s |

NotebookLM Layer 6 Gap: 10-30s gecikme (auth stabil — 23 Tem 2026 itibariyle duzgun calisiyor, Edel teyit etti). Wiki'ye yazilan bilgi NotebookLM'de de var diye varsayma. wiki_fts'yi guclu tutmak trigram'dan daha kritik. Edel onceligi: USER.md/MEMORY.md duzeltmeleri > trigram > NotebookLM aktarimi (rafa kalkti — extra is, anlik fayda yok).

### Oncelik (24 Tem 2026 — Edel duzeltmesiyle revize)

1. **USER.md limit artisi + MEMORY.md auto-archive canlandirma** (en acil — USER.md %99 dolu, auto-archive calismiyor) ✅ COZULDU
2. **Trigram gecisi** (en yuksek kazanc — wiki_fts_trigram + cron ile cozuldu) ✅ COZULDU
3. **Session retention: SILME — OPTIMIZE ET.** 1.741 session veri hazinesidir. Edel: *"sohbetlerde yazdigim mesajlar, alinan kararlar onemli bilgiler barindirir, silinmesi kendi gecmisini tutmak gibi."* Cozum: state.db incremental backup (SQL dump + gzip → GitHub), asla delete degil. ✅ COZULDU

## Sıkıştırma Davranışını Değiştirme

Eğer threshold veya diğer compression ayarlarını değiştirmek gerekirse,
Hermes yapılandırma dosyasında (`config.yaml`) şu değerler var:

- **threshold:** Context % kaçta sıkıştırma düşünülsün (0.2 = %20)
- **target_ratio:** Sıkıştırma sonrası hedef context oranı
- **protect_last_n:** Kaç mesaj sonuna kadar korunsun
- **protect_first_n:** Kaç mesaj başından korunsun (system prompt dahil)
- **hygiene_hard_message_limit:** Maksimum mesaj sınırı
