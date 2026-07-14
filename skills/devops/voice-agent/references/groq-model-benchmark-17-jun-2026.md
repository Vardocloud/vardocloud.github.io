# Groq Model Benchmarks — Turkish Voice (17 June 2026)

Test conditions: Istanbul AWS us-east-1, streaming=false unless noted.

## Non-streaming Comparison

| Model | Latency | Turkish Quality | Notes |
|-------|---------|-----------------|-------|
| `meta-llama/llama-4-scout-17b-16e-instruct` | 300-416ms | ✅ Clean, consistent | **Recommended** |
| `llama-3.3-70b-versatile` | 171-216ms | ❌ Mixes Russian/English/German | Rejected — multilingual bleed |
| `llama-3.1-8b-instant` | 202-222ms | ⚠️ Formal, slightly awkward | Backup only |
| `gemma2-9b-it` | 52ms | ❌ Returns "?" | Useless for voice |

## Streaming First-Token

| Model | First Token | 
|-------|------------|
| `meta-llama/llama-4-scout` | 151ms |
| `llama-3.3-70b-versatile` | 112ms |

## Free Alternatives Tested (Non-Groq)

| Provider | Model | Latency | Result |
|----------|-------|---------|--------|
| DeepSeek | `deepseek-chat` | 742ms | ❌ Empty content (format issue) |
| OpenRouter | `google/gemini-2.5-flash:free` | 309ms | ❌ Returns "?" |

## Model Name Pitfalls (Groq)

```python
✅ "meta-llama/llama-4-scout-17b-16e-instruct"  # Correct
❌ "llama-4-scout-17b-16e-instruct"             # 404
❌ "llama4-scout-17b-16e-instruct"              # 404
✅ "llama-3.3-70b-versatile"                    # Valid but multilingual bleed for TR
```

## Conclusion

Groq's free tier with Llama-4-Scout is the best available option for Turkish voice agents as of June 2026. No other free provider comes close in speed + language quality combination.
