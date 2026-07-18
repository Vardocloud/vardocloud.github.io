# opencode-zen Reasoning Content Fix

**Tarih:** 18 Temmuz 2026
**Model:** deepseek-v4-flash-free
**Provider:** opencode-zen (base_url: https://opencode.ai/zen/v1)

## Sorun

deepseek-v4-flash-free opencode.ai/zen'de bir **reasoning model** olarak yapılandırılmış. 
`max_tokens` parametresi gönderildiğinde yanıt `reasoning_content`'e yazılıyor, `content` boş kalıyor.

## Çözüm: 2 Adım

### 1. Cloudflare WAF — User-Agent Engeli

opencode.ai/zen/v1 Cloudflare WAF tarafından korunuyor. curl'un varsayılan User-Agent'ı 
(`curl/8.14.1`) 403 Forbidden (error code 1010) ile engelleniyor.

**Fix:** Provider extra_headers'ına Chrome tarayıcı header'ları ekle:

```yaml
extra_headers:
  User-Agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
  Origin: 'https://opencode.ai'
  Referer: 'https://opencode.ai/zen'
```

Bu header'larla API'ye doğrudan erişim sağlanabilir (Browserbase Cloud IP'si gerekmez).

### 2. Reasoning Model — content Boş Sorunu

deepseek-v4-flash-free opencode.ai/zen'de reasoning model olarak çalışır.
Reasoning modellerde:
- `max_tokens` → sadece reasoning token'larını sınırlar, **content boş kalır**
- `max_completion_tokens` → toplam token'ları sınırlar, **content dolu gelir**

**Fix:** Provider extra_body'sinde `max_tokens`'ı null yap, `max_completion_tokens` kullan:

```yaml
extra_body:
  max_tokens: null              # Hermes'in gönderdiği max_tokens:16384'ü ezer
  max_completion_tokens: 8192   # reasoning model için doğru parametre
```

### Test Sonuçları

| Parametre | content | reasoning_content | finish_reason |
|-----------|---------|-------------------|---------------|
| `max_tokens: 20` | ❌ boş | ✅ var | length |
| `max_completion_tokens: 20` | ✅ "2" | ✅ var | stop |
| Hiçbiri | ✅ "2" | ✅ var | stop |
| `max_tokens: null` + `max_completion_tokens: 100` | ✅ "2" | ✅ var | stop |
| `max_tokens: 50` + `max_completion_tokens: 200` | ❌ boş | ✅ var | length |

**Önemli:** `max_tokens` ve `max_completion_tokens` birlikte gönderilince `max_tokens` baskın çıkar, content boş kalır.
Bu yüzden `max_tokens: null` ile Hermes'in gönderdiği değer ezilmelidir.

### Rate Limit Testi

10 ardışık istek (0.5sn aralıkla):
- 10/10 başarılı
- Ortalama token tüketimi: ~244 token/istek
- Hiç rate limit veya 429 hatası alınmadı

## Config Uygulaması

opencode-zen custom provider'ında:

```yaml
- api_key_env: OPENCODE_ZEN_API_KEY
  api_mode: chat_completions
  base_url: https://opencode.ai/zen/v1
  extra_headers:
    User-Agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
    Origin: 'https://opencode.ai'
    Referer: 'https://opencode.ai/zen'
  extra_body:
    max_tokens: null
    max_completion_tokens: 8192
  models:
    deepseek-v4-flash-free: deepseek-v4-flash-free
  name: opencode-zen
```

## Geçmiş Çözümler (Reddedilen)

| Çözüm | Neden Reddedildi |
|-------|-----------------|
| LiteRouter/deepseek-v3.2'ye geçmek | LiteRouter'da deepseek-v4-flash:free ile aynı kotayı paylaşır, limit erken biter |
| hy3-free kullanmak | Tencent Hy3 modeli, lisansı AB/UK/Güney Kore'ye ihracatı yasaklıyor |
| NVIDIA deepseek-ai/deepseek-v4-flash | Worker queue overload (503 ResourceExhausted), güvenilmez |
