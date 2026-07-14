# OpenRouter Free Model Araştırması — 8 Haziran 2026

**Amaç:** StepFun değerlendirici için OpenRouter'da ücretsiz, Türkçe anlayan ve JSON çıktı verebilen model bulmak.

## Yöntem

1. OpenRouter modeller sayfası: `https://openrouter.ai/models?order=pricing-low-to-high&q=free`
2. "Text output" filtrele (24 model)
3. Her adayı test et: Türkçe prompt → JSON yanıt bekle
4. Benchmark/intelligence skorlarını karşılaştır
5. OpenRouter model sayfasından desteklenen dilleri kontrol et

## Test Sonuçları

| Model ID | Türkçe | JSON Çıktı | Hız | Not |
|----------|--------|-----------|-----|-----|
| `z-ai/glm-4.5-air:free` | ✅ Çalıştı | ✅ Tam JSON | ~26 tok/s | Intelligence 23.2 (en yüksek), agentic index 21.0, tool call error %4.1 |
| `nousresearch/hermes-3-llama-3.1-405b:free` | ⚠️ Testte 429 | ✅ Biliniyor | 🐌 405B | Llama 3.1 tabanlı, çok popüler (rate limit) |
| `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | ⚠️ Testte 429 | ✅ Structured output | Hızlı (24B) | Uncensored — objektif değerlendirme avantajı |
| `nvidia/nemotron-3-super-120b-a12b:free` | ⚠️ Kısmi | ? | 12B aktif | 1M context, MTP |
| `meta-llama/llama-3.3-70b-instruct:free` | ❌ **Türkçe yok** | ✅ tools destekler | ~19 tok/s | Sadece 8 dil (EN/DE/FR/IT/PT/HI/ES/TH) |

## GLM 4.5 Air Detay

- **Provider:** Z.ai (Zhipu AI)
- **Mimari:** MoE (Mixture of Experts)
- **Context:** 131K
- **Thinking mode:** `reasoning.enabled=true` ile kontrol
- **Benchmark:** GPQA Diamond 73.3%, IFBench 37.6%, Tau2-Bench 46.5%
- **Tool calling:** ✅ OpenAI-compatible tools
- **Uptime:** 98.52%
- **Not:** Çin modeli, Türkçe'de beklenenden iyi performans

## LLM Türkçe Desteği — Kılavuz

Model seçerken Türkçe desteğini kontrol etmek için:
1. OpenRouter model sayfasını aç (örn. `https://openrouter.ai/meta-llama/llama-3.3-70b-instruct:free`)
2. "Supported Languages" bölümünü kontrol et
3. Türkçe listede yoksa elenir
4. Genel kural: Çin modelleri (GLM, Qwen) ve OpenAI tabanlı (gpt-oss) genelde Türkçe'de iyidir. Meta/Mistral modelleri Türkçe'de ortalama-altıdır.

## Güncelleme — 11 Haziran 2026

⚠️ **`z-ai/glm-4.5-air:free` ARTIK ÜCRETSİZ DEĞİL.** OpenRouter pricing değişti. Yeni araştırma yapıldı.

### Güncel Durum (11 Haz)

OpenRouter'da 26 ücretsiz model listelendi. Çoğu "Provider returned error" veya 429 rate-limit verdi. **Çalışan sadece 2 model:**

| Model ID | Süre (basit test) | JSON Çıktı | Maliyet | Not |
|----------|------------------|-----------|---------|-----|
| `openai/gpt-oss-120b:free` | **3.9s** ✅ | ✅ Tam JSON | $0 | **ÖNERİLEN** — hızlı, güvenilir, reasoning 43c |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | **80.9s** ❌ | ✅ Tam JSON | $0 | Çok yavaş, 120s timeout riski |

### Detaylı Test (Gerçek Evaluator Yüküyle)

Tam stepfun prompt'u + 3 konuşma + sistem prompt'u ile test:

| Model | Süre | Content | Valid JSON | M/T/A/B/R/D |
|-------|------|---------|-----------|-------------|
| `openai/gpt-oss-120b:free` | **13.7s** | 1212 karakter | ✅ | 1.0/1.0/0.0/1.0/1.0/0.67 |

### Başarısız Adaylar (Rate-limit / Provider Error)

- `qwen/qwen3-coder:free` — 429 / Provider returned error
- `google/gemma-4-26b-a4b-it:free` — Provider returned error
- `meta-llama/llama-3.3-70b-instruct:free` — 429 / Provider returned error
- `nousresearch/hermes-3-llama-3.1-405b:free` — 429 / Provider returned error

### Test Yöntemi (11 Haz)

```python
import json, urllib.request, time
key = open('/tmp/.or_key').read().strip()
body = json.dumps({
    "model": "MODEL_ADI",
    "messages": [
        {"role": "system", "content": "Sadece JSON döndür: {\"test\": \"ok\"}"},
        {"role": "user", "content": "test"}
    ],
    "max_tokens": 200,
    "temperature": 0.0
}).encode()
req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=body,
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "HTTP-Referer": "https://vanitas.ai",
        "X-Title": "Vanitas"
    })
t0 = time.time()
with urllib.request.urlopen(req, timeout=30) as resp:
    result = json.loads(resp.read())
print(f"duration={time.time()-t0:.1f}s content='{result['choices'][0]['message'].get('content','')[:80]}'")
```

### Gelecekte Model Değişikliği Gerekirse

1. `openrouter.ai/api/v1/models`'den free modelleri listele (pricing=0 veya `:free` suffix)
2. Her adayı iki aşamalı test et:
   - **Aşama 1:** Basit Türkçe prompt + JSON beklentisi (30s timeout) → content boş değil mi?
   - **Aşama 2:** Gerçek stepfun prompt'u + 3-5 konuşma (120s timeout) → valid JSON + M/T/A/B/R/D puanları var mı?
3. Reasoning model ise (content=None, reasoning dolu) max_tokens=8000 ile dene
4. Süre 30s+ ise cron timeout riski → elenir. 15s altı idealdir.

## Test Prompt'u

```python
# Basit test — model çalışıyor mu ve Türkçe anlıyor mu?
import urllib.request, json
key = open('/tmp/.or_key').read().strip()
body = json.dumps({
    'model': 'z-ai/glm-4.5-air:free',
    'messages': [{'role': 'user', 'content': 'Sadece 1 kelimeyle yanit ver: merhaba'}],
    'max_tokens': 10
}).encode()
req = urllib.request.Request(
    'https://openrouter.ai/api/v1/chat/completions',
    data=body,
    headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
)
resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read())
print(data['choices'][0]['message']['content'])
```
