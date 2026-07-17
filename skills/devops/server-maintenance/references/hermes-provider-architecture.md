## Hermes 0.16 Provider Architecture

### Built-in vs Custom Providers

| Provider | Built-in? | API Key (.env) | Notlar |
|----------|-----------|----------------|--------|
| `deepseek` | ✅ | `DEEPSEEK_API_KEY` | `deepseek-pro`, `deepseek-v4-flash` gibi OpenCode model adlarını DESTEKLEMEZ |
| `opencode-zen` | ✅ | `OPENCODE_ZEN_API_KEY` | alias: `opencode`, `zen`. is_aggregator=true |
| `opencode-go` | ✅ | `OPENCODE_GO_API_KEY` | alias: `go`, `opencode-go-sub`. is_aggregator=true. **deepseek-v4-flash ve deepseek-v4-pro burada tanımlı** |
| `pollinations` | ❌ | `POLLINATIONS_API_KEY` | Built-in değil! Sadece `custom_providers` ile tanımlı |
| `mistral` | ❌ | Mistral API key | Built-in değil, `custom_providers` ile tanımlı |

### Tespit Edilen Provider/Model Uyuşmazlıkları

**Kritik:** `deepseek-v4-flash` ve `deepseek-v4-pro` OpenCode'a ait model isimleridir — DeepSeek'in kendi API'sinde bu isimde modeller yoktur. `opencode-go` custom provider'ı altında tanımlıdırlar.

| Alias | Model | Şu anki provider | Olması gereken |
|-------|-------|-----------------|----------------|
| `/derin` | `deepseek-v4-pro` | `deepseek` ❌ | `opencode-go` |
| `/bedava-kod` | `deepseek-v4-flash` | `deepseek` ❌ | `opencode-go` |
| `/hizli` | *(yok)* | `pollinations` ❌ | model eksik |
| `/bedava-deep` | `nemotron-3-ultra-free` | opencode-zen | ⚠️ custom_providers'ta `nematron-3-ultra-free` yazıyor (typo) |
| Delegasyon | `deepseek-v4-flash` | `deepseek` ❌ | `opencode-go` |

### Pollinations Özel Durumu

Pollinations built-in olmadığı için:
- `providers.pollinations: ''` boş string override'ı **kaldırılmalı** — Hermes bunu built-in override'ı olarak okur, Pollinations built-in olmadığı için anlamsızdır
- Sadece `custom_providers` içinde `name: Pollinations` olarak tanımlıdır
- Internal slug: `custom:pollinations`
- `model_aliases`'de `provider: pollinations` kullanıldığında Hermes önce built-in'leri tarar, bulamazsa custom_providers'a düşer

### Auxiliary Modeller Pollinations'ı Nasıl Kullanır?

Auxiliary config (`auxiliary.vision`, `auxiliary.web_extract` vb.) provider sistemini **bypass eder** — doğrudan `base_url` + `api_key` alır:

```yaml
auxiliary:
  vision:
    provider: pollinations   # etiket amaçlı, resolution için kullanılmaz
    model: qwen-vision
    base_url: http://127.0.0.1:19999/v1  # direkt proxy
    api_key: sk_2qC...4Tsc
```

Bu sayede auxiliary modeller Pollinations proxy'ye (19999) doğrudan bağlanır.

### Ana Provider (deepseek) Açmazı

`model.default: deepseek-pro` + `model.provider: deepseek`:
1. Hermes `deepseek` built-in provider'ını bulur
2. `DEEPSEEK_API_KEY`'i `.env`'den okur
3. `https://api.deepseek.com` üzerinden `deepseek-pro` modelini çağırır

**Sorun:** DeepSeek'in kendi API'sinde `deepseek-pro` diye bir model adı yoktur. Bu isim OpenCode/başka bir proxy'ye ait. Gateway test'te 401 dönmesinin sebebi bu olabilir.

### Düzeltme Stratejisi

1. `providers.pollinations` satırını config'den kaldır
2. Model alias'larını doğru provider'larla eşle:
   - `deepseek-v4-pro` → `opencode-go`
   - `deepseek-v4-flash` → `opencode-go`
3. `/hizli` alias'ına model ekle (örn. `openai`)
4. `/bedava-deep` → `nemotron-3-ultra-free` typo'sunu düzelt
5. Ana provider'ı `opencode-go` yap veya deepseek API'de geçerli bir model adı kullan
