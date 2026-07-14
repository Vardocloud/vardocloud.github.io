# Turkish Language Model Comparison (Pollinations, 2026-06-16 — UPDATED)

## Real conversation test (2026-06-16, v10.4 voice session)
Test prompt: "Sen Vanitas'sın, Edel'in AI arkadaşı. Doğal, sıcak, samimi Türkçe konuş." + "Bugün çok sıkıldım ya, ne yapsam?"
max_tokens: 60, stream: false

| Model | Quality | Tone | Notes |
|-------|---------|------|-------|
| **`gemma`** | 🏆 BEST | Warm, inviting, conversational | "Hadi gel, modunu değiştirecek bir şeyler yapalım. İstersen film seçelim, istersen biraz dertleşelim..." — invites dialogue, not lists |
| `gpt-5.4-mini` | ✅ Good | Specific, practical | "Canın sıkıldıysa hızlıca şunlardan birini yapalım: 10 dakikalık yürüyüş..." — lists options but naturally |
| `openai` (GPT-OSS 20B) | ✅ Good | Emotional, warm | "Ay çok üzüldüm ya… 😕 Sıkıntı için hızlı 'kıpırdatma' fikri bırakıyorum..." — natural but tends to list |
| `minimax` | ⚠️ OK | Casual | "Ooo, sıkıntı bastı ha! 😄" — good start but cut short, inconsistent |
| `glm` | ❌ BROKEN | Thinks aloud | Outputs internal reasoning: "Kullanıcı bugün çok sıkıldığını söylüyor..." — unusable |

## Ranking (2026-06-16 UPDATE)
1. **`gemma`** 🏆 — Warmest, most conversational. Invites dialogue instead of listing options.
2. **`gpt-5.4-mini`** — Good specific suggestions, natural tone.
3. **`openai` (GPT-OSS)** — Good, emotional, but tends to list options (bullet points).
4. **`minimax`** — Promising start but inconsistent output.
5. **`glm`** — BROKEN: outputs internal reasoning. DO NOT USE.

## Hermes API model routing trap (2026-06-16)
**⚠️ Hermes `/v1/chat/completions` (port 8642) ignores the `model` field.** All requests are routed to Pollinations Mistral regardless of model name. Tested: `openai`, `mimo-v2.5-free`, `gpt-5.4-mini` all returned identical Mistral responses (22,705 tokens). To use specific models, bypass Hermes API and call Pollinations proxy (19999) directly.

## Simple greeting test (2026-06-16)
Test prompt: "Sen Vanitas'sın, Edel'in AI arkadaşı." + "Merhaba, bugün nasılsın?"

### gemma
"Merhaba! İyiyim, teşekkür ederim. Sen nasılsın, günün nasıl geçiyor?"
- Natural "sen," warm, asks follow-up
- **Vanitas identity test:** Maintains personality when prompted

### openai (GPT-OSS 20B)
"İyiyim, sen nasılsın? 😊"
- Natural "sen," short, emoji
- Solid backup

### mistral
"Merhaba! Ben çok iyiyim, teşekkürler. Siz nasılsınız?"
- "Siz" (vous) — FORMAL, wrong for girlfriend persona
- Was the Hermes API default until 2026-06-16
- DO NOT USE for Turkish voice

### glm
"1. **Analyze the Input:** * User says: \"Merhaba...\""
- Thinks in English before responding
- Unusable for chat
