# OpenCode Go Proxy Mimarisi

**Keşif Tarihi:** 31 Mayıs 2026
**Amaç:** OpenCode Go'nun Cloudflare bypass ve proxy mimarisini belgelemek.

## Mimari Özet

OpenCode, iki ayrı AI provider'ı iki ayrı local proxy portu üzerinden yönetir:

```
~/.config/opencode/opencode.json
├── Pollinations provider → http://127.0.0.1:19999/v1
│   ├── npm: @ai-sdk/openai-compatible
│   ├── Modeller: minimax, glm, gpt-5.4-mini, gemma
│   └── Proxy: ~/.hermes/scripts/pollinations-proxy.py
│
└── OpenCode Go provider → http://127.0.0.1:19998/v1
    ├── npm: @ai-sdk/openai-compatible  
    ├── Modeller: deepseek-v4-flash, deepseek-v4-pro, minimax-m2.7,
    │            glm-5, glm-5.1, kimi-k2.5, kimi-k2.6, mimo-v2.5,
    │            mimo-v2.5-pro, minimax-m2.5, qwen3.6-plus, qwen3.7-max
    └── Proxy: HENÜZ YOK (yapılacak)
```

## OpenCode Go API

- **Auth key:** `~/.local/share/opencode/auth.json` → `"opencode-go"` key'i
- **Key format:** `sk-pqn...` (Pollinations formatında)
- **API endpoint:** OpenCode Go kendi altyapısı üzerinden, Cloudflare korumalı
- **UA gereksinimi:** Browser User-Agent zorunlu (Cloudflare 1010 bypass)
- **Port:** 19998 (19999'dan AYRI)

## Debugging İpuçları

1. **"Invalid model or alias" hatası:** Model adı yanlış formatta. `opencode-go/deepseek-v4-flash-free` GEÇERSİZ, doğrusu `opencode-go/deepseek-v4-flash`.
2. **"Invalid API key" hatası:** Proxy çalışmıyor veya key yanlış endpoint'e gidiyor.
3. **Port kontrolü:** `curl http://127.0.0.1:19999/v1/models` — cevap gelmiyorsa proxy down.
4. **Config lokasyonu:** `~/.config/opencode/opencode.json` (standart `~/.opencode.yaml` DEĞİL).
5. **Port kontrolü:** `curl http://127.0.0.1:19998/v1/models` — cevap gelmiyorsa proxy yok.

## ⚠️ Pollinations Proxy Kararsızlığı (PITFALL — 7 Haz 2026)

Pollinations proxy (:19999) belirli aralıklarla DOWN olur — `curl` timeout verir, hiç yanıt dönmez. Bu durumda `gpt-5.4-mini`, `gemma` gibi Pollinations modelleri kullanılamaz.

**Belirti:** `curl -s --max-time 5 http://127.0.0.1:19999/v1/models` → timeout, hiç çıktı yok.

**Çözüm — Fallback model kullan:**
1. Pollinations modelleri yerine `deepseek-v4-flash-free` + `opencode-zen` kullan (ücretsiz)
2. Cron job'da provider'ı `opencode-zen`, modeli `deepseek-v4-flash-free` yap
3. `base_url` alanını `null` olarak ayarla — provider kendi endpoint'ini kullansın

**Cron job provider değiştirirken base_url tuzağı:**
- Cron job'da `base_url` alanı manuel set edilmişse (örn. `http://127.0.0.1:19999/v1`), provider değişse bile istekler eski endpoint'e gider
- Provider `opencode-zen` + `base_url: http://127.0.0.1:19999/v1` → Pollinations proxy'sine Zen formatında istek → 400/hatalı yanıt
- **Doğrusu:** `cronjob(action='update', job_id='...', model={provider: 'opencode-zen', model: 'deepseek-v4-flash-free'})` ve `base_url`'i `null` yapmak için job'ı patch'le

## Mevcut Durum (31 Mayıs 2026)

| Bileşen | Port | Durum |
|---------|------|-------|
| Pollinations proxy | 19999 | ✅ Çalışıyor |
| OpenCode Go proxy | 19998 | ❌ Yok |
| Pollinations Ekip | 19999 | ✅ 4/4 ajan yanıt veriyor |
| OpenCode Go Ekip | 19998 | ❌ Test edilemedi |

## Yapılacaklar

1. Port 19998 için `opencode-go-proxy.py` oluştur
2. OpenCode Go API endpoint'ini tespit et (muhtemel: api.opencode.ai)
3. Browser UA ile Cloudflare bypass ekle
4. auth.json'daki key'i enjekte et
5. systemd servisi yap
