# Provider Sorunları ve Tanı

## Pollinations Kesintisi (HTTP 502)

### Belirtiler
- `RuntimeError: Your request was blocked.` hatası
- Birden fazla cron job aynı anda patlar
- `curl` testi HTTP 502 döner

### Tanı Komutu (API key manuel gir)
```bash
curl -s -w "\nHTTP %{http_code}" \
  "https://gen.pollinations.ai/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <POLLINATIONS_API_KEY>" \
  -d '{"model":"mistral-large","messages":[{"role":"user","content":"test"}],"max_tokens":5}' \
  --max-time 15
```
`<POLLINATIONS_API_KEY>` yerine `.env` dosyasındaki değeri yaz.

### Hızlı Tanı: Provider Karşılaştırması
Cron job'ların provider'larını karşılaştır:
- Deepseek kullananlar çalışıyor + Pollinations kullananlar patlıyor → Pollinations down
- Hepsi patlıyor → Daha büyük sorun (internet, sunucu)

### Çözüm
1. Pollinations 502/401 → cron job'ları deepseek'e geçir
2. Pollinations düzelince geri al
3. Alternatif: Pollinations yerine başka provider yapılandır

## Config'de Provider Karışıklığı (Pitfall)

`config.yaml`'da iki ayrı provider var:

| Provider | Amaç | URL | Modeller |
|----------|------|-----|----------|
| **Pollinations** | Çoklu model (17) | `gen.pollinations.ai/v1` | claude, deepseek, gemini, mistral, ... |
| **Mistral** | Sadece Mistral | `api.mistral.ai/v1` | mistral-large, medium, small |

İkisi de `mistral-large` modelini sunar ama farklı API key ve endpoint.
`mistral-large @ pollinations` → Pollinations API, `mistral-large @ mistral` → Mistral API.
Provider'lar karıştırılırsa `401 Unauthorized` alınır.

### Kesinti Geçmişi
- 23-24 Mayıs 2026: Pollinations 502, tüm pollinations cron job'ları patladı. LinkedIn ve weekly_curator deepseek'e taşındı.
- 25 Mayıs 2026: Pollinations düzeldi, API key zorunlu hale geldi (önceden açıktı).
- 27 Mayıs 2026: Pollinations çalışıyor (200 OK). 88 model mevcut, 17'si config'de tanımlı.

### ⚠️ Pitfall: 401 Unauthorized = Down Değil

Pollinations 401 döndüğünde **down sanma**. API key `.env` dosyasında `POLLINATIONS_API_KEY` olarak kayıtlı.

Tanı: önce key'siz, sonra key'li `/v1/models` endpoint'ini test et.
Eğer key'siz 401, key'li 200 → Pollinations çalışıyor, down değil.
