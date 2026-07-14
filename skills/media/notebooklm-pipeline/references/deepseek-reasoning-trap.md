# Deepseek Reasoning Tuzağı — Kanıt ve Çözüm

## Problem

`deepseek-v4-flash-free` (Zen, API keysiz) ve diğer deepseek varyantları `reasoning_content` alanı üretir. Bu alan `max_tokens` limitine DAHİLDİR. Sonuç: model "düşünmek" için tüm token'ları harcayıp boş `content` dönebilir.

## Kanıt (5 Haz 2026)

Aynı prompt, iki modele gönderildi:

```
"Sen bir podcast yapımcısısın. Konu: AI etiği ve psikoloji. 
2 hostlu 5dk podcast planı çıkar. SADECE JSON dön."
```

| Metrik | mimo-v2.5-free | deepseek-v4-flash-free |
|--------|----------------|------------------------|
| finish_reason | length | length |
| reasoning_content | **YOK** | "We are asked to create a podcast plan..." (tüm token'lar burada) |
| content | Temiz JSON ✅ | **BOŞ** ❌ |
| Süre | 9042ms | 7461ms |
| Token israfı | %0 | **%100** |

## Çözüm

**Birincil model: `mimo-v2.5-free`** (Zen, API keysiz)
- 0 reasoning_content
- Tüm token'lar içeriğe gider
- Türkçe'de mükemmel, JSON üretimi temiz
- Latency deepseek ile aynı (~0.4sn basit sorgularda)

**Yedek: `nemotron-3-super-free`** (Zen, API keysiz)
- 0 reasoning_content

**Son çare: `deepseek-v4-flash-free`**
- SADECE system prompt "Kısa cevap ver. Reasoning yapma." ekiyle
- max_tokens ≥ 1500 kullan (reasoning'e gidenleri telafi etmek için)
- content boş dönerse `reasoning_content`'i manuel parse et

## Etkilenen Sistemler

Bu tuzak şu skill'leri etkiler:
- `notebooklm-pipeline` → APA article summarization
- `email-knowledge-pipeline` → Analist email classification
- `vanitas-podcast-fabrikasi` → Aşama 1 içerik planlayıcı

Hepsi `mimo-v2.5-free`'e geçirildi.

## Zen API Ücretsiz Modeller (5 Haz 2026)

| Model | reasoning | Türkçe | API Key |
|-------|-----------|--------|---------|
| mimo-v2.5-free | 0 ✅ | Mükemmel | GEREKMEZ |
| nemotron-3-super-free | 0 ✅ | İyi | GEREKMEZ |
| deepseek-v4-flash-free | VAR ❌ | İyi | GEREKMEZ |
| qwen3.6-plus-free | 0 ✅ | Orta | GEREKMEZ |
| minimax-m3-free | 0 ✅ | İyi | GEREKMEZ |

Endpoint: `https://opencode.ai/zen/v1/chat/completions`
