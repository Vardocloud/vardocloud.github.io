# Delegate Task Model Optimization

**Date:** 2026-05-24
**Context:** Cost-saving strategy for WhatsApp message context analysis

## Pattern

When a cron job or main session needs to process large input (conversation buffers, logs, batch data), use `delegate_task` with a CHEAPER model to analyze, then have the main model only see the structured summary.

### Architecture
```
Large Input (15 messages, ~2000 tokens)
        │
        ▼
┌───────────────────────────────┐
│ delegate_task                  │
│ model: deepseek-flash (cheap) │  ← ~500 token analysis output
│ prompt: "analyze this..."     │
└───────────────┬───────────────┘
                │ JSON summary (~200 tokens)
                ▼
┌───────────────────────────────┐
│ Main model (deepseek-v4-pro)  │  ← only sees summary
│ Decision: ask Edel? add to    │
│ calendar? skip?               │
└───────────────────────────────┘
```

### Cost Comparison
| Approach | Main Model Tokens | Cost |
|----------|-------------------|------|
| Main processes all 2000 tokens | 2000+ | ~0.20 TL |
| delegate_task (flash) + main (summary) | 200 + 500 | ~0.07 TL |
| **Savings** | | **~65%** |

### When to Use
- Conversation context analysis (WhatsApp groups, chat logs)
- Batch document processing
- Log analysis for anomaly detection
- Any task where input >> output

### When NOT to Use
- Single message analysis (overhead > savings)
- Tasks requiring nuanced judgment (use main model)
- When delegate_task latency is unacceptable (adds ~5-10s)

### Model Selection (30 Mayıs 2026 — güncel)

Pollinations üzerinden (proxy ile):
- **Kod/teknik:** `qwen-coder` (0.06/0.22) veya `deepseek` (0.14/0.28)
- **Araştırma/analiz:** `deepseek` (0.14/0.28, 🧠 reasoning)
- **Hızlı/basit:** `openai-fast` (0.05/0.40) veya `nova-fast` (0.035/0.14)
- **Genel/yaratıcı:** `mistral` (0.075/0.20)
- **Ağır reasoning:** `glm` (GLM-5.1, 744B MoE)

Tam katalog: `references/pollinations-model-catalog.md`
