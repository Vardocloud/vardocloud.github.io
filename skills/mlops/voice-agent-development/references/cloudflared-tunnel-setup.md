# Cloudflared Tünel ile Voice Agent

## Kurulum
```bash
# 1. Sunucuyu başlat
cd ~/voice-agent-venv && PORT=8765 python voice_agent_server.py &

# 2. HTTPS tüneli aç
cloudflared tunnel --url http://127.0.0.1:8765 2>&1 | tee /tmp/cf_voice.log

# 3. URL'yi al
grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cf_voice.log
```

## Önemli Noktalar
- Cloudflared WebSocket'i destekler — relay mimariyle çalışır
- **Idle timeout:** 8 saniye trafik olmazsa WebSocket kapanır
- PCM ses akışı (ScriptProcessorNode ~80ms'de bir 8192 byte) sürekli veri gönderdiği için timeout olmaz
- Tünel URL'si her yeniden başlatmada DEĞİŞİR
- Telefonda HTTPS zorunlu (getUserMedia için) — cloudflared bunu sağlar

## Port Yönetimi
```bash
# Portu boşalt
fuser -k 8765/tcp

# Portta ne var kontrol
ss -tlnp | grep 8765
```
