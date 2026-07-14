# Decomposer Model Comparison: DeepSeek V4 Flash vs MiniMax M3

## Session: 14 Tem 2026 — NVIDIA Provider + Auxiliary Gap Doldurma

### Test Setup
- **Gorev:** "BIST analizini guncelle" (Turkish input) → English decomposition
- **System prompt:** `_SYSTEM_PROMPT` from `kanban_decompose.py` with English output requirement added
- **Temperature:** 0.3 (both models)
- **Avatar profiles:** analyst, coder, researcher

### Results

| Kriter | DeepSeek V4 Flash | MiniMax M3 |
|--------|-------------------|------------|
| Task sayisi | 5 | 5 |
| Dil uyumu | English ✅ | English ✅ |
| JSON format | Clean ✅ | Clean ✅ |
| Gecikme | ~100ms (local) | ~3-5s (NVIDIA API) |
| Aktif parametre | 13B (MoE 284B total) | ~50B (est., undisclosed) |
| Maliyet | Ucretsiz (lokal proxy) | $0.60/1M input |
| Lisans | MIT | Modified-MIT |

### DeepSeek V4 Flash Output
1. Fetch and clean BIST 100 data → coder
2. Calculate support and resistance levels → analyst
3. Compute MACD → analyst
4. Compute RSI → analyst
5. [synthesis/report task]

### MiniMax M3 Output
1. Fetch BIST 100 last 30 days of OHLCV data → coder
2. Compute MACD and RSI indicators → analyst (combined)
3. Calculate support and resistance levels → analyst
4. Produce integrated analysis report → analyst

### Verdict: DeepSeek V4 Flash for decomposer

**Why:**
1. **Local proxy** (127.0.0.1:19998) — near-zero latency
2. **13B active params** — proportional to task complexity (decomposition is lightweight)
3. **MIT license** — no restrictions
4. **Both models produced English output** when prompted, quality equivalent
5. **MiniMax M3 overkill** — full 284B+ model for a simple JSON-structured reasoning task

**When to use MiniMax M3 instead:**
- Decomposition needs multimodal input (images/diagrams in task body)
- Coding-heavy task analysis where MiniMax's SWE-Bench advantage matters
