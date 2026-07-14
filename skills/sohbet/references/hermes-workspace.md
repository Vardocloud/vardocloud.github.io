# Hermes Workspace — Vanitas Web Arayüzü

Oracle Cloud ARM64 sunucuda, mevcut Hermes Agent (port 8642) yanında çalışıyor.

## Kurulum
```bash
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace && pnpm install && pnpm build
```

## .env (manuel yazılmalı — secret redaction heredoc'ları yer)
```
HERMES_API_URL=http://127.0.0.1:8642
HERMES_API_TOKEN=<API_SERVER_KEY ile aynı>
HOST=0.0.0.0
PORT=3000
HERMES_PASSWORD=<güçlü şifre>
COOKIE_SECURE=0
TRUST_PROXY=1
```

## Başlatma
```bash
cd /home/ubuntu/hermes-workspace && pnpm dev
```

## Erişim
- Lokal: http://127.0.0.1:3000
- Tailscale: http://100.82.131.32:3000

## Özellikler
Chat (SSE), sessions, skills, memory, config, jobs, dashboard çalışıyor.
MCP yönetimi ve enhancedChat yok — zaten ayrı kullanılıyor.

## Pitfall
- `pnpm start` için önce `pnpm build` şart; `pnpm dev` build'siz çalışır
- Secret redaction: .env'deki TOKEN ve PASSWORD'u Edel manuel yazmalı
