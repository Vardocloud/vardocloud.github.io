# StepFun Değerlendirici — Case Study

## ⚠️ 20 Haz 2026 KRİTİK DERS: Türkçe Kalitesi > Teknik Metrikler

Nemotron-3-nano'nun hallucination rate'i 0.0, content dolu, hızlı — ama **Türkçesi berbattır.** 
"baziliklardir" gibi çıktılar üretir. Değerlendirme scriptinde kullanılamaz.

**Doğru kriter sıralaması:**
1. 🟢 **Türkçe kalitesi** — Birincil. Model anlamlı Türkçe cümle kurabiliyor mu?
2. 🟡 **Content alınabiliyor olması** — İkincil. Boşsa regex ile çıkarılabilir.
3. ⚪ **Hız / Halüsinasyon / Diğer metrikler** — Üçüncül.

**Aktif karar:** `step-3.5-flash:free` (Türkçesi orta, content boş → reasoning_content regex) >
nemotron (Türkçesi berbat, content dolu). **Teknik kolaylık asla dil kalitesinin önüne geçmez.**

## Scenario
`stepfun_evaluator.py` (daily cron job, her gün 10:00, `no_agent=true`) değerlendirir Vanitas sohbet kalitesini. Script:
1. Son 24 saatteki konuşmaları SQLite DB'den çeker
2. Routeway API üzerinden `step-3.5-flash:free` modeline gönderir
3. Dönen JSON değerlendirmeyi `ogrenme.md`'ye ekler ve özeti stdout'a yazar

## History

| Dönem | API | Model | Key Storage |
|-------|-----|-------|-------------|
| Mayıs 2026 | OpenRouter | `openai/gpt-oss-120b:free` | `/tmp/.or_key` |
| Haziran 2026 (erken) | Routeway | `step-3.5-flash:free` | `/tmp/.or_key` |
| Haziran 2026 (orta) | Routeway | `nemotron-3-nano-30b-a3b:free` ❌ (Türkçe berbat) | `/tmp/.or_key` |
| 20 Haz 2026 (güncel) | Routeway | `step-3.5-flash:free` ✅ (reasoning → regex) | `/tmp/.or_key` |

### 🔴 Güncelleme: script`/tmp/.or_key` Resilience Gap (20 Haz 2026)

**Olay:** Routeway'e geçiş sonrası, `/tmp/.or_key` bir sonraki gün kayboldu. Script `[Errno 2] No such file or directory: '/tmp/.or_key'` hatası ile çöktü. Edel raporladı.

**Kök neden:** Docker container'da `/tmp/` kalıcı değil — tmpwatch, reboot veya container restart sonrası silindi. Key re-fetch script'i manuel çalıştırılmadığı için cron sonraki tick'te key'siz kaldı.

