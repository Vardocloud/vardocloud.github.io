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

## Sıkıştırma Davranışını Değiştirme

Eğer threshold veya diğer compression ayarlarını değiştirmek gerekirse,
Hermes yapılandırma dosyasında (`config.yaml`) şu değerler var:

- **threshold:** Context % kaçta sıkıştırma düşünülsün (0.2 = %20)
- **target_ratio:** Sıkıştırma sonrası hedef context oranı
- **protect_last_n:** Kaç mesaj sonuna kadar korunsun
- **protect_first_n:** Kaç mesaj başından korunsun (system prompt dahil)
- **hygiene_hard_message_limit:** Maksimum mesaj sınırı
