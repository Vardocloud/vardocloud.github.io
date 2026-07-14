# Pollinations Model Routing — Delegasyon Stratejisi

**Date:** 30 Mayıs 2026  
**Durum:** Delegasyon proxy üzerinden çalışıyor. Per-task model override yok, tek `delegation.model` config'ten okunuyor.

## Ücretsiz Modeller ve Yetenekleri

| Model | Alias | Güçlü Yönü | Kullanım |
|-------|-------|-----------|----------|
| `deepseek` | deepseek-v4-flash | Reasoning, araştırma, analiz | Varsayılan, genel amaçlı |
| `qwen-coder` | Qwen3-Coder-30B-A3B | Kod yazma, teknik işler | Kod görevleri |
| `mistral` | mistral-small-3.2-24b | Genel amaçlı, çok yönlü | Yaratıcı/metin işleri |
| `openai-fast` | gpt-5-nano | En hızlı, tool calling | Basit/hızlı görevler |

## Routing Stratejisi

Varsayılan model: `deepseek` (en ucuz, en güvenilir)

Görev tipine göre geçici model değişimi:
```bash
# Kod görevi için
hermes config set delegation.model "qwen-coder"
# Araştırma için (varsayılan)
hermes config set delegation.model "deepseek"
# Yaratıcı iş için
hermes config set delegation.model "mistral"
```

## Per-Task Routing (execute_code wrapper)

Hermes delegasyonu per-task model override desteklemediği için, direkt API çağrısı wrapper'ı:
```python
# execute_code içinden, görev tipine göre model seçimi
MODELS = {
    "code": "qwen-coder",
    "research": "deepseek",
    "creative": "mistral",
    "fast": "openai-fast"
}
# Proxy üzerinden çağrı
requests.post("http://127.0.0.1:19999/v1/chat/completions", ...)
```

## PAID Modeller (KULLANMA)
- `gemini`, `gemini-flash-lite-3.1`, `openai-large`, `claude` → pollen yetersiz hatası
