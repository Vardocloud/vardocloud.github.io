# Hermes API Server

OpenAI-uyumlu API server, gateway ile aynı süreçte çalışır (port 8642, loopback-only varsayılan).

## Endpoints

| Method | Path | Açıklama |
|--------|------|----------|
| POST | /v1/chat/completions | OpenAI Chat Completions formatı |
| POST | /v1/responses | OpenAI Responses API (stateful) |
| GET | /v1/models | Model listesi |
| GET | /v1/capabilities | Yetenek listesi |
| GET | /health | Sağlık kontrolü |
| GET | /health/detailed | Detaylı durum |

## Authentication

- Env: `API_SERVER_KEY` veya config `key` alanı
- Header: `Authorization: Bearer <key>`
- Boş bırakılırsa auth devre dışı (herkese açık)
- Ağa açıksa MUTLAKA key set et

## Host/Port Yapılandırması

- Env: `API_SERVER_HOST` (varsayılan: 127.0.0.1)
- Port: `API_SERVER_PORT` env veya config (varsayılan: 8642)
- Dışarı açmak için: `API_SERVER_HOST=0.0.0.0`

## n8n Entegrasyonu

"OpenAI Chat Model" node'unda:
- Base URL: `http://<hermes-ip>:8642/v1`
- API Key: `API_SERVER_KEY` değeri
- Model: `deepseek-v4-pro` (veya herhangi bir aktif model)

## Güvenlik Notları

- Tailscale üzerinden erişim tercih edilir (port açmaya gerek kalmaz)
- Public IP'ye açılacaksa API key zorunlu
- UFW kuralı: `sudo ufw allow from <n8n-ip> to any port 8642`
