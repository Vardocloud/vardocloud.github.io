# Systemd User Service — Telegram Bot Deployment

5 Haz 2026 — `@keficobot` (Fiş Asistanı) deployment'ında kullanılan pattern.

## Service Dosyası

`~/.config/systemd/user/fis-asistani.service`:

```ini
[Unit]
Description=Fis Asistani Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/data/projects/fis-asistani
EnvironmentFile=/data/projects/fis-asistani/.env
ExecStart=/data/projects/fis-asistani/.venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=fis-asistani

[Install]
WantedBy=default.target
```

## Kritik Kurallar

| Kural | Nedeni |
|-------|--------|
| `EnvironmentFile=` kullan, asla `Environment=` | API key'leri servis dosyasında plain text bırakma |
| `.env` dosyası `chmod 600` | Bot token'ı içerir |
| `WorkingDirectory=` tam path | Proje root'unda çalışması gereken import'lar için |
| `Restart=always` + `RestartSec=10` | Crash sonrası otomatik restart, 10sn bekleme |
| `/data` üzerinde venv | Kök diskte yer kaplamaz |

## Komutlar

```bash
# İlk kurulum
systemctl --user daemon-reload
systemctl --user enable fis-asistani
systemctl --user start fis-asistani

# Durum kontrol
systemctl --user status fis-asistani

# Log
journalctl --user -u fis-asistani -f

# Restart
systemctl --user restart fis-asistani
```

## .env Formatı

```bash
FIS_BOT_TOKEN=123456:ABCdef...
FIS_USER_ID=6306976553
```

token değerini ASLA log'da veya servis dosyasında gösterme.
