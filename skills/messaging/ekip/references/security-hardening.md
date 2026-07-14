# Hermes Güvenlik Sertleştirme (Hardening)

31 Mayıs 2026 — OpenClaw-Security NotebookLM analizinden uyarlanmıştır.

## Uygulanan Önlemler

### 1. Docker Hardening (open-webui)
```bash
docker run -d --name open-webui \
  --cap-drop=ALL --cap-add=NET_BIND_SERVICE \
  --security-opt=no-new-privileges \
  ...
```

**Not:** non-root (`--user 1000:1000`) ve `--read-only` open-webui'de env hatası verdi — ayrıca araştırılacak.

### 2. Prompt Injection Savunması
- Harici içerikler `<user_data>...</user_data>` ile sarmalanır
- "system:", "assistant:", "ignore previous rules" → SUSPICIOUS → doğrulama sorulur
- config.yaml, .env, token içeriği ASLA kullanıcıya gösterilmez

### 3. Config Değişiklikleri (31 Mayıs)
- `delegation.inherit_mcp_toolsets: false` — Pollinations alt ajanlar gereksiz MCP araçlarını almaz
- `fail2ban`: sshd + recidive, 24sa + 7gün ban
- UFW: `80.94.92.0/24`, `80.94.95.0/24`, `45.148.10.0/24` bloklandı
- Port 3000: UFW deny + process kill

### 4. Supply Chain (pip)
- 25 paket güncellendi (cryptography, aiohttp, fastapi, uvicorn, boto3, vb.)
- pnpm audit: 0 vulnerability
- Dayanıklılık: her güncelleme sonrası gateway restart testi yapıldı

## Kaynak
- NotebookLM: "OpenClaw-Security" (ID: 2372503c-5243-4a19-b3f8-693520068b76, 43 source)
- ClawKeeper, SecAlign, TaskForge, RAK çerçevesi
