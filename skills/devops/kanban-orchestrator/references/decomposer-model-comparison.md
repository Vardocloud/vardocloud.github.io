# Decomposer Model Comparison: DeepSeek V4 Flash vs MiniMax M3

## Session: 14 Tem 2026 — NVIDIA Provider + Decomposer Atamasi

### Results (real test with `kanban_decompose.py` prompt)

| Kriter | DeepSeek V4 Flash | MiniMax M3 |
|--------|-------------------|------------|
| Task sayisi | 5 | 5 |
| Dil uyumu | English | English |
| JSON format | Clean | Clean |
| Gecikme | ~100ms (local proxy) | ~3-5s (NVIDIA API) |
| Aktif parametre | 13B (MoE 284B total) | undisclosed |
| Maliyet | Ucretsiz (lokal proxy veya NVIDIA free) | NVIDIA free tier |
| Lisans | MIT | Modified-MIT |

### DeepSeek V4 Flash Output
1. Fetch and clean BIST 100 data -> coder
2. Calculate support and resistance levels -> analyst
3. Compute MACD -> analyst
4. Compute RSI -> analyst
5. [synthesis/report task]

### MiniMax M3 Output
1. Fetch BIST 100 last 30 days of OHLCV data -> coder
2. Compute MACD and RSI indicators -> analyst (combined)
3. Calculate support and resistance levels -> analyst
4. Produce integrated analysis report -> analyst

### Verdict: DeepSeek V4 Flash for decomposer

Why:
1. Local proxy (opencode-go) gives near-zero latency
2. 13B active params proportional to decomposition task weight
3. MIT license
4. Both models equivalent on English JSON output quality
5. MiniMax overkill for simple structured reasoning

### NVIDIA Free Tier Limitation (14 Tem 2026)

NVIDIA free tier'da deepseek-ai/deepseek-v4-flash katalogda bulunur ancak:
- Model basina ~48 request limiti vardir (ResourceExhausted: 503)
- Limit dolunca "Worker local total request limit reached (48/48)" hatasi alinir
- Limitin sifirlanma suresi bilinmiyor (24 saat olabilir)
- NVIDIA free tier'da alternatif calisan modeller: meta/llama-3.3-70b-instruct, minimaxai/minimax-m3, z-ai/glm-5.2

**Oneri:** Lokal proxy (opencode-go, 127.0.0.1:19998) uzerinden deepseek-v4-flash kullan — kota yok, gecikme yok, ayni model.

### Access Paths
- **opencode-go (127.0.0.1:19998)** — recommended for decomposer, lower latency, no rate limits
- **custom:NVIDIA (integrate.api.nvidia.com/v1)** — free tier, 40 req/min, model basina ~48 request limit
- **opencode-zen** — deepseek-v4-flash-free, alternatif
