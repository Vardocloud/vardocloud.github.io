# OpenClaw Crash-Loop Vakası (30 Mayıs 2026)

## Belirtiler
- Sunucu tamamen dondu (SSH, Tailscale, hiçbir şey erişilemez)
- Reboot sonrası gateway çalışıyor ama RAM hızla tükeniyor

## Kök Neden
OpenClaw npm modülü (`~/.npm-global/lib/node_modules/openclaw`) diskten silinmiş ama systemd service dosyası kalmış.

```
openclaw-gateway.service:
  ExecStart=/usr/bin/node .../openclaw/dist/index.js gateway --port 18789
  → MODULE_NOT_FOUND → crash → Restart=always → sonsuz döngü
```

## API Key Tehlikesi
Service dosyasında açık metin API key'ler: TELEGRAM_BOT_TOKEN, GROQ_API_KEY, MISTRAL_API_KEY, FIREWORKS_API_KEY, OPENROUTER_API_KEY.

## Temizlik
```bash
systemctl --user stop openclaw-gateway
systemctl --user disable openclaw-gateway
rm ~/.config/systemd/user/openclaw-gateway.service
npm uninstall -g openclaw
systemctl --user daemon-reload
```
Ayrıca context-mode içindeki OpenClaw plugin kalıntıları da temizlendi.

## Önlemler
- Watchdog: crash-loop tespiti + otomatik disable
- Post-update check: binary bütünlük kontrolü
- Docker restart: on-failure:5
