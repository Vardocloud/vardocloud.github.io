---
name: file-retention
description: "File retention policy and auto-cleanup — temp_cleanup.py script, cron schedule, retention rules, safe/delete classification."
version: 1.0.0
metadata:
  hermes:
    tags: [disk, cleanup, retention, cache, temp, cron]
    category: devops
---

# File Retention & Auto-Cleanup

Vanitas'ın retention kuralları ve `temp_cleanup.py` scripti. Haftalık cron ile otomatik çalışır.

## Kullanım

```bash
# Disk raporu
python3 ~/.hermes/scripts/temp_cleanup.py --report

# Önizleme
python3 ~/.hermes/scripts/temp_cleanup.py --dry-run

# Temizlik
python3 ~/.hermes/scripts/temp_cleanup.py --force
```

## Retention Rules

### Build Artifacts (always clean, age ignored)

Patterns under `/tmp/`: pip-unpack-*, pip-metadata-*, chatterbox_test*, vision_test, markitdown-mcp, hermes-results/*, tmp*, hermes-snap-*.sh, hermes-cwd-*.txt, glaido_*.txt, karusel_*.pdf

### Age-Based Retention

| Location | Retention | Type |
|----------|-----------|------|
| `~/.hermes/audio_cache/` | 30 days | voice message cache |
| `~/.hermes/image_cache/` | 30 days | screenshot cache |
| `~/.hermes/cron/output/` | 30 days | job logs |
| `/tmp/` audio files (.wav) | 14 days | downloads |
| `/tmp/` packages (.deb) | 14 days | installers |
| `/tmp/` temp scripts (.sh) | 14 days | temporary |
| `/tmp/` videos (reel_*.mp4) | 7 days | downloads |

### Safe List (never touched)

- Python scripts in home directory (`karusel_*.py`, `scan_markets.py`, etc.)
- Shell scripts in home directory
- Hermes skills, plugins, scripts directories
- Hermes config, env, token files
- Git repos in home directory

## Cron

- **Job ID:** 97f19be6f7c6
- **Schedule:** Sunday 06:00
- **Mode:** no_agent (no LLM tokens)

## History

- **30 Jun 2026:** First run — 11.5 GB freed (537 items). chatterbox_test 6.2 GB, pip-unpack ~5 GB. /tmp from 12 GB to 345 MB.

## Drive Backup (Pending)

Current Google OAuth token has only `drive.readonly` scope. Need `drive.file` for uploads. Options:
1. Revoke + re-auth with broader scope
2. Install rclone as separate remote

## Pitfalls

- Safe list prevents accidental deletion of scripts and configs.
- Build artifacts have zero retention — they are always cleaned regardless of age.
- Container doesn't reboot, so /tmp is never auto-cleared. Retention cron is essential.
