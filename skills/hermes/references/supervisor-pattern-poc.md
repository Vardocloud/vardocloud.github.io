# Supervisor Pattern — PoC Findings (3 Temmuz 2026)

> **Context:** AI Automation Society (Skool) post'larından esinlenerek Hermes delegate_task üzerinde test edildi.
> Orijinal kaynak: Nate Herk — "Multi-Agent Pipelines Are Not Just a Trend" / "The Real Shift Is at the Evaluation Layer"

## Core Concept

Güçlü bir model (Supervisor) planlar ve doğrular, ucuz modeller (Executor) yürütür. Supervisor:
- **Hedefler konusunda katı**, implementasyon konusunda esnek
- Çıktıyı JSON schema + quality threshold ile doğrular
- Hata varsa tüm pipeline'ı yeniden başlatmak yerine **spesifik executor'a targeted retry** yapar

## PoC Mimarisi

```
Supervisor (ben/üst model)
  ├── Planlama: task'leri böl, her biri için JSON schema tanımla
  ├── Delegasyon: delegate_task(tasks=[...]) ile paralel sub-agent spawn
  ├── Validasyon: her sub-agent çıktısını schema + keyword + length kontrol
  └── Retry: sadece hatalı sub-task'ı yeniden çalıştır (targeted)
       │
       ▼
3x Executor (north-mini-code-free — cheap model)
  ├── Fable 5 araştırması → 157.9s ✅
  ├── Claude Dispatch araştırması → 200.6s ✅
  └── Printing Press araştırması → 95.3s ✅
```

## PoC Metrikleri

| Metrik | Değer |
|--------|-------|
| Paralel süre (3 task) | 202.8s |
| Sequential tahmini | 453.8s |
| Zaman kazancı | **%55** |
| Pass rate | 3/3 (%100) |
| Retry rate | 0/3 (gerekmedi) |
| Model | north-mini-code-free (cheap) |
| Ortalama task süresi | 151.3s |

## Bulgular

### ✅ Çalışanlar
- **Paralel delegasyon** sequential'e göre %55 daha hızlı
- **Cheap model** (north-mini-code-free) tüm task'larda yeterli kalite üretti
- **JSON schema uyumu** %100 — her sub-agent istenen formatta çıktı verdi
- **İzolasyon** — sub-agent'lar birbirini etkilemeden bağımsız çalıştı
- **Hermes delegate_task** paralel batch modu kusursuz çalıştı

### ⚠️ Eksikler (Supervisor Pattern'in eklemesi gerekenler)
1. **Validation layer MANUEL** — otomatik JSON schema checker yok (Python `jsonschema` kütüphanesi ile yapılabilir)
2. **Retry tetiklenmedi** — tümü başarılı oldu, hata senaryosu test edilemedi (kasıtlı hatalı task planlanmalı)
3. **Cross-task tutarlılık kontrolü yok** — 3 aracın çıktılarını karşılaştırma/imzalama yok
4. **Supervisor planning phase otomatik değil** — task'leri manuel böldüm (LLM tabanlı otomatik bölünebilir)

### 🔧 Sıradaki Adımlar
1. Otomatik JSON schema validator (Python jsonschema ile)
2. Kasıtlı hatalı task ile targeted retry simülasyonu
3. Quality threshold — her çıktıya 0-10 puanlama
4. Supervisor'ın task'leri otomatik bölmesi (LLM planning)

## Supervisor Discipline (Orijinal Kaynaktan)

Supervisor "yardımsever değil, son derece disiplinli" olmalı:
- Improvize etmeye başlarsa tüm pipeline dağılır
- Katı bir validator olarak çalışmalı, "bir başka yaratıcı ajan" olarak değil
- Planlama ve yürütme ayrışması öngörülebilirliği artırır

> "Planner/supervisor senin bağlamın ve çalışma stilinle eğitilmişse maliyet çok düşer."

## İlgili Dosyalar
- `/tmp/hermes-delegation-architecture.md` — Mevcut delegate_task kaynak kodu analizi (2 Tem 2026)
- `/tmp/supervisor-pattern-source.md` — Orijinal Skool post özeti
- `~/wiki/skool/ai-automation-society/2026-07-02-multi-agent-pipelines-supervisor-pattern.md` — Wiki sayfası
