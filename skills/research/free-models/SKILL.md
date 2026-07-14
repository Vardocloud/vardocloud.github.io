---
name: free-models
description: "Free model kataloğu (LiteRouter + NVIDIA + diğer), TR/EN seçim stratejisi, konuşma değerlendirme pipeline'ı"
metadata:
  hermes:
    tags: [models, lite-router, nvidia, free, evaluation, strategy]
    category: research
---

# Free Models — Araç Kutusu & Strateji

**Amaç:** Kullanılabilir free provider'lar ve modellerin yeteneklerini, hangi işlerde kullanılacağını ve seçim stratejisini tanımlar. Her provider'ın durumu değişebilir — test etmeden kabul etme.

## 🚨 Güncel Durum (13 Tem 2026)

| Provider | Durum | Açıklama |
|----------|-------|----------|
| **LiteRouter** | ✅ Çalışıyor | deepseek-v3.2:free Türkçe'de en iyisi |
| **NVIDIA (build.nvidia.com)** | ✅ Çalışıyor | minimaxai/minimax-m3 Türkçe LinkedIn için en iyisi (TEST EDİLDİ) |
| **opencode-zen** | ❌ Bozuk | deepseek-v4-flash-free content boş döndürür, reasoning token var ama çıktı yok |
| **Pollinations** | ❌ Terk edildi | [14 Tem 2026] Para yüklemeden çalışmıyor. Tüm referanslar temizlendi |

**Önemli:** Provider durumları değişir. Cron job atamadan önce test et.

## 🎯 Dil Bilincine Göre Model Seçimi

### ✅ Türkçesi Kanıtlanmış
| Model | Provider | Kullanım |
|-------|----------|----------|
| `deepseek-v3.2:free` | LiteRouter | Her şey — sohbet, post, analiz, email, değerlendirme |
| `minimaxai/minimax-m3` | NVIDIA | **LinkedIn post, psikoloji içerik, Türkçe metin üretimi — EN İYİSİ (TEST EDİLDİ)** |
| `gemma-3-27b:free` | LiteRouter | Çeviri, çok dilli içerik, görsel+metin |

### ⚠️ Dili Bilinmiyor (Test Gerek)
| Model | Provider | Kullanım | Not |
|-------|----------|----------|-----|
| `grok-4.1-fast-reasoning:free` | LiteRouter | EN data analizi, uzun doküman (2M context), kod | |
| `mistral-small-24b-2501:free` | LiteRouter | Hızlı EN işlem (150 t/s), API çağrıları | |
| `mistralai/mistral-nemotron` | NVIDIA | LinkedIn/post adayı | Basit TR testi geçer ama Edel kaliteyi beğenmedi |

### ❌ İngilizce Odaklı (EN İşler)
| Model | Provider | Kullanım |
|-------|----------|----------|
| `gpt-oss-120b:free` | LiteRouter | EN araştırma, reasoning, JSON çıktı |
| `llama-3.3-70b-turbo:free` | LiteRouter | Structured JSON (%0 hata) |
| `devstral-small-2507:free` | LiteRouter | EN kodlama (SWE-Bench %53.6) |
| `mistralai/mixtral-8x7b-instruct-v0.1` | NVIDIA | EN metin, basic TR (TEST EDİLDİ) |
| `meta/llama-3.1-8b-instruct` | NVIDIA | Küçük/EN, TR basic selamlaşma (TEST EDİLDİ) |
| `google/gemma-2-2b-it` | NVIDIA | Çok küçük, basic TR (TEST EDİLDİ) |

## 🧪 Model Test Metodolojisi

Free model atamadan önce mutlaka DOĞRUDAN API testi yap:

