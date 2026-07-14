# Routeway & StepFun — Provider Detayı (20 Haz 2026 Güncel)

## Routeway API — Genel Bilgi
Routeway (`routeway.ai`) OpenAI-compatible bir API gateway. 221+ model sunar, bazıları `:free` suffix ile ücretsiz.

### Erişim
- **Gateway:** `https://api.routeway.ai/v1`
- **Auth:** `Authorization: Bearer *** (OpenAI-compatible)
- **Key formatı:** `clsk-` ile başlar, 32+ karakter
- **SDK:** OpenAI Python SDK (sadece `base_url` değişir)
- **Dokümantasyon:** https://docs.routeway.ai/llms.txt

### Free Modeller (`:free` suffix)
| Model | Tip | Not |
|-------|-----|-----|
| `gpt-oss-120b:free` | LLM, Reasoning, Function Call | ⭐ En uygun değerlendirme |
| `gpt-4o-mini:free` | Vision, LLM, Function Call | Daha hızlı, iyi alternatif |

## Sohbet Skill'i İçin Kullanım
StepFun, sohbet değerlendirme/öğrenme sub-agent'ı olarak DeepSeek Flash'a alternatif:
- Günlük konuşma kalitesi değerlendirmesi
- Edel'i öğrenme (tercihler, konuşma tarzı)
- Role-play'de iyi biliniyor, insansı değerlendirme potansiyeli

## StepFun Modelleri — Routeway'de
StepFun modelleri (`stepfun/step-3.5-flash`, `stepfun/step-3.7-flash`) Routeway'de **ücretli** olabilir. Değerlendirme için Routeway'deki `gpt-oss-120b:free` önerilir.

## Kullanım
```python
from openai import OpenAI
client = OpenAI(
    base_url="https://api.routeway.ai/v1",
    api_key="clsk-..."
)
response = client.chat.completions.create(
    model="gpt-oss-120b:free",
    messages=[{"role": "user", "content": "..."}]
)
```

## API Key — Gerçek Key vs Döküman (20 Haz 2026)

| Özellik | Döküman (docs.routeway.ai) | Gerçek (Bitwarden SM) |
|---------|---------------------------|----------------------|
| Prefix | `clsk-` | `sk-fmh...` |
| Uzunluk | 32+ karakter | 78 karakter |
| Auth | Bearer token | Bearer token ✅ |

Routeway docs `clsk-` formatı belirtir, ancak Bitwarden SM'deki `ROUTEWAY_API_KEY` secret'ı `sk-fmh...` formatında (78 karakter). Edel dashboard'da key'in doğru olduğunu teyit etti. Bu tutarsızlık henüz açıklanmadı.

## 401 Hatası — Bilinen Sorun (20 Haz 2026 — ÇÖZÜLMEDİ)

| Endpoint | Method | Sonuç |
|----------|--------|-------|
| `/v1/models` | GET | ✅ HTTP 200, model listesi döner |
| `/v1/chat/completions` | POST | ❌ HTTP 401 "Invalid API key" |

- GET `/v1/models` başarılı ama POST `/v1/chat/completions` tüm modellerde 401
- Denenen auth: `Authorization: Bearer <key>`, `X-API-Key: <key>` (ikisi de 401)
- Denenen modeller: `step-3.5-flash:free`, `gpt-oss-120b:free`, `gpt-4o-mini`, `step-3.7-flash:free`
- Denenen HTTP client'lar: curl, Python urllib, Python requests (hepsi 401)
- ALL_PROXY="" (WARP kapalı, doğrudan bağlantı)
- Olası nedenler: Key'in chat completion scope'u yok, hesap bölgesel kısıtlama, API routing sorunu
- **Çözüm:** Dashboard'da key permission/scope kontrol et, yeni test key'i oluştur

## Pitfall
- API key injection: `sk-fmh...` formatı (dökümandaki `clsk-` değil) — `mcp_local_secure_secure_save` ile yazılabilir
- `/tmp/.or_key` dosya adı tarihsel (OpenRouter için oluşturulmuştu), Routeway key'i için farklı bir dosya adı kullanılabilir
- ALL_PROXY="" zorunlu — WARP Routeway'i bloklar
