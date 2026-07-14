# DeepSeek Prompt Caching — Test Data (Jul 2026)

## Test Environment

- **Provider proxy:** opencode-go (OpenAI-compatible, local)
- **Model:** deepseek-v4-flash
- **Method:** Two consecutive requests with identical system prompt, different user messages
- **Cache TTL:** 5 minutes (config: `prompt_caching.cache_ttl: 5m`)

## Results

### Test A: Stable System Prompt (no timestamp)

| Request | cache_hit | cache_miss | total_prompt | Hit Ratio |
|---------|-----------|------------|-------------|-----------|
| 1 (cold) | 0 | 180 | 180 | 0% |
| 2 (warm) | 128 | 46 | 174 | **71%** |

Cache worked. 128 of 180 system prompt tokens served from cache on second request.

### Test B: Variable Timestamp at Prefix Start

| Request | cache_hit | cache_miss | total_prompt | Hit Ratio |
|---------|-----------|------------|-------------|-----------|
| 1 (ts=14:30) | 0 | 165 | 165 | 0% |
| 2 (ts=14:31) | 0 | 165 | 165 | **0%** |

Timestamp changed by 1 minute between requests. Both requests were cache misses — the variable prefix completely disabled caching.

## Conclusions

1. DeepSeek caching is **strictly prefix-based** and byte-exact
2. Any variable content at position 0 kills all caching
3. Stable prefix → ~70% cache hit achievable
4. ~90% token cost savings on cache hits ($0.014 vs $0.14/M tokens)
5. `prompt_cache_hit_tokens` in API `usage` reliably reports cache status

## Reference: DeepSeek Pricing

- Cache hit: $0.014 / 1M tokens
- Cache miss: $0.14 / 1M tokens
- 64-token minimum for cache eligibility
- Disk-based caching (first among major providers)
