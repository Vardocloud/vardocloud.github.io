# Morning Greeting → Pollinations Migration (2026-06-08)

## Timeline

1. **Base URL contamination**: `morning_greeting` job'unda `base_url: http://127.0.0.1:19999/v1` (Pollinations proxy'si) varken model `mimo-v2.5-free` (opencode-zen) set edilmişti. Pollinations bu modeli tanımadığı için "Invalid model or alias" hatası.
   - **Fix**: `base_url` kaldırıldı → job opencode-zen'de çalışır hale geldi.

2. **Pollinations'a taşı**: Edel token yenilendiğini söyledi. Model `gpt-5.4-mini`, provider `custom:Pollinations` olarak değiştirildi.

3. **128 tool limit**: Pollinations'taki gpt-5.4-mini (Azure OpenAI) 128 tool limiti. Hermes 135+ tool gönderiyor.
   - **Fix**: `enabled_toolsets: ["terminal", "web", "file", "search"]` eklendi → 128'in altına düştü.

4. **Sonuç**: Job Pollinations'da çalışıyor. Azure filter sorunu yok (token yenilenmiş).

## Key Lessons

- **Token refresh Azure filter'ı çözebilir**: Daha önce gpt-5.4-mini Azure filter tarafından bloklanan rutin Türkçe mesajlar, token yenilenince çalışmaya başladı.
- **enabled_toolsets seçimi job tipine göre değişir**: morning_greeting için `delegation` gerekmez, sadece `["terminal","web","file","search"]` yeterli.
- **Üç adımda Pollinations geçişi**: base_url kontrol → model/provider değişikliği → enabled_toolsets ekleme.

## Config Snapshot (After Fix)

```json
{
  "model": "gpt-5.4-mini",
  "provider": "custom:Pollinations",
  "base_url": null,
  "enabled_toolsets": ["terminal", "web", "file", "search"]
}
```
