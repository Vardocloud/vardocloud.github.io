# Delegate Task Subagent Mimarisi ve Validation Açıkları

> Kaynak: Hermes Agent v0.16.0 | tools/delegate_tool.py (2829 satır) | 2 Temmuz 2026

---

## 1. Sistem Genel Bakış

`delegate_task`, parent AIAgent'in child AIAgent (subagent) spawn etmesini sağlar.
Her child: izole bağlam, kendi terminal session'ı, kısıtlı toolset alır.
Parent sadece özet sonuç görür — ara tool call'ları parent'a ulaşmaz.

**İki mod:**
- Single: `goal` + opsiyonel `context`, `toolsets`
- Batch: `tasks` array'i ile paralel (default max 3 concurrent child, configurable)

---

## 2. OpenAI Function-Calling Schema (JSON)

```python
DELEGATE_TASK_SCHEMA = {
    "name": "delegate_task",
    "parameters": {
        "type": "object",
        "properties": {
            "goal":        {"type": "string"},
            "context":     {"type": "string"},
            "toolsets":    {"type": "array", "items": {"type": "string"}},
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "goal":     {"type": "string"},
                        "context":  {"type": "string"},
                        "toolsets": {"type": "array"},
                        "role":     {"type": "string", "enum": ["leaf", "orchestrator"]}
                    },
                    "required": ["goal"]
                }
            },
            "role":        {"type": "string", "enum": ["leaf", "orchestrator"]},
            "acp_command": {"type": "string"},
            "acp_args":    {"type": "array"}
        },
        "required": []
    }
}
```

⚠️ `description` alanları her `get_definitions()` çağrısında dinamik yeniden yazılır (`_build_dynamic_schema_overrides`).

---

## 3. Güvenlik — Blocked Tools

Subagent'ların asla erişemeyeceği tool'lar (sabit):

```python
DELEGATE_BLOCKED_TOOLS = frozenset([
    "delegate_task",   # recursive yok (leaf'lerde)
    "clarify",         # kullanıcı etkileşimi yok
    "memory",          # shared MEMORY.md'ye yazma yok
    "send_message",    # cross-platform yan etki yok
    "execute_code",    # child adım adım reasoning yapmalı
])
```

