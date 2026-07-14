# Keepalive-MCP Bridge

Keepalive Chrome (port 18800) + MCP auth profilleri arasında 20 dk'lık sync döngüsü.

## Mimari

```
                    ┌──────────────────┐
                    │  Keepalive Chrome │ (port 18800, Xvfb :99)
                    │  notebooklm.google│ VNC: localhost:6080
                    └────────┬─────────┘
                             │ CDP (Network.getAllCookies)
                             ▼
                    ┌──────────────────┐
                    │ cdp_extract_both │ ~/hermes/scripts/
                    └────────┬─────────┘
                             │ cookies.json
                             ▼
                    ┌──────────────────┐
                    │  sync_mcp_auth() │ nb_keepalive.py
                    └───┬─────────┬────┘
                        │         │
                        ▼         ▼
              ┌──────────┐  ┌──────────┐
              │  legacy   │  │   pro    │
              │imgorulsunn│  │kenshin4155│
              └──────────┘  └──────────┘
```

## Bileşenler

| Bileşen | Yol | Görev |
|---------|-----|-------|
| `nb_keepalive.py` | `~/.hermes/scripts/nb_keepalive.py` | Ana döngü: Chrome check → CDP extract → MCP sync |
| `cdp_extract_both.py` | `~/.hermes/scripts/cdp_extract_both.py` | Keepalive Chrome'dan cookies alır |
| `sync_mcp_auth()` | nb_keepalive.py içinde | `nlm login --cdp-url --profile NAME --force` ile profilleri günceller |
| `nb_autologin.py` | `~/.hermes/scripts/nb_autologin.py` | Fallback: CDP başarısız olursa Selenium ile login dener |
| `nb_telegram_alert.py` | `~/.hermes/scripts/nb_telegram_alert.py` | 3x fallback başarısızsa Telegram SOS |
| `start-chrome-keepalive.sh` | `~/.hermes/scripts/start-chrome-keepalive.sh` | Chrome'u port 18800'de başlatır |

## Cron Job

```
Job: nb_keepalive_2h
Schedule: */20 * * * * (her 20 dk)
Script: nb_keepalive.py
no_agent: true
```

Zaten mevcut. Yeni bir job eklemeye gerek yok.

## Profil Dizini

```
~/.notebooklm-mcp-cli/profiles/
├── legacy/     → isimgorulsunn@gmail.com
├── pro/        → kenshin4155@gmail.com
└── default/    → eski/auth'suz
```

## Acil Durum Prosedürü

Keepalive Chrome ölürse ve otomatik restart çalışmazsa:

1. VNC: `http://localhost:6080/vnc.html`
2. Chrome zaten `notebooklm.google.com` ile açılır (start-chrome-keepalive.sh)
3. Google hesap seçme ekranında istenen hesabı seç + şifre gir
4. Haber ver → `sync_mcp_auth()` çalıştır

Manuel sync:
```bash
export PATH="$HOME/.local/bin:$HOME/.local/share/uv/tools/notebooklm-mcp-cli/bin:$PATH"
nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --profile legacy --force
nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --profile pro --force
```
