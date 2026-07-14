# LiteRouter Free Modeller — Vanitas Kullanım Rehberi

> Oluşturma: 20 Haziran 2026
> LiteRouter API: https://api.literouter.com/v1 (OpenAI-compatible)
> API Key: /tmp/.or_key (Bitwarden secret ID'den alınır)
> Free modeller: `model-adı:free` suffix ile

## ⚠️ Dil Uyarısı (KRİTİK)
Çoğu modelin **Türkçe desteği kanıtlanmamıştır**. Sadece aşağıda ✅ ile işaretlenen modeller Türkçe görevlerde kullanılabilir. Diğerleri İngilizce görevler içindir (kod, araştırma, data analizi, yaratıcı yazarlık).

---

## Türkçe İşler İçin Uygun Modeller

| Model | Türkçe | JSON | İçerik | En İyi Kullanım |
|---|---|---|---|---|
| deepseek-v3.2:free | ✅ Kanıtlı | ✅ Resmi | ✅ Dolu | Sohbet değerlendirme, post yazımı, analiz, email |
| gemma-3-27b-it:free | ✅ 140 dil var | ✅ Structured output | ✅ Dolu | Çeviri, çok dilli içerik, multimodal (görsel+metin) |
| llama-3.3-70b-instruct-turbo:free | ❓ Test gerek | ✅ %0 hata | ✅ Dolu | Structured JSON (en düşük hata oranı) |

## İngilizce Görevler İçin

| Model | Boyut | JSON | En İyi Kullanım | Referans |
|---|---|---|---|---|
| grok-4.1-fast-reasoning:free | ? (xAI) | ✅ Structured Outputs | **2M context** ile dev doküman işleme, çok adımlı ajan | [xAI docs](https://docs.x.ai/developers/model-capabilities/text/structured-outputs) |
| gpt-oss-120b:free | 117B MoE | ✅ Native (en düşük hata) | Derin araştırma, structured JSON, o4-mini seviyesi | [OpenAI](https://openai.com/index/introducing-gpt-oss/) |
| owl-alpha:free:full-context | ? | ✅ %0.34 hata | **1M context**, agentic, Claude Code uyumlu | [OpenRouter](https://openrouter.ai/openrouter/owl-alpha) |
| mistral-small-24b-2501:free | 24B | ⚠️ Tool calling ile | **150 t/s** hızlı API, instruction following | [Mistral](https://mistral.ai/news/mistral-small-3/) |
| devstral-small-2507:free | 24B | ❌ | Agentic coding (SWE-Bench %53.6) | [Mistral](https://mistral.ai/news/devstral-2507/) |
| trinity-mini:free | 26B MoE | ✅ Structured output | ABD yapımı, function calling, GDPR uyumlu | [Arcee](https://www.arcee.ai/trinity) |
| mistral-nemo-2407:free | 12B | ⚠️ | Çok dilli test, Nvidia destekli | [HuggingFace](https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407) |
| mythomax-l2-13b:free | 13B | ❌ | **Roleplay #1**, hikaye, NPC diyalogu | [OpenRouter](https://openrouter.ai/gryphe/mythomax-l2-13b) |
| l3-8b-lunaris:free | 8B | ⚠️ | Generalist + roleplay, yaratıcı yazarlık | [OpenRouter](https://openrouter.ai/sao10k/l3-lunaris-8b/api) |
| gpt-oss-20b:free | 21B MoE | ⚠️ | Edge cihaz (16GB), o3-mini seviyesi | [OpenRouter](https://openrouter.ai/openai/gpt-oss-20b/pricing) |
| ministral-3b-2512:free | 3B | ❌ | En küçük, vision, mobil cihaz | [Mistral](https://mistral.ai/news/mistral-3/) |
| llama-3.2-3b-instruct:free | 3B | ❌ | En küçük Llama, 8 dil | [OpenRouter](https://openrouter.ai/meta-llama/llama-3.2-3b-instruct) |

## Uncensored Modeller
Bu modellerde "Uncensored" etiketi var — kısıtlama yok:
- devstral-small-2507:free — Uncensored, coding
- llama-3-8b-instruct:free — Uncensored
- llama-3.1-8b-instruct:free — Uncensored
- llama-3.1-8b-instruct-turbo:free — Uncensored

## Full-Context Modeller
- openrouter:free:full-context — 25 free model arasında akıllı routing, hangi modelin iyi olduğu bilinmiyorsa kullanılır
- owl-alpha:free:full-context — 1M context ile kesintisiz ajan görevleri

## Vanitas Görevlerine Eşleştirme

### Türkçe Gereken İşler
| Görev | Model | Gerekçe |
|---|---|---|
| Sohbet değerlendirme | deepseek-v3.2:free | Kanıtlı Türkçe, JSON mode |
| LinkedIn post (Türkçe) | deepseek-v3.2:free | Uzun form, APA uyumlu |
| Not alma / wiki | gemma-3-27b:free | 140 dil, geniş bilgi |
| Çeviri | gemma-3-27b:free | 140 dil desteği |
| Email yazma | deepseek-v3.2:free | Yapısal metin, Türkçe |

### İngilizce Yapılabilecek İşler
| Görev | Model | Gerekçe |
|---|---|---|
| Kod / teknik | devstral-small-2507 | SWE-Bench %53.6 |
| Uzun doküman analizi | grok-4.1-fast-reasoning | 2M context |
| Agentic işler | owl-alpha | 1M context, tool use |
| Derin araştırma | gpt-oss-120b | o4-mini seviyesi |
| Yaratıcı yazarlık | mythomax/l3-lunaris | Roleplay odaklı |
| Hızlı API işlemleri | mistral-small-24b | 150 t/s |
| Structured JSON (kritik) | llama-3.3-70b-turbo | %0 hata oranı |
| GDPR uyumlu | trinity-mini | ABD yapımı |