**Ders:** `/tmp/.or_key`'e güvenme — script her açılışta key'i kontrol etmeli, yoksa otomatik kurtarma yapmalı (Bitwarden'dan yeniden çek). Skill SKILL.md'ye Pattern C eklendi.

**Çözüm:**
1. Script'e `get_api_key()` fonksiyonu eklendi (Pattern C) — key yoksa Bitwarden'dan fetch
2. Anti-loop mekanizması: kurtarma başarısız olursa 1 saat bekleme
3. Fallback: key hiç alınamazsa anlamlı hata mesajı

## Routeway API Quirks (Known)

### 1. `method="POST"` Required
Python `urllib.request.Request` with `data=` parameter defaults to POST, but Routeway requires explicit `method="POST"`. Without it, returns 502/504:

```python
# WRONG — returns 502/504
req = urllib.request.Request(url, data=body, headers=h)

# CORRECT
req = urllib.request.Request(url, data=body, headers=h, method="POST")
```

### 2. StepFun Reasoning Model — Empty Content
`step-3.5-flash:free` is a reasoning model. The `content` field in the response is ALWAYS empty. The model's output goes to `reasoning_content` instead.

```json
// Response shape
{
  "choices": [{
    "message": {
      "content": "",                    // ← always empty
      "reasoning_content": "actual output here...",
      "reasoning": "also here..."
    }
  }]
}
```

**Fix:** Extract JSON from `reasoning_content` using regex:
```python
import re
msg = result["choices"][0]["message"]
content = msg.get("content", "")
if not content:
    reasoning = msg.get("reasoning_content", "") or msg.get("reasoning", "")
    if reasoning:
        # Find JSON blocks in reasoning output
        candidates = re.findall(r"\{[^{}]*\}", reasoning)
        for c in reversed(candidates):
            if len(c) > 50 and ("ortalama" in c or "puan" in c):
                return c
```

### 3. Routeway Free Model Catalog (20 Haz 2026)

| Model | Türkçe | Content | Gerçek Durum |
|-------|--------|---------|-------------|
| `step-3.5-flash:free` | 🟡 Orta | ⚠️ Boş (reasoning) | ✅ Çalışıyor — regex gerek |
| `nemotron-3-nano-30b-a3b:free` | 🔴 **Berbat** | ✅ Dolu | ✅ Çalışıyor ama kullanma |
| `deepseek-v4-flash:free` | 🟢 İyi | ✅ Dolu | ❌ Arada 502 |
| Diğer 12 model (gpt-oss-120b, minimax, gemma, vs.) | ? | ? | ❌ 502 Bad Gateway |

**Kritik not:** Routeway `/v1/models` tüm modelleri `available: true` gösterir ama gerçek API çoğundan 502 döner. **Listeye değil, fiili teste güven.**

### 4. Model Seçiminde Doğru Kriter Sırası (20 Haz 2026 Dersi)

```
YANLIŞ (benim yaptığım):
1. Hallucination rate düşük mü? 🔴
2. Content field dolu mu? 🔴
3. Hızlı mı? 🔴
4. Türkçesi iyi mi? → "sonra bakarım" ← HATA

DOĞRU (bundan sonra):
1. Türkçe kalitesi iyi mi? 🟢 ← BİRİNCİL
2. Content alınabiliyor mu? (dolu veya regex) 🟡
3. Hız / stabilite / halüsinasyon ⚪
```

### 5. Rate Limits (Free Tier)
- Nemotron: ~1 req/2s before 429
- Step-3.5-flash: ~1 req/2s  
- Long prompts (3K+ system + conversation) on step-3.5-flash can produce 504 Gateway Timeout
- max_tokens > 4000 may timeout on free tier
- All free: 5-20 RPM / 200 RPD

### 6. LiteRouter Alternatifi ve grok-4.1-fast-reasoning:free (20 Haz 2026)

Routeway'deki kronik 502 sorunları nedeniyle LiteRouter değerlendirildi:

| Özellik | Routeway | LiteRouter |
|---------|----------|------------|
| Endpoint | `api.routeway.ai/v1` | `api.literouter.com/v1` |
| Free tier | 5 RPM / 200 RPD | Unlimited (1 req/5sn soft) |
| Failover | Yok — 502'de çöker | Instant — otomatik yedek modele geçer |
| Çalışan free modeller | 2/15 (step-3.5, nemotron) | Bilinmiyor — test edilmedi |
| Kayıt | Gerekli | literouter.com'da gerekli |

**grok-4.1-fast-reasoning:free Değerlendirmesi:**
- **Model:** xAI Grok 4.1 Fast Reasoning (LiteRouter üzerinden free)
- **Reasoning kontrolü:** `reasoning_enabled=false` ile kapatılabiliyor → content boş kalmaz
- **Context:** 2M token
- **Hız:** Fast reasoning — çok hızlı
- **Türkçe:** ❓ Bilinmiyor. xAI modelleri İngilizce ağırlıklı. Grok 2 1212'de multilingual geliştirmeleri var ama Grok 4.1'de net bilgi yok.
- **Routeway durumu:** Routeway'de 7 grok model var ama HİÇBİRİ free değil (grok-4.1-fast $0.19M input)
- **Risk:** Reasoning model olduğu için content sorunu yaşayabilir (ama reasoning kapatılabiliyor). Türkçe performansı test edilmedi.

LiteRouter'a geçiş yapılırsa, Routeway key'i yerine LiteRouter key'i gerekir. Script'te sadece BASE_URL değişir — API formatı aynı (OpenAI uyumlu).

## Migration Steps

### OpenRouter → Routeway (step-3.5-flash)

1. **Base URL:** `https://openrouter.ai/api/v1` → `https://api.routeway.ai/v1`
2. **Model:** `openai/gpt-oss-120b:free` → `step-3.5-flash:free`
3. **Headers:** Remove `HTTP-Referer` and `X-Title` (OpenRouter-specific)
4. **Auth:** Same Bearer token format, different key
5. **method:** Add `method="POST"` (see quirk #1)
6. **Content handling:** Add reasoning_content fallback (see quirk #2)

### step-3.5-flash → nemotron-3-nano-30b-a3b:free (June 2026)

1. **Model:** Change to `nemotron-3-nano-30b-a3b:free`
2. **Simplify output handling:** Remove reasoning_content regex extraction — Nemotron fills `content` directly
3. **Keep** `method="POST"`, headers, and key file unchanged
4. **Result:** Faster, cleaner, no content-empty edge cases

## Security Pattern
The `/tmp/.or_key` file is written by a secure pipeline (Python script that calls `bws` to fetch from Bitwarden, writes to file, chmod 600). The cron script never sees the Bitwarden token or the API key value directly — only reads it from disk. The primary LLM never sees the key value at any point.
