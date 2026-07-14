# OpenCode Go Model Benchmark — 2 Haziran 2026

Tam test sonuçları. Tüm modeller aynı prompt ile, WARP SOCKS5 proxy üzerinden test edildi.

## Test 1: 500 token eşik testi

**Prompt (EN):** "What are the top 3 AI safety concerns in 2026? Answer in Turkish, one line each, no explanation."

| # | Model | Content (c) | Reasoning (c) | Finish | Süre |
|---|-------|------------|---------------|--------|------|
| 1 | minimax-m2.7 | 195 ✅ | 0 | stop | ~25s |
| 2 | minimax-m2.5 | 206 ✅ | 0 | stop | ~25s |
| 3 | glm-5.1 | 0 ❌ | 1700 | length | ~30s |
| 4 | glm-5 | 0 ❌ | 1865 | length | ~30s |
| 5 | deepseek-v4-flash | 0 ❌ | 1522 | length | ~25s |
| 6 | deepseek-v4-pro | 0 ❌ | 2014 | length | ~25s |
| 7 | kimi-k2.6 | 1866 spam | 0 | length | ~25s |
| 8 | kimi-k2.5 | 1866 spam | 0 | length | ~25s |
| 9 | qwen3.7-max | HATA | — | — | ~5s |

**Sonuç:** 500 token'da sadece Minimax ailesi (m2.5, m2.7) içerik üretiyor. Diğerleri ya reasoning'e boğuluyor ya da spam.

---

## Test 2: GLM-5.1 kademeli max_tokens eşik testi

**Prompt:** "What are the top 3 AI safety concerns in 2026? Answer in Turkish, one line each."

| max_tokens | Content | Reasoning | Completion Tokens | Finish |
|-----------|---------|-----------|-------------------|--------|
| 300 | 0 ❌ | 1162c | 300 | length |
| 500 | 0 ❌ | 1730c | 500 | length |
| 800 | RATE-LIMIT | — | — | — |
| 1200 | RATE-LIMIT | — | — | — |
| 2000 | RATE-LIMIT | — | — | — |

**Sonuç:** 500 token'da completion token'ların %100'ü reasoning'e gidiyor. En az 2000 token gerek.

---

## Test 3: Kalite benchmark (Türkçe araştırma sorusu, 2000 token)

**Prompt (TR):** "Sen bir iletisim psikolojisi arastirmacisisin. Instagram DM'de 28 yasinda bir kadinla dogal bir sohbet baslatmak isteyen bir kisiye 3 pratik taktik ver..."

| Model | Token | Content (c) | Reasoning | Türkçe Kalitesi |
|-------|-------|------------|-----------|-----------------|
| GPT-5.4-mini | 346 | 1104 | 0 | ⭐⭐⭐ En doğal |
| minimax-m2.7 | 736 | 956 | 0 | ⭐⭐ İyi, yapılandırılmış |
| minimax-m2.5 | 651 | 1049 | 0 | ⭐⭐ İyi |
| GLM-5.1 | HATA | — | — | Rate-limit |

**Sonuç:** GPT-5.4-mini en doğal Türkçe. Minimax modelleri de kabul edilebilir.

---

## Test 4: GLM-5.1 prompt optimizasyonu

**Prompt (TR):** "Istanbulda en iyi 3 kahve mekani? SADECE isimleri yaz."

| Varyant | Content | Reasoning | Değişim |
|---------|---------|-----------|---------|
| Normal + "düşünme" | ✅ 3 mekan | **838c** | — |
| reasoning_effort=low | ✅ 3 mekan | 1262c | +%50 ❌ |
| temperature=1.5 | ✅ 3 mekan | 1296c | +%55 ❌ |

Referans (önceki test, 2000 token, "düşünme" yok): 2883c reasoning.

**Sonuç:** Prompt'a "düşünme, direkt yaz" eklemek reasoning'i 2883 → 838 chars'a düşürdü (%70 azalma). API parametreleri (reasoning_effort, temperature) işe yaramadı.

---

## Test 5: OpenCode Go sağlık (2 Haz 2026)

- Proxy :19998: ✅ 9 model, hepsi listeleniyor
- Proxy :19999: ✅ GPT-5.4-mini, Gemma çalışıyor
- OpenCode config: `compaction: "auto"` → `{"mode": "auto"}` fix uygulandı
- GLM modellerine `temperature: 1.0, timeout: 300000` eklendi
- qwen3.7-max: API düzeyinde bozuk, `'choices'` KeyError
- OpenCode Zen: 0 credentials, API key bekleniyor

---

## Nihai Model Seçimi (2 Haz 2026 — Zen güncellemesi)

| Ajan | Birincil | Yedek | Platform |
|------|----------|-------|----------|
| 🔬 Analist | **mimo-v2.5-free** | nemotron-3-super-free | Zen (opencode.ai, API keysiz) |
| ✍️ Yazar | GPT-5.4-mini | — | Pollinations :19999 |
| 🔧 Kodcu | **minimax-m2.7** | — | OpenCode Go :19998 |
| 📦 Yardımcı | Gemma-4-26B | — | Pollinations :19999 |
| 🧠 Değerlendirici | StepFun 3.7 Flash | — | OpenRouter |

⚠️ **2 Haz 2026 güncelleme:** Zen keşfedildi. Analist Zen'e taşındı — API key gerektirmiyor, MiMo-V2.5 ailesi benchmark lideri.
Kodcu minimax-m2.7 olarak sabit (DeepSeek V4 Pro DEĞİL — Edel düzeltmesi).
