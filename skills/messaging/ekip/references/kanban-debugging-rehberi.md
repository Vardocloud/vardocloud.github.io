# Kanban Sistematik Debugging Rehberi

> Oluşturma: 6 Haz 2026 — Kanban board incelemesi sırasında bulunan 6 sorun ve debugging metodolojisi.

## Sistematik Debugging Adımları

Kanban'da "stuck", "blocked", "running ama ilerlemiyor" durumunda sırasıyla:

### 1. Board Durumu
```bash
hermes kanban list                    # Tüm task'lar
hermes kanban list --status running   # Sadece running
hermes kanban list --status blocked   # Sadece blocked
hermes kanban stats                   # Özet: ready/running/blocked/done sayıları
```

### 2. Task Detayı
```bash
hermes kanban show <task_id>          # Task body, claim, log
hermes kanban log <task_id>           # Detaylı event log
hermes kanban runs                    # Aktif worker process'leri
hermes kanban assignees               # Hangi profil hangi task'ları almış
```

### 3. Worker Process Kontrolü
```bash
ps aux | grep -E "hermes.*kanban"     # Kanban worker process'leri
journalctl --user -u hermes-gateway --since "5 min ago" | grep -i error
```

### 4. Gateway Sağlığı
```bash
hermes gateway status                 # Gateway durumu
systemctl --user status hermes-gateway
```

### 5. Proxy Sağlığı
```bash
ss -tlnp | grep -E "19998|19999"      # Proxy port'ları açık mı?
curl -s http://127.0.0.1:19998/v1/models | head -c 200  # OpenCode Go canlı mı?
```

### 6. Profil Konfigürasyonu
```bash
cat ~/.hermes/profiles/<profile>/config.yaml  # Model, provider doğru mu?
grep -A 15 custom_providers ~/.hermes/profiles/<profile>/config.yaml  # Provider block var mı?
```

## 6 Yaygın Kanban Sorunu (6 Haz 2026 bulguları)

### 1. Context Engine Eksik: `context-mode-compressor` bulunamadı
**Belirti:** Log'da `Context engine 'context-mode-compressor' not found — falling back to built-in compressor`
**Etki:** Tüm worker'lar built-in compressor'a düşüyor, verimsiz.
**Çözüm:** MCP sunucusu kurulu değilse `pip install context-mode-mcp`, config.yaml'da `context_engine: context-mode-compressor` tanımlı olduğundan emin ol.

### 2. Skill Güvenlik Taraması: Agent-created skill'ler bloke ediliyor
**Belirti:** `Security scan blocked this skill (Requires confirmation (agent-created source + dangerous verdict, 2 findings))`
**Etki:** `kanban-worker` ve `kanban-orchestrator` skill'leri yüklenemiyor, worker'lar boş başlıyor.
**Çözüm:** Skill'leri `hermes curator approve <skill-name>` ile onayla. Veya güvenlik taramasını o skill için devre dışı bırak.

### 3. Proxy Aşırı Yüklenme: 6+ eşzamanlı worker → APITimeoutError
**Belirti:** `APITimeoutError ... provider=custom base_url=http://127.0.0.1:19998/v1 model=deepseek-v4-flash`
**Etki:** Worker'ların bir kısmı timeout, diğerleri çalışıyor — tutarsız.
**Çözüm:** `hermes kanban dispatch --max 3` ile eşzamanlılığı sınırla. Proxy tek thread'li olduğu için 6+ long-lived streaming bağlantıyı kaldıramaz.

### 4. Credential Provider Uyuşmazlığı: `custom` vs `custom:opencode-go`
**Belirti:** `Unknown provider 'custom'` veya credential çözümlenemiyor.
**Etki:** Worker başlatılamıyor.
**Çözüm:** Profil config'inde `provider: custom:opencode-go` olduğundan VE `custom_providers` block'unun kopyalandığından emin ol.

### 5. Worker CLI Syntax Hatası: `--title` flag'i geçersiz
**Belirti:** `hermes kanban create: unrecognized arguments: --title`
**Etki:** Worker task oluşturamıyor.
**Çözüm:** `title` **pozisyonel** argümandır: `hermes kanban create "TITLE" --body "..."` doğru. `--title "..."` yanlış.

### 6. Gateway Drain Timeout: Restart sırasında worker'lar asılı kalıyor
**Belirti:** Gateway restart sonrası task'lar `running` durumunda takılı, `kanban runs` zombie process gösteriyor.
**Etki:** Worker'lar gateway'e rapor veremiyor, task'lar stuck.
**Çözüm:** Restart öncesi tüm running task'ları `hermes kanban reclaim <task_id>` ile geri al, board temizlendikten sonra restart et. Restart sonrası yeniden dispatch.
