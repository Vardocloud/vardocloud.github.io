# OpenCode Go + Pollinations İkili Proxy Mimarisi

**Tarih:** 31 Mayıs 2026 (Güncelleme: 15 Haziran 2026)
**Durum:** Aktif, manuel süreç olarak çalışıyor (systemd servisi inactive, `ss -tlnp | grep 19998` ile görünür)

## Mimari Özet

İki proxy localhost'ta çalışır:
- Port 19999: Pollinations API (`https://gen.pollinations.ai`) — openai, gemma, minimax, glm, gpt-5.4-mini
- Port 19998: OpenCode Go API (`https://opencode.ai/zen/go`) — deepseek-v4-flash, deepseek-v4-pro, glm-5, glm-5.1, kimi-k2.6, kimi-k2.5, kimi-k2.7-code, minimax-m2.7, minimax-m2.5, minimax-m3, qwen3.7-max, qwen3.7-plus, qwen3.6-plus

## Script Konumları

| Bileşen | Dosya |
|---------|-------|
| Pollinations Proxy | `~/.hermes/scripts/pollinations-proxy.py` |
| OpenCode Go Proxy | `~/.hermes/scripts/opencode-go-proxy.py` |

## Systemd Servisleri

User-level servis dosyaları: `~/.config/systemd/user/pollinations-proxy.service` ve `~/.config/systemd/user/opencode-go-proxy.service`. Boot'ta otomatik başlar (`loginctl enable-linger ubuntu`).

## OpenCode Go API Detayları

### Endpoint ve Auth
- Base URL: `https://opencode.ai/zen/go/v1`
- Auth: `~/.local/share/opencode/auth.json` icinde `opencode-go` key'i (67 chars, `sk-pqn` prefix)

### Model Isimlendirme (KRITIK)
API'ye direkt cagrida model isimleri **prefix'siz** kullanilir. `glm-5` dogru, `opencode-go/glm-5` yanlis (SDK routing prefix'i).

### Iki Endpoint Turu
- `/v1/chat/completions` (OpenAI uyumlu): deepseek-v4-flash, deepseek-v4-pro, glm-5, glm-5.1, kimi-k2.6, kimi-k2.5, kimi-k2.7-code, minimax-m3
- `/v1/messages` (Anthropic uyumlu): minimax-m2.7, minimax-m2.5, qwen3.7-max, qwen3.7-plus, qwen3.6-plus

Proxy sadece chat/completions yonlendirir. Minimax ve Qwen Anthropic endpoint'i kullanir — proxy uzerinden bos content doner.

### Tum Modeller Reasoning Modeli (KRITIK PITFALL)

OpenCode Go'daki tum modeller reasoning yapar. Yanit once `reasoning_content` alaninda dusunce zinciri olarak baslar, tamamlaninca `content` alanina yazilir.

**`max_tokens` dusukse model hic `content` uretmeden kesilir:**
- `max_tokens=500`: tum token'lar reasoning'e gider, content BOŞ (`finish_reason: length`)
- `max_tokens=1000`: reasoning yarida kesilir
- `max_tokens=2000`: yeterli (onerilen minimum)

### Onerilen Token Butceleri

| Kullanim | max_tokens |
|----------|-----------|
| Basit hesap/yardimci | 200-500 |
| Kod uretimi | 800-2000 |
| Icerik yazimi | 1500-2000 |
| Arastirma/analiz | 2000-4000 |

## Proxy Ozellikleri

1. **Browser UA:** Cloudflare 1010 engelini asmak icin Chrome 126 UA
2. **Auth enjeksiyonu:** Istemci auth gondermezse proxy otomatik ekler
3. **Responses→Chat donusumu:** `/v1/responses` → `/v1/chat/completions`
4. **Fake endpoint'ler:** `/v1/models`, `/api/tags`, `/v1/props`, `/version` — Hermes uyumu icin
5. **Dogrudan forwarding:** Diger tum istekler oldugu gibi iletilir

## Pollinations vs OpenCode Go

| Ozellik | Pollinations | OpenCode Go |
|---------|-------------|-------------|
| Ucret | Ucretsiz | $10/ay |
| Model sayisi | 5 | 13 |
| Reasoning | Hayir | Evet (tum modeller) |
| Context limiti | 128K | 128K-1M |
| max_tokens ihtiyaci | Dusuk | Yuksek (reasoning payi) |

## Ilgili Dosyalar
- OpenCode Go proxy: `~/.hermes/scripts/opencode-go-proxy.py`
- Pollinations proxy: `~/.hermes/scripts/pollinations-proxy.py`
- OpenCode config: `~/.config/opencode/opencode.json`
- EKIP agent prompt'lari: `~/.hermes/agents/{analist,kodcu,yazar,yardimci}.md`
- EKIP wrapper: `~/.hermes/scripts/light_agent.py`
