# Memory

## Server
- Docker Local (Windows PC), x86_64 container, Ubuntu 22.04, 6GB RAM limit
- Host: 127.0.0.1 (Gateway :8642, SSH :2222) | Tailscale: auth pending
- Timezone: Europe/Istanbul (UTC+3)
- Timezone: Europe/Istanbul (UTC+3)

## Disk Layout
- Docker volume: C:\VanitasDocker\data → /home/ubuntu (mounted)
- Container disk: limited by host
- ~/.hermes = /home/ubuntu/.hermes (volume mount from host)

## Agent Infrastructure
- Hermes v2026.6.5, Python 3.11, Docker container
- Gateway: 127.0.0.1:8642, Docker health check, auto-restart
- Primary model: DeepSeek V4 Pro (1M context, custom:opencode-go proxy :19998)
- Fallback: OpenCode Go qwen3.7-max -> Mistral mistral-large (2-level)
- Delegation: OpenCode Go deepseek-v4-flash (default orchestrator)
- Auxiliary: Pollinations gemma via UA proxy (:19999) (vision, web_extract, approval, compression, session_search)
- Approval: smart mode (LLM-classified dangerous commands)
- Compression: threshold 0.20 (~200K tokens, DeepSeek V4 Pro 1M context)
- MCP: NotebookLM (disabled - pending install), context-mode (disabled - pending install)
- Website blocklist: enabled (malicious TLDs, URL shorteners, paste sites, IP loggers)

## Provider Architecture
| Provider | Type | Endpoint | Auth |
|----------|------|----------|------|
| custom:opencode-go | Proxy (port 19998) | http://127.0.0.1:19998/v1 | OPENCODE_GO_API_KEY |
| custom:Pollinations | UA Proxy (port 19999) | http://127.0.0.1:19999/v1 | POLLINATIONS_API_KEY |
| opencode-zen | Built-in | https://opencode.ai/zen/v1 | OPENCODE_ZEN_API_KEY |
| Mistral | API | https://api.mistral.ai/v1 | MISTRAL_API_KEY |

## Kanban Multi-Agent Profiles
| Profile | Model | Provider | Purpose | Fallback |
|---------|-------|----------|---------|----------|
| analist | mimo-v2.5-free | opencode-zen | Research analyst | deepseek-v4-flash-free / opencode-zen |
| kodcu | minimax-m3-free | opencode-zen | Software engineer | deepseek-v4-flash-free / opencode-zen |
| yardimci | gemma | custom:Pollinations | Quick helper | deepseek-v4-flash / custom:opencode-go |
| yazar | gpt-5.4-mini | custom:Pollinations | Turkish content writer | deepseek-v4-flash / custom:opencode-go |

- Kanban orchestrator: default profile (deepseek-v4-pro)
- auto_decompose: true, auto_decompose_per_tick: 3

## OpenCode Zen Free Models (verified working)
- mimo-v2.5-free, minimax-m3-free, deepseek-v4-flash-free
- nemotron-3-super-free, nemotron-3-ultra-free
- NOTE: qwen3.6-plus-free appears in /v1/models but returns 403 (not usable)

## OpenCode Go Models (verified working)
- deepseek-v4-pro, deepseek-v4-flash, glm-5, glm-5.1
- kimi-k2.5, kimi-k2.6, minimax-m2.5, minimax-m2.7, minimax-m3, qwen3.7-max

## Pollinations Models (verified working, no tool calling)
- gemma, glm, gpt-5.4-mini, minimax, openai

## Voice (TTS/STT)
- TTS: Pollinations ElevenLabs v3, voice=bella, OpenAI-compatible endpoint
- STT: Local faster-whisper v1.2.1, model=small
- Telegram voice modes: /voice off (default), /voice on (voice to voice), /voice tts (all replies voice)
- Voice mode state: ~/.hermes/gateway_voice_mode.json
- OpenWebUI TTS: Pollinations endpoint, model=elevenlabs, voice=bella
- OpenWebUI STT: Whisper small model
- Edel prefers text replies by default; uses /voice on for voice conversations

## Google Calendar Integration
- OAuth2 authenticated (Google Workspace skill)
- google_api.py for calendar create/list/delete
- Calendar events with built-in reminders bypass Azure content filtering
- Daily calendar context: 08:30 cron job fetches events for context

## Services
- Open WebUI: Docker, port 8080, host network
- fail2ban: 3 failures = 2 hour ban
- logrotate: 7 days, 50MB max
- NotebookLM auth: refresh token via CDP auto-renewal
- Systemd services: hermes-gateway, opencode-go-proxy (:19998), pollinations-proxy (:19999)
- hermes-dashboard: web dashboard (systemd)

## Security
- Docker: cap_drop=ALL, no-new-privileges:false, DAC_OVERRIDE+FOWNER+SYS_CHROOT added
- SSH: key-only (ed25519), port 2222, StrictModes no, UsePAM yes
- Windows Firewall: Allow Gateway Local (8642) + Allow SSH Local (2222)
- All sensitive files: 600 permissions
- Secret redaction: enabled (redact_secrets: true)
- Website blocklist: enabled

Telegram voice/TTS/STT settings are in ~/.hermes/AGENTS.md, specifically the /voice off|on|tts|status quick commands section.

Polymarket starting strategy: AI generates signals (mode B), human approves trades; target category is crypto price/price-range markets. Test/validation sequence: 14 days paper+shadow; max drawdown stop threshold 25%. Time scale: first 5 days 15-min mode, if performance weak then switch to 30-60 min mode on days 11-14. Trade metric focus: net PnL (pocket profit) + drawdown. Risk setting: 2% portfolio risk per trade and confidence score threshold balanced (mode B).

## Cloud Migration Infrastructure (2026-06-20)
- GitHub repo: `torkucloud/vanitas-docker` (taşınabilir kod)
- `.gitignore`: secrets, cache, backups, db'ler, logs hariç — sadece kod/config kalır
- `scripts/pack-data.sh`: PC'de `vanitas-data-portable.tar.gz` üretir (~80MB)
  - Dahil: state.db, profiles/, cron/jobs.json, kanban.db, scripts/, tools/, skills/, config.yaml
  - Hariç: bin/, node_modules/, audio_cache/, logs/, backups/, secrets/, .env
- `scripts/deploy-cloud.sh`: Cloud VM'de unpack + build + up + health check
- `scripts/self-backup.sh`: Container içinden snapshot → backups/ (opsiyonel GitHub release)
- `docker-compose.cloud.yml`: Port 127.0.0.1, resource env var'dan okur
- `.env.template`: Tüm env var'lar placeholder ile
- `vanitas.sh`: Linux yönetim scripti (vanitas.ps1 eşdeğeri)
- `MIGRATION.md`: Vanitas'in okuyabileceği taşınma rehberi
- Tailscale: Cloud VM'de `docker exec vanatis-tailscale tailscale up` ile bağlan
- BWS: `.env`'de BWS_ACCESS_TOKEN varsa 32 secret açılışta otomatik uygulanır