1. **API'yi belirle:** Provider'ın base_url + auth header'ını bul (config.yaml veya .env)
2. **Model adını bul:** Provider'ın catalog/list endpoint'inden
3. **Türkçe test prompt'u gönder:** curl ile API endpoint'ine POST, model adı ve mesaj ile. max_tokens=50 yeterli.
4. **Kontrol et:** HTTP 200 + content dolu mu? Yoksa reasoning token var ama content boş mu? (opencode-zen hatası)
5. **LinkedIn/post testi:** Basit merhaba çalışsa bile complex prompt'ta boş dönebilir (step-3.7-flash). Gerçek kullanım senaryosuna yakın prompt ile tekrar test et.
6. **Timeout kontrolü:** 15-20sn'den uzun süren modeller cron için uygun değil.
7. **Toplu karşılaştırma:** En iyi modeli bulmak için aynı prompt'u 5-10 modelde dene, çıktıları yan yana karşılaştır. Tek model test edip "bu iyi" deme — en iyisini bulana kadar dene.
8. **Prompt kalitesi testi:** LinkedIn/post gibi gerçekçi bir prompt kullan (2-3 cümle, konu belirt, ton belirt). Sadece "merhaba de" testi aldatıcı olabilir.

### 🧠 Model Seçim Kriterleri (Auxiliary Task'lar İçin)

Bir modeli auxiliary task'a atarken şu kriterleri sırayla değerlendir:

| # | Kriter | Soru |
|---|--------|------|
| 1 | **Dil kalitesi** | Modelin o dilde (TR/EN) kanıtlanmış performansı var mı? Benchmark yetmez — gerçek promptla test et. |
| 2 | **Görev-model eşleşmesi** | Görevin gerektirdiği yetenek modele göre çok mu büyük/küçük? Decomposition gibi hafif işe 284B model koyma. |
| 3 | **Provider stabilitesi** | Free tier çalışıyor mu? Timeout vermiyor mu? Rate limit yeterli mi? |
| 4 | **Multimodal gerekli mi?** | Göreve görsel/video gidiyor mu? Gitmiyorsa text-only daha hızlı ve ucuz. |
| 5 | **Lisans** | MIT > Modified-MIT > kapalı. Ticari kullanım kısıtlaması var mı? |
| 6 | **Output format** | JSON gerekiyorsa structured output desteği gerek. |
| 7 | **Maliyet** | Free tier yeterli mi? Token başı ücret uygun mu? |

**Kritik hata (yapma):** Sadece benchmark'a bakıp model seçme. Gerçek görevde test etmeden atama yapma. Dil kalitesi her şeyden önce gelir — kullanıcının dilinde iyi olmayan bir model ne kadar güçlü olursa olsun kullanıcı beğenmez.

1. **API'yi belirle:** Provider'ın base_url + auth header'ını bul (config.yaml veya .env)
2. **Model adını bul:** Provider'ın catalog/list endpoint'inden
3. **Türkçe test prompt'u gönder:** curl ile API endpoint'ine POST, model adı ve mesaj ile. max_tokens=50 yeterli.
4. **Kontrol et:** HTTP 200 + content dolu mu? Yoksa reasoning token var ama content boş mu? (opencode-zen hatası)
5. **LinkedIn/post testi:** Basit merhaba çalışsa bile complex prompt'ta boş dönebilir (step-3.7-flash). Gerçek kullanım senaryosuna yakın prompt ile tekrar test et.
6. **Timeout kontrolü:** 15-20sn'den uzun süren modeller cron için uygun değil.
7. **Toplu karşılaştırma:** En iyi modeli bulmak için aynı prompt'u 5-10 modelde dene, çıktıları yan yana karşılaştır. Tek model test edip "bu iyi" deme — en iyisini bulana kadar dene.
8. **Prompt kalitesi testi:** LinkedIn/post gibi gerçekçi bir prompt kullan (2-3 cümle, konu belirt, ton belirt). Sadece "merhaba de" testi aldatıcı olabilir.

## 📦 Cron Job Model Atama

### LiteRouter
```python
cronjob(action='update', job_id='JOB_ID',
    model={'provider': 'LiteRouter', 'model': 'deepseek-v3.2'})
```

### NVIDIA
Test edilmiş modeller:

