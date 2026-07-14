# Hermes API Server — n8n & Platform Entegrasyonu

Hermes, OpenAI-uyumlu bir API server sunar. Gateway ile aynı portta (8642) çalışır.

## Endpoint'ler

| Method | Path | Açıklama |
|--------|------|----------|
| POST | `/v1/chat/completions` | OpenAI Chat Completions formatı |
| GET | `/v1/models` | Model listesi |
| GET | `/health` | Health check |
| GET | `/health/detailed` | Detaylı durum |

## n8n Entegrasyonu

1. n8n'de **OpenAI Chat Model** node'u ekle
2. Base URL: `http://<sunucu-ip>:8642/v1`
3. API Key: Hermes API key (veya boş bırak, gateway kimlik doğrulamasına bağlı)

## Port Erişimi

- **Varsayılan:** Sadece `127.0.0.1` (loopback). Aynı sunucudaki servisler erişebilir.
- **Dış erişim için:** Config'de host'u `0.0.0.0` yapmak gerekir.
- **Güvenlik:** Dış erişim açılacaksa UFW/nginx reverse proxy ile koruma önerilir.

## Diğer Uyumlu Platformlar

OpenAI API formatı destekleyen her platform bağlanabilir:
- Open WebUI
- LobeChat, LibreChat, AnythingLLM
- NextChat, ChatBox
- Custom Python/JS script'leri (OpenAI SDK ile)
