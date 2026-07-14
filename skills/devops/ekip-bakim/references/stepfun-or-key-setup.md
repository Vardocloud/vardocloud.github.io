# StepFun OpenRouter Key — Investigation Notes

**Date:** 2026-06-11
**Context:** Edel reported StepFun `/tmp/.or_key` not found error. Investigated whether key existed somewhere and was lost during config changes.

## Finding

The OpenRouter API key (`sk-or-v1-...`) was **never stored** in the system at any point. Not in:

- `.env` (current or any backup — checked 5+ copies)
- `config.yaml` (current or backup)
- Any token/key files under `~/.hermes/`
- Log files (only "OPENROUTER_API_KEY not set" warnings)
- Cron output or state snapshots

The `/tmp/.or_key` file was planned in skill documentation (`sohbet` skill) but the first-time setup step was **never executed**.

## Why It Was Never Configured

The `sohbet` skill documented the StepFun Değerlendirici setup as a **plan**, but the actual execution step was missed. The key was expected at `/tmp/.or_key` but no script, cron job, or manual step ever created this file.

## Setup Command

```bash
echo 'sk-or-v1-...tam-key...' > /tmp/.or_key && chmod 600 /tmp/.or_key
```

Key from https://openrouter.ai/keys (free tier sufficient for StepFun 3.7 Flash).

## Lesson for Future

When documenting a credential-dependent feature in a skill:
1. Add a readiness check step (e.g., "verify `/tmp/.or_key` exists")
2. Add a first-time setup command block
3. Add a verification step after setup
4. Do NOT assume setup was done because the docs describe it
