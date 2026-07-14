---
name: container-security-audit
title: Container / Restricted Environment Security Audit
description: "Hızlı (~30s) günlük güvenlik denetimi — ss/netstat/fail2ban/ufw/systemctl olmayan container, WSL ve cron ortamları için port tarama, brute force kontrol, servis sağlığı."
trigger: "Daily cron security audit. User asks 'güvenlik kontrolü yap'. Container/WSL/cron ortamında güvenlik taraması."
version: 1.0.0
---

# Container Security Audit

`ss`, `netstat`, `lsof`, `fail2ban`, `ufw`, `systemctl --user` ve `lastb` çoğu container/WSL/cron ortamında bulunmaz. Bu skill **sadece bu alternatifleri** kullanır.

## 6-Point Daily Check

### 1. Listening Ports → `/proc/net/tcp`

```bash
python3 -c "
data = open('/proc/net/tcp').read()
for line in data.strip().split('\n')[1:]:
    parts = line.split()
    ip_hex, port_hex = parts[1].split(':')
    state = int(parts[3], 16)
    if state != 0x0A:  # LISTEN
        continue
    ip_bytes = bytes.fromhex(ip_hex)
    ip = '.'.join(str(b) for b in reversed(ip_bytes))
    port = int(port_hex, 16)
    print(f'{ip}:{port}')
"
```

**State decoding:** `0x0A` = LISTEN, `0x01` = ESTABLISHED, `0x06` = TIME_WAIT.

Beklenmeyen port var mı? Özellikle `0.0.0.0`'da dinleyenler.

### 2. Failed SSH Attempts

```bash
# Aktif oturum var mı?
w
who
who -b              # boot zamanı
lastlog -t 365      # son kullanıcı girişleri
```

`lastb` ve `journalctl` boş dönebilir — container cron'unda btmp tutulmaz, bu beklenir.

### 3. Docker Containers

```bash
docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "Docker mevcut degil"
```

Container içinde Docker daemon yoksa — sorun değil.

### 4. Disk Usage

```bash
df -h / /data 2>/dev/null   # %85+ alarm
```

### 5. Memory & Swap

```bash
free -h  # swap kullanım trendi
```

### 6. Service Health (systemctl'siz)

```bash
# Process varlığı
pgrep -a -f 'hermes-gateway'
pgrep -a -f 'opencode-go-proxy'
pgrep -a -f 'pollinations-proxy'

# HTTP health check
curl -sf http://127.0.0.1:8888/health 2>/dev/null
```

## Scoring

| Check | Score | Criteria |
|-------|-------|----------|
| Ports | +1 | Beklenmeyen dinleyen yok |
| SSH | +1 | Aktif oturum yok, brute force yok |
| Docker | +1 | Container'lar healthy (veya Docker yok) |
| Disk | +1 | %85 altı |
| Memory | +1 | Swap kullanımı ihmal edilebilir |
| Services | +1 | Tüm beklenen servisler çalışıyor |

Total /5 (docker dahil değilse /5'e docker'sız hesapla).

## Pitfalls

- **Python3 `/proc/net/tcp` hex formatı:** IP little-endian, port big-endian. `bytes.fromhex()` + `reversed()` ile düzelt.
- **`ps aux` eşlemesi:** `/proc/net/tcp` portu ile `ps aux`'daki `--port=` argümanlarını eşle. Chrome child process'leri (zygote, gpu, renderer) ana process'in portunu taşır — onları sayma.
- **`curl` HTTP yanıtı:** Bilinmeyen portlarda `curl -sf http://localhost:<port>/` HTML dönüyorsa servis, boş/refused ise atıl.
- **`lastlog` boş olabilir:** Container'da kullanıcı yoksa normaldir.
- **Docker yokken `docker ps` hata vermez:** `2>/dev/null` ile sessiz kapat, çıktı boşsa "mevcut değil" raporla.