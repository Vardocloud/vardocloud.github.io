# Delegation Model Routing — Bulgular ve Workaround

## Keşif Tarihi: 30 Mayıs 2026

## Problem
Pollinations modellerini `delegate_task` alt ajanlarında kullanmak istiyoruz ama:
1. Pollinations safety filtresi Hermes'in sistem mesajlarını engelliyor
2. `delegation.base_url` ayarı ignore ediliyor (custom_providers eşleşmesi öncelikli)

## Pollinations Erişim (ÇÖZÜLDÜ ✅)

**GERÇEK SORUN:** Cloudflare browser signature ban (error 1010). Python UA bloklanıyordu.
**Çözüm:** Proxy (systemd `pollinations-proxy.service`, port 19999) → tarayıcı UA header'ı ekler.
**Detay:** `references/cloudflare-ua-bypass.md`

`Pollinations-Safe: false` header'ı gerekli DEĞİLDİR — sorun içerik değil HTTP katmanıydı.

## Delegation Config Bulguları

### Çalışanlar
- `delegation.model: openai` → model değişiyor ✅
- `delegation.api_key: sk_...` → custom_providers ile eşleşiyor ⚠️
- `delegation.api_mode: chat_completions` → path: `/chat/completions` (base_url sonunda `/v1` OLMALI)

### Çalışmayan
- `delegation.base_url` → **TAMAMEN GÖRMEZDEN GELİNİYOR** ❌
  - Sebep: `delegation.api_key` set edilince, Hermes bunu `custom_providers`'daki API key ile eşleştirip o provider'ın `base_url`'ini kullanıyor
  - Kanıt: Var olmayan porta (19999) yönlendirince bile connection error yerine 404 (Pollinations'tan)

### Çözüm Yolu
`custom_providers` altına proxy'yi base_url olarak kullanan yeni bir provider ekle:
```yaml
custom_providers:
  - name: PollinationsProxy
    base_url: http://127.0.0.1:19999/v1
    api_key: sk_2qC...  # Pollinations API key
    api_mode: chat_completions
    models:
      openai: openai
      gemini-flash-lite-3.1: gemini-flash-lite-3.1
      deepseek: deepseek
      qwen-coder: qwen-coder
      mistral: mistral
      grok: grok
```

Sonra: `delegation.provider: PollinationsProxy`, `delegation.model: openai`

## Alternatif: execute_code + requests
Proxy olmadan da çalışan yöntem:
```python
import requests, os
key = os.environ["POLLINATIONS_API_KEY"]
resp = requests.post(
    "https://gen.pollinations.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}", "Pollinations-Safe": "false"},
    json={"model": "openai", "messages": [...]}
)
```

Bu yöntem `delegate_task` değil, direkt API çağrısıdır. Tool kullanamaz.

## Pollinations MCP
- Binary: `/home/ubuntu/.npm-global/bin/pollinations-mcp`
- 22 tool (text, image, video, audio, search)
- Auth sorunu: `POLLINATIONS_API_KEY` env var'ı MCP subprocess'ine ulaşmıyor
- Wrapper script denendi (`.env` source + export), config env denendi, ikisi de çalışmadı
- `listTextModels` (auth gerektirmez) çalışıyor, `generateText` auth hatası

## Ücretsiz Pollinations Modelleri
| Alias | Gerçek Model |
|-------|-------------|
| openai | GPT-5.4 Nano |
| gemini-flash-lite-3.1 | Gemini 3.1 Flash Lite |
| deepseek | DeepSeek V4 Flash |
| qwen-coder | Qwen3-Coder 30B |
| mistral | Mistral Small 3.2 |
| grok | Grok 4.20 Beta |

## Hermes -z Pollinations Sessizliği (30 Mayıs 2026)

**Semptom:** `hermes -z "prompt" -m MODEL --provider custom:Pollinations --yolo` → sessiz, exit 0
**Çalışan:** `hermes -z` deepseek ve Mistral ile çalışıyor, `hermes chat` Pollinations ile çalışıyor

**Debug zinciri:**
1. Proxy log'ları: `/v1/props`, `/api/tags`, `/version`, `/v1/models/openai` → Pollinations'ta 404 → hermes provider'ı geçersiz sayıyor
2. Sahte endpoint yanıtları eklendi → chat completions isteği gidiyor ✅ ama çıktı yok
3. Pollinations cevap veriyor (proxy log'unda POST isteği var) ama hermes stdout'a yazdırmıyor
4. Muhtemel neden: Pollinations response'undaki `content_filter_results` ek alanı

**Geçici çözüm:** `light_agent.py` (direkt Pollinations API, toolsuz) + analist için `hermes -z deepseek` (tool'lu)

## OpenCode + Pollinations Keşfi (30 Mayıs 2026)

- `opencode run --model openai/gpt-5.4-mini` → `/v1/responses` endpoint'ine gidiyor → 404
- OpenCode, OpenAI'nin yeni Responses API'sini kullanıyor, Pollinations bunu desteklemiyor
- Çözüm: Proxy'ye `/v1/responses` → `/v1/chat/completions` dönüşümü eklenmeli
- `opencode models openai` → Pollinations'tan model listesini başarıyla çekiyor ✅
- `opencode providers list` → env var'dan OPENAI_API_KEY tanıyor ✅
