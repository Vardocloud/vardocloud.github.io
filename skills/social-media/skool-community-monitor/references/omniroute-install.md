# OmniRoute — Kurulum ve Test Notları

**Kaynak:** AI Automation Society (23 Tem 2026) — Chetan Mishra'nın rate limit / silent quality degradation tartışması.
**Karar:** 🔵 TRY — Test edildi, çalışıyor.

## Kurulum

```bash
npm install -g omniroute
# v3.8.48, 1183 paket
```

## Çalıştırma

```bash
# Serve modunda başlat (start değil, serve!)
omniroute serve --port 20128 --no-open --daemon
```

- `--daemon` arka planda çalıştırır
- Port 20128 (varsayılan)

## Endpoint

```
http://localhost:20128/v1
```

OpenAI-uyumlu. Tüm standart OpenAI API çağrıları çalışır.

## Doğrulama

```bash
# Model listesi
curl -s http://localhost:20128/v1/models

# Chat completion test
curl -s http://localhost:20128/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"oc/deepseek-v4-flash-free","messages":[{"role":"user","content":"1+1?"}],"max_tokens":10}'
```

## Önemli Modeller

| Prefix | Kaynak | Örnek Modeller |
|--------|--------|----------------|
| `auto/` | Combo (akıllı routing) | `best-free`, `best-coding`, `coding:free`, `cheap` |
| `ddgw/` | DuckDuckGo (ücretsiz) | `gpt-4o-mini`, `gpt-5-mini`, `claude-3-5-haiku`, `mistral-small` |
| `aug/` | Auggie | `claude-sonnet-4.6`, `claude-opus-4.6`, `gemini-3.1-pro`, `gpt-5.5` |
| `tllm/` | The Old LLM (ücretsiz) | `GPT_5`, `CLAUDE_4_6_OPUS`, `gemini_3_pro`, `grok_4` |
| `oc/` | OpenCode | `deepseek-v4-flash-free`, `minimax-m3-free`, `qwen3.6-plus-free` |

## Vanitas'a Entegrasyon

OmniRoute, Hermes'in provider routing'inden bağımsız çalışır. Şu an için manuel olarak `http://localhost:20128/v1` endpoint'ine yönlendirme yaparak kullanılır. Gelecekte Hermes config'inde custom provider olarak eklenebilir.

Asıl değeri: rate limit yediğimizde `auto/coding:free` veya `auto/best-free` gibi bir model adı verirsek, OmniRoute otomatik olarak boşta olan provider'a geçer. Kesinti olmaz.

## Kaldırma

```bash
npm uninstall -g omniroute
# 10 saniye, iz bırakmaz
```
