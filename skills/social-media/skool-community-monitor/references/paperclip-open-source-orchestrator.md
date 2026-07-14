# Paperclip — Open-Source AI Company Orchestrator

> **Keşif:** 4 Temmuz 2026 — AI Automation Society (Nate Herk post'u)
> **URL:** Paperclip GitHub — https://github.com/mohammed-bashar/paperclip
> **Durum:** Ücretsiz, açık kaynak (MIT)

## Ne İşe Yarar

Paperclip, birden fazla AI agent'ı tek bir "şirket" yapısında organize eden bir orchestrator'dır. Her agent'ın rolü, bütçesi, skill'leri ve rutini vardır. Bir **CEO agent'ı** tüm worker'ları heartbeat mekanizmasıyla izler.

## Mimari

| Bileşen | Açıklama |
|---------|----------|
| **CEO Agent** | Merkezi yönetici. Worker'ların heartbeat'ini dinler, budget dağıtır, rotasyon yapar |
| **Worker Agent'lar** | Her biri bir role sahip (araştırmacı, yazar, kodcu). Skills + routines ile çalışır |
| **Heartbeat** | Worker'lar periyodik sinyal gönderir. CEO sinyal kesilince müdahale eder |
| **Skills** | Her worker'ın uzmanlık alanı (function calling mantığı) |
| **Routines** | Worker'ların günlük/görev bazlı programı |
| **Budgets** | Her worker'ın token/bütçe limiti. CEO aştığında uyarır veya keser |

## Vanitas'a Uyarlanabilirlik: **uyarlanabilir**

Paperclip'in supervisor/worker pattern'i Vanitas'ın `delegate_task` + supervisor pattern yaklaşımıyla birebir örtüşür:

- **CEO Agent** → Vanitas'ın supervisor/planner ajan rolü
- **Worker Agent'lar** → delegate_task ile spawn edilen subagent'lar
- **Heartbeat** → `kanban_heartbeat` ile aynı mantık (canlılık sinyali)
- **Budgets** → Vanitas'ta `delegation.max_concurrent_children`, timeout ayarları
- **Skills + Routines** → Vanitas'taki skill'lerin görev-zamanlı tetiklenmesi

## Farklar

| Paperclip | Vanitas/Hermes |
|-----------|---------------|
| Kendi agent framework'ü | delegate_task + subagent sistemi |
| CEO heartbeat ile izler | kanban_heartbeat ile izler |
| Skills + routines manuel tanımlı | Skill'ler SKILL.md ile tanımlı, cron ile tetiklenir |
| Budget token bazlı | Timeout + max_concurrent_children ile sınırlı |

## Çıkarım

Paperclip, mevcut supervisor/worker pattern'in daha sofistike bir implementasyonudur. Vanitas bu pattern'i zaten kullanıyor — Paperclip'ten alınacak ana ders heartbeat mekanizmasının daha sıkı uygulanması ve budget/token yönetimidir.

**GitHub:** https://github.com/mohammed-bashar/paperclip
**Lisans:** MIT
**Dil:** Python
**Son commit (keşif tarihi):** 2026-07