| Model | Türkçe Kalitesi | Durum | Not |
|-------|-----------------|-------|-----|
| `minimaxai/minimax-m3` | ⭐ En iyi | ✅ Kullan | LinkedIn/post için en doğal |
| `mistralai/ministral-14b-instruct-2512` | ✅ İyi | ✅ Yedek | |
| `meta/llama-3.3-70b-instruct` | ✅ İyi | ✅ Kullanılabilir | Config'de `nvidia-llama-3.3-70b` alias'ı ile map'li. Çalışıyor (bazen yavaş yanıt) |
| `mistralai/mixtral-8x7b-instruct-v0.1` | ⚠️ Karışık | ⚠️ Dene | Gramer hataları olabiliyor |
| `meta/llama-3.1-8b-instruct` | ✅ Basic TR | ✅ Yedek | |
| `google/gemma-2-2b-it` | ✅ Basit | ✅ Küçük işler | |
| `mistralai/mistral-nemotron` | ❌ Edel beğenmedi | ❌ Kullanma | |
| `stepfun-ai/step-3.7-flash` | ❌ Boş döner | ❌ Kullanma | Complex prompt'ta content=null |

```python
cronjob(action='update', job_id='JOB_ID',
    model={'provider': 'NVIDIA', 'model': 'minimaxai/minimax-m3'})
```

**Not:** Model adı config.yaml'daki mapping'de yoksa Hermes passthrough yapar — API'ye olduğu gibi gönderilir.

### Kullanım Senaryoları
| İş | Önerilen Model | Provider | Gerekçe |
|----|---------------|----------|---------|
| LinkedIn post (Türkçe) | `minimaxai/minimax-m3` | NVIDIA | TEST EDİLDİ: en doğal, samimi, profesyonel TR çıktı |
| Gmail okuma/kontrol | `deepseek-v3.2` | LiteRouter | Türkçe mail için kanıtlanmış |
| Günlük sentez/özet | `deepseek-v3.2` | LiteRouter | Uzun context, TR+EN karışımı |
| JSON çıktı gerektiren | `llama-3.3-70b` | LiteRouter | Structured JSON %0 hata |
| Hızlı EN işlem | `mistral-small` | LiteRouter | 150 t/s |

## ⚙️ API Key Yönetimi

### LiteRouter
- Key: Bitwarden secret'dan alınır, `/tmp/.or_key`'e yazılır (chmod 600)
- `/tmp` ephemeral — reboot'ta silinir. Bitwarden'dan yeniden çek.
- **User-Agent zorunlu:** API 403 dönerse, `'User-Agent': 'Vanitas/1.0'` header'ını ekle
- **Endpoint:** `https://api.literouter.com/v1/chat/completions`
- **Model adı:** `deepseek-v3.2:free` değil, **sadece `deepseek-v3.2`** kullan

### NVIDIA
- Key: `.env` dosyasında `NVIDIA_API_KEY` env var'ında tutulur
- **Endpoint:** `https://integrate.api.nvidia.com/v1`
- **Catalog:** `curl -s https://integrate.api.nvidia.com/v1/models` ile 121+ model listelenir
- **Config alias ekleme:** config.yaml'da NVIDIA provider'ının `models:` listesine `minimax-m3: minimaxai/minimax-m3` gibi satır eklenir
- **Bilinen çalışan free modeller:**
  - `minimaxai/minimax-m3` — Türkçe en iyisi (TEST EDİLDİ: HTTP 200, stop)
  - `mistralai/ministral-14b-instruct-2512` — Türkçe iyi (TEST EDİLDİ)
  - `mistralai/mixtral-8x7b-instruct-v0.1` — Basic TR (TEST EDİLDİ)
  - `meta/llama-3.1-8b-instruct` — Basic TR (TEST EDİLDİ)
  - `google/gemma-2-2b-it` — Minimal TR (TEST EDİLDİ)
- **Bilinen çalışmayan:**
  - `stepfun-ai/step-3.5-flash` — content=null
  - `stepfun-ai/step-3.7-flash` — Basic test geçer ama complex prompt'ta null
  - `google/gemma-3-4b-it` — 404
  - `moonshotai/kimi-k2.6`, `01-ai/yi-large`, `writer/palmyra-creative-122b`, `ibm/granite-3.0-8b-instruct` — 404
