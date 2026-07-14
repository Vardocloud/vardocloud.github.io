# AI Model Marketplace Research — Zenmux / Pollinations / OpenRouter

**Session origin:** 2026-07-11 — Zenmux vision model taraması
**Umbrella skill:** `research-orchestration`

## Overview

When Edel needs to evaluate AI models from marketplace platforms (Zenmux, Pollinations, OpenRouter, LiteRouter), use this methodology to systematically extract model data, filter by criteria, and compare pricing.

## Workflow

### Phase 1: Understand the Platform's Filtering System

Every marketplace has a different layout. Before extracting data:

1. **Check available filters** — Input modality (text/image/audio/video), provider, pricing, context length, reasoning type
2. **Check sort options** — Newest, cheapest, most popular
3. **Check tags** — Free, Discounted, Featured
4. **Note total model count** — e.g. Zenmux shows "169 models" (Text), "14 models" (Image)

### Phase 2: Filter by Target Capability

Target the capability you need first:

- **Vision/image analysis** → filter by `input_modalities=image`
- **Text-only** → filter by `input_modalities=text`
- **Audio/Speech** → filter by modality or supported protocol

**Zenmux URL pattern:**
```
https://zenmux.ai/models?input_modalities=image
https://zenmux.ai/models?input_modalities=text
https://zenmux.ai/models?input_modalities=video
```

### Phase 3: Extract Model Data via Browser + JS Console

The browser snapshot (even in full mode) gets truncated for large pages. Use JS console for structured extraction:

**Step 1 — Get model names:**
```javascript
var h2s = document.querySelectorAll('h2');
var names = Array.from(h2s).map(function(h) { return h.textContent.trim(); });
names.join('\n');
```

**Step 2 — Extract visible page text:**
```javascript
var allText = document.body.innerText;
var lines = allText.split('\n');
// Find the models section and extract
var startIdx = -1;
for (var i = 0; i < lines.length; i++) {
  if (lines[i].trim() === 'Learn More') { startIdx = i + 1; break; }
}
if (startIdx > 0) {
  lines.slice(startIdx, startIdx + 300).join('\n');
}
```

**Step 3 — Parse model cards for pricing:**
Each model card shows:
- **Name + Slug** (e.g. `openai/gpt-5.6-luna`)
- **Token volume** (e.g. `243.72Mtokens`)
- **Description** (capabilities)
- **Input Type** / **Output Type** icons
- **Input $/M tokens** (e.g. `$1-2/M tokens`)
- **Output $/M tokens** (e.g. `$6-9/M tokens`)
- **Context length** (e.g. `1.05M`)
- **Max Output** (e.g. `128.00K`)
- **Providers** count + uptime %
- **Discounts** (e.g. `52% OFF`, `66% OFF`)
- **Free badge** (for free models)

### Phase 4: Filter by Edel's Criteria

Model selection priority order:

1. **Vision/Multimodal capability** — Does it accept image input? Check description for "image", "vision", "multimodal", "visual" keywords
2. **Affordability** — Input price per 1M tokens. Budget range: $0.14-$2.50/M input is "affordable"
3. **Turkish language support** — Search for benchmarks or user reports (Claude: documented multilingual benchmarks; Gemini: 70+ languages; Qwen: tested by user; Doubao/Kimi: need verification)
4. **Context window** — Larger (1M+) is better for complex analysis

**Price tiers:**
| Tier | Input $/M tok | Example | Use case |
|------|--------------|---------|----------|
| 🆓 Free | $0 | Grok 4.5 Free | Testing only (rate limited) |
| 💎 Budget | $0.10-0.50 | Qwen3.7-Plus ($0.14), Gemini 3.1 Flash Lite ($0.25) | Production vision |
| 💰 Mid | $0.50-2.00 | Doubao-Seed ($0.42), Kimi K2.7 Code ($0.43), GPT-5.6 Luna ($1-2) | Quality balance |
| 💵 Premium | $2-10 | Claude Sonnet 5 ($2), GPT-5.6 Terra ($2.5-5) | Best quality |

### Phase 5: Cross-Reference Provider A (Tags) → Provider B (Usage)

Edel's workflow preference:

1. **Use Pollinations for tag/capability checking** — Pollinations API's model list has tags describing model capabilities (vision, text, etc.). No balance needed — just query the model list endpoint
2. **Research on Zenmux** — Once you identify which model has vision capability from tags, look it up on Zenmux for:
   - Exact pricing per 1M tokens
   - Provider availability and uptime
   - Discounts available
3. **Never use Pollinations for actual API calls** if balance is zero — only for discovery

### Phase 6: Compile Comparison Table

Present findings as a compact table sorted by price (cheapest first):

```
| # | Model | Input $/M | Output $/M | Vision Type | Turkish | Context | Notes |
|---|-------|-----------|------------|-------------|---------|---------|-------|
| 1 | **Qwen3.7-Plus** | $0.14 | $0.55 | Image+Video | ⭐⭐⭐ | 1M | 66% OFF |
```

Include: model name, full slug, pricing, vision capability type, Turkish support rating, context window, any discounts, uptime.

## Known Platform Quirks

### Zenmux
- Pagination uses JS state, not URL parameters — navigating to `?page=2` doesn't change content if JS isn't triggered
- Filter by `input_modalities=` URL parameter works server-side
- Model descriptions are truncated in the browser snapshot; use JS `document.body.innerText` for full text
- Some models listed under "Text" also accept image input (like GPT-5.6 series, Claude) — always check descriptions
- "Image" filter shows **image INPUT** models, not just image generation — includes vision analysis models
- Price ranges (e.g. `$1-2/M`) mean the rate varies by provider tier

### Pollinations
- Model list endpoint: `GET https://text.pollinations.ai/models` or through proxy at `GET http://127.0.0.1:19999/v1/models`
- Tags in model metadata describe capabilities (vision, audio, etc.)
- No balance required for listing models

## Candidate Selection Example (2026-07-11 Session)

From Zenmux's image-input filter (14 models):

**Top affordable vision candidates:**
1. **Qwen3.7-Plus** — $0.14/$0.55/M — 66% OFF — multimodal (text+image+video input)
2. **Gemini 3.1 Flash Lite** — $0.25/$1.5/M — vision+text — Turkish ✅
3. **Grok 4.5 Free** — $0/$0 — limited time free — needs Turkish testing
4. **Doubao-Seed-2.1 Pro** — $0.42/$2.11/M — 52% OFF — multimodal
5. **Kimi K2.7 Code** — $0.43/$1.79/M — 55% OFF — multimodal
6. **Claude Sonnet 5** — $2/$10/M — vision+files — Turkish good — best quality
7. **GPT-5.6 Luna** — $1-2/$6-9/M — vision — most affordable OpenAI

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| Browser snapshot truncates model list | Use JS console to extract text content |
| "Image" filter shows both vision ANALYSIS and image GENERATION models | Read description — Nano Banana models are image GEN, Claude/GPT are vision ANALYSIS |
| Price ranges confuse comparison | Use the lower end of ranges for cost estimation |
| Free models have rate limits | Always note rate limiting in recommendations |
| Turkish support not documented on marketplace | Search external benchmarks or test with a Turkish prompt |
| Page 2 button doesn't change URL | JS-based pagination — use browser_click on the button, not URL navigation |
