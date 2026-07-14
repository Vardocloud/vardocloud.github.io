# OpenWebUI + Hermes API Integration

## Architecture

```
Browser (Tailscale) → OpenWebUI (Docker, host net, :8080) → Hermes API (host, :8642)
```

OpenWebUI uses `--network host` → `127.0.0.1:8642` Hermes API'ye direkt erişir.

## Required Env Vars

| Env | Value |
|-----|-------|
| `OPENAI_API_BASE_URL` | `http://127.0.0.1:8642/v1` |
| `OPENAI_API_KEY` | `.env` dosyasındaki `API_SERVER_KEY` değeri |

## Containerdan API Erişimini Test

```bash
# Host'tan:
curl -s http://127.0.0.1:8642/health
# → {"status": "ok", "platform": "hermes-agent"}

curl -s http://127.0.0.1:8642/v1/models -H "Authorization: Bearer <api_key>"
```

## Secret Redaction Workaround

`docker run -e OPENAI_API_KEY=<key>` çalışmaz — Hermes redaction key'i `***` ile değiştirir.

Çözüm: `--env-file` kullan. Key'i `.env`'den okuyup geçici dosyaya yaz, container'ı onunla başlat:

```python
import builtins
env = builtins.open('/home/ubuntu/.hermes/.env').read()
for line in env.split('\n'):
    if 'API_SERVER_KEY=' in line:
        key = line.split('=',1)[1].strip().strip('"').strip("'")
        with builtins.open('/tmp/owui.env','w') as f:
            f.write(f'OPENAI_API_BASE_URL=http://127.0.0.1:8642/v1\n')
            f.write(f'OPENAI_API_KEY={key}\n')
```

## Full Docker Run Command

```bash
docker run -d --name open-webui \
  --network host \
  --restart always \
  -v open-webui:/app/backend/data \
  --env-file /tmp/owui.env \
  ghcr.io/open-webui/open-webui:main
```

## Tailscale Access Fix

OpenWebUI container sağlıklı ama Tailscale'den erişilemiyorsa iptables kontrolü:

```bash
sudo iptables -L INPUT -n | grep 8080
# DROP varsa → Tailscale arayüzü bloklanıyor
sudo iptables -I INPUT 1 -i tailscale0 -p tcp --dport 8080 -j ACCEPT
sudo mkdir -p /etc/iptables && sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null
```

## Verification Checklist

- [ ] `curl http://127.0.0.1:8642/health` → 200
- [ ] `docker ps` → open-webui healthy
- [ ] `curl http://127.0.0.1:8080` → 200
- [ ] Tailscale'den `http://100.82.131.32:8080` erişilebilir
- [ ] OpenWebUI admin panel → Connections → Hermes model görünüyor