Orchestrator role'ü `delegate_task`'i korur (config'de max_spawn_depth >= 2 ise).

---

## 4. Child Agent Oluşturma

_Agent'in aldığı system prompt özeti:_

```
You are a focused subagent working on a specific delegated task.

YOUR TASK: {goal}

CONTEXT: {context}

Complete this task using the tools available to you.
When finished, provide a clear, concise summary of:
- What you did
- What you found or accomplished
- Any files you created or modified
- Any issues encountered
```

**Önemli child parametreleri:**
- `skip_memory=True` — parent'ın memory'sine erişemez
- `skip_context_files=True` — context dosyalarını okumaz
- `quiet_mode=True` — kendi çıktısını bastırır
- `skip_memory=True` — memory entegrasyonu kapalı
- Credential override: farklı provider/model kullanılabilir
- Parent'ın credential pool'u miras alınabilir (rate-limit rotasyonu için)

---

## 5. Çalıştırma Döngüsü

1. **Heartbeat thread** — parent'ın gateway timeout'unu engellemek için her 30sn'de parent activity touch
2. **Hard timeout** — `child_timeout_seconds` (default 600sn = 10dk)
3. **Single task**: direkt `run_conversation`
4. **Batch**: `ThreadPoolExecutor` ile paralel, `wait(FIRST_COMPLETED)` polling
5. **Parent interrupt** kontrolü — her 0.5sn'de kontrol

---

## 6. Çıktı Formatı

```json
{
  "results": [{
    "task_index": 0,
    "status": "completed|failed|interrupted|timeout|error",
    "summary": "Child'ın ürettiği son metin",
    "api_calls": 12,
    "duration_seconds": 45.2,
    "model": "deepseek-v4-flash",
    "exit_reason": "completed|max_iterations|interrupted",
    "tokens": {"input": 12500, "output": 3400},
    "tool_trace": [
      {"tool": "web_search", "args_bytes": 120, "result_bytes": 4500, "status": "ok"}
    ]
  }],
  "total_duration_seconds": 47.1
}
```

---

## 7. Mevcut Validation Durumu

**Şu an hiçbir validation yok.** Sistemin güvenceleri:

| Güvence | Mekanizma |
|---------|-----------|
| Tool bloklama | DELEGATE_BLOCKED_TOOLS ile zararlı işlemler engellenir |
| Depth limit | max_spawn_depth ile sonsuz recursion önlenir |
| Timeout | child_timeout_seconds (default 600s) ile asılı child'lar öldürülür |
| Stale detection | Heartbeat ile takılma tespiti |
| Parent interrupt | Child'lar interrupt sinyali alır |
| File-state uyarısı | Child parent'ın okuduğu dosyayı değiştirirse uyarı |

### Eksik Olan:
- ❌ **JSON schema validation** — subagent çıktısının yapısal doğrulaması yok
- ❌ **Content validation** — subagent çıktısının içerik doğrulaması yok (hallucination detection)
- ❌ **Verifiable handle check** — subagent'ın ürettiği path/URL/ID'lerin otomatik kontrolü yok
- ❌ **Type guarantee** — dönen result'ın tür/içerik garantisi yok (self-report)
- ❌ **Cross-task consistency** — batch task'ler arası veri tutarlılığı kontrolü yok

---

## 8. Config Değişkenleri

| Key (delegation.*) | Default | Açıklama |
|---|---|---|
| `max_concurrent_children` | 3 | Paralel batch limiti |
| `max_iterations` | 50 | Child başına maksimum tool call |
| `max_spawn_depth` | 1 | 0=parent, 1=child (flat), 2+=nested |
| `child_timeout_seconds` | 600 | Hard timeout (saniye) |
| `orchestrator_enabled` | true | Orchestrator role kill switch |
| `subagent_auto_approve` | false | Child için dangerous command auto-approve |
| `provider` | - | Child için farklı provider override |
| `model` | - | Child için farklı model override |
| `reasoning_effort` | - | Child reasoning seviyesi |
| `inherit_mcp_toolsets` | true | Parent MCP toolsets child'a geçer mi |

---

## 9. Supervisor Pattern İçin Değerlendirme

### Önerilen 3 Katmanlı Model

```
Katman 1 — Structured Generation (önleme)
├── Subagent prompt'unda beklenen JSON formatını belirt
├── Outlines/Pydantic ile structured output zorla
└── Maliyet: yok (sadece prompt değişikliği)

Katman 2 — JSON Schema Validation (filtreleme)
├── Dönen çıktıyı Pydantic model ile validate et
├── Tip/format/exists hatalarını yakala
└── Maliyet: ms seviyesi

Katman 3 — Verifiable Handle Check (doğrulama)
├── Kritik alanlar için parent agent tool call
│   (stat → dosya var mı?, curl → API yanıt veriyor mu?)
├── Subagent'ın self-report'unu bağımsız verify et
└── Maliyet: task başına ~2-5sn
```

### Riskler
1. **False sense of security** — JSON schema validation sadece YAPIYI kontrol eder, İÇERİĞİ DEĞİL. "file_created: true" schema'dan geçer ama dosya gerçekte olmayabilir.
2. **Esneklik kaybı** — Her task tipi için ayrı schema tanımı gerekir
3. **Schema drift** — Task'ler evrim geçirdikçe schema'lar güncellenmezse kırılma
4. **Latency + token** — Her delegate_task çağrısında validation ek süre
5. **Validation'ın kendisi hata yapabilir** — LLM-as-Judge kullanılırsa o da hallucinate edebilir

### Uygulama Stratejisi

| Risk Seviyesi | Katman | Örnek Task'ler |
|--------------|--------|----------------|
| Düşük | 1+2 | Bilgi toplama, özet çıkarma |
| Orta | 1+2 + kritik alanlarda 3 | Dosya yazma, veri dönüştürme |
| Yüksek | 1+2+3 (tüm katmanlar) | API çağrısı, production deploy, ücret/puan bilgisi |

---

*Bu doküman 2 Temmuz 2026'da Hermes Agent v0.16.0 kaynak kodundan derlenmiştir.*