- **Katalogda var, completion test edilmedi:**
  - `deepseek-ai/deepseek-v4-flash` — NVIDIA free tier kataloğunda mevcut. Decomposition (text-only) için ideal aday: MIT lisansı, 13B aktif, güçlü reasoning. Completion testi yapılıp doğrulanmalı. Önceki test "503 ResourceExhausted" dönmüştü — free tier kotası dolmuş olabilir. Farklı zamanda tekrar dene.
  - `deepseek-ai/deepseek-v4-pro` — NVIDIA kataloğunda var, muhtemelen ücretli.
- **Timeout veren (ücretli/kısıtlı olabilir):**
  - `meta/llama-3.1-70b-instruct`, `meta/llama-4-maverick-17b-128e-instruct`
  - `qwen/qwen3-next-80b-a3b-instruct`, `qwen/qwen3.5-122b-a10b`
  - `microsoft/phi-4-mini-instruct`, `google/gemma-4-31b-it`
  - `z-ai/glm-5.2`

## 🚨 Pitfall'lar

1. **opencode-zen content boş döner** — HTTP 200 alırsın, reasoning_content dolu gelir ama content="" olur. Bu model ölü demo. Kullanma.
2. **Step 3.7 Flash tuzağı** — Basit "Merhaba" testinde çalışır ama complex LinkedIn prompt'ta content=null döner. Basit test yetmez, gerçek prompt ile test et.
3. **Pollinations terk edildi** — [14 Tem 2026] Tüm kullanım durduruldu. Image generation boşluğu için Segmind veya OpenRouter Gemini image modellerine geçildi.
4. **NVIDIA model adları case-sensitive** — API'deki tam adı kullan. Catalog'dan birebir kopyala.
5. **Cron job model passthrough** — Mapping'de olmayan model adları passthrough edilir. API'nin kabul edip etmediğini test et.
6. **API key redaction Python syntax hatası** — `write_file` veya `terminal` ile Python script'i yazarken `auth = "Authorization: Bearer " + key` şeklinde yaz. `"Authorization: Bearer ***"` yazarsan güvenlik sistemi key'i `***` ile değiştirir ve Python syntax hatası alırsın. Çözüm: string parçalarını ayır — concat et.
7. **Timeout olan modelleri cron'a koyma** — 15-20sn'den uzun süren modeller cron için uygun değil. Agent loop'u bloke eder.

## 🖼️ Image Generation Provider Durumu (14 Tem 2026)

Pollinations terk edildi. Şu an çalışan ücretsiz image generation API key'imiz yok. Detaylı test sonuçları: `references/image-generation-providers.md`

**Önerilen çözüm:** Segmind (100 image/gün ücretsiz) veya OpenRouter Gemini image modelleri ($0.00000025/prompt). LinkedIn görselleri için Unsplash RSS de geçici çözüm.

| Sağlayıcı | Görsel Üretim | Vision | Not |
|-----------|--------------|--------|-----|
| **Segmind** | ✅ 100/gün ücretsiz | ❌ | Kaydolmak gerek |
| **OpenRouter Gemini** | ✅ Ücretli (çok ucuz) | ✅ | Kredi yüklemek gerek |
| **HuggingFace** | ❌ DNS hatası | ❌ | Docker/WSL erişemiyor |
| **Groq** | ❌ | ✅ Vision var | Zaten kullanılıyor |

## 📁 Referans Dosyaları
- `references/image-generation-providers.md` — Pollinations sonrası test edilen tüm sağlayıcılar ve durumları
- `references/nvidia-free-models.md` — NVIDIA API test sonuçları (hangi modeller çalıştı, HTTP kodları, Türkçe kalitesi)
- `sohbet/references/literouter-free-model-rehberi.md` — LiteRouter 19 model detayı
- `sohbet/references/konusma-degerlendirme-prompt.md` — Değerlendirme prompt şablonu
- `sohbet/references/ogrenme.md` — Günlük öğrenme/rapor kaydı
- `references/model-senaryolar.md` — Model-senaryo eşleştirmeleri
- `references/en-arac-kutusu.md` — EN işler için araç kutusu detayı
