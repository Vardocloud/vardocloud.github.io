# Hermes Workspace — Kurulum ve Konfigürasyon

Vanitas'a web arayüzü eklemek için. Telegram sohbet + Workspace yönetim paneli.

## Ön Koşul
- Hermes Agent çalışıyor olmalı (port 8642)
- `API_SERVER_ENABLED=true` ve `API_SERVER_KEY` ayarlı
- Tailscale güvenli uzak erişim için

## Kurulum

```bash
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace
pnpm install
pnpm build
```

## .env Yapılandırması

```env
HERMES_API_URL=http://127.0.0.1:8642
HERMES_API_TOKEN=<API_SERVER_KEY ile aynı>
HOST=0.0.0.0
PORT=3000
HERMES_PASSWORD=<güçlü şifre>
COOKIE_SECURE=0
TRUST_PROXY=1
```

## Çalıştırma

```bash
pnpm dev   # Geliştirme
pnpm start # Prod (build sonrası)
```

## Erişim
- Lokal: `http://127.0.0.1:3000`
- Tailscale: `http://100.82.131.32:3000`

## Pitfall'lar

### Secret Redaction Bypass
API_SERVER_KEY ve PASSWORD değerleri heredoc'ta bile redacte uğrar.
Kullanıcı (Edel) doğrudan yazmalı:
```bash
echo 'HERMES_API_TOKEN=<key>' >> .env
echo 'HERMES_PASSWORD=<sifre>' >> .env
```

### pnpm audit
Kurulum sonrası `pnpm audit` çalıştır, high vulnerability varsa:
```bash
pnpm audit --fix update
```

### Özellikler
- ✅ chat, sessions, skills, memory, jobs, dashboard
- ❌ enhancedChat, MCP management
