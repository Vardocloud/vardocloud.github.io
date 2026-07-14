---
name: cli-tool-installation
description: "Installation, PATH configuration, and environment setup for CLI tools (opencode, claude-code, codex, etc.) in Hermes terminal environment."
version: 1.0.0
created_by: agent
platforms: [linux, macos]
---

# CLI Tool Installation & PATH Setup

Generic guide for installing CLI tools and making them discoverable in Hermes terminal sessions.

## The Problem

Hermes `terminal()` tool runs commands via **non-interactive, non-login bash**. In this mode:

- Shell init files like `~/.bashrc` and `~/.profile` are **not read** by default
- This means PATH additions from those files are **invisible** to Hermes terminal
- Tools installed via npm/pip appear as "command not found" even when correctly installed

## The Mechanism

Bash starts in different modes depending on how it is invoked:

| Mode | Init files read | Hermes? |
|------|----------------|---------|
| Interactive login | `~/.profile`, `~/.bash_profile` | ❌ |
| Interactive non-login | `~/.bashrc` | ❌ |
| Non-interactive (sh/ssh) | `BASH_ENV` env var | ✅ Hermes uses this |

Hermes spawns bash in **non-interactive** mode. The key config point is the `BASH_ENV` environment variable — bash reads this file on startup for EVERY non-interactive invocation.

## The Fix (Two Layers)

### Layer 1 — Move PATH exports before `.bashrc`'s guard

Ubuntu's default `.bashrc` exits early when non-interactive:

```bash
case $- in
    *i*) ;;
      *) return;;  # ← non-interactive shells never reach bottom of file
esac
```

Restructure so PATH exports come BEFORE this guard:

```bash
# ~/.bashrc (top section)
export PATH="$HOME/.npm-global/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac
```

### Layer 2 — Set BASH_ENV

Set the `BASH_ENV` environment variable so Hermes' non-interactive bash sources the rc file:

```bash
BASH_ENV=$HOME/.bashrc
```

Add this to wherever Hermes reads environment variables (e.g., Hermes `.env` file or systemd service environment).

## Container Restart — Binary Exists but "Command Not Found"

After a Docker container restart, tools may appear "silently deleted" when they are actually intact but PATH is misconfigured.

### Post-Restart Diagnostic Sequence

```bash
# 1. Check container uptime (when did it restart?)
ps -p 1 -o etime=

# 2. Check PATH
echo "$PATH"

# 3. Check if ~/.hermes/bin is in PATH
echo "$PATH" | tr ':' '\n' | grep -q '\.hermes/bin' && echo "IN PATH" || echo "NOT IN PATH"

# 4. Locate binaries directly (they may still exist on disk)
ls -la /home/ubuntu/.hermes/bin/bw 2>/dev/null   # Bitwarden CLI
ls -la /home/ubuntu/.hermes/bin/bws 2>/dev/null   # Bitwarden Secrets
ls -la /home/ubuntu/.hermes/bin/cloudflared 2>/dev/null

# 5. Check if key background services survived the restart
ps aux | grep "bw serve"               # Bitwarden server (port 8087)
ps aux | grep "hermes-gateway"         # Hermes gateway

# 6. Verify Hermes-loaded secrets (PEXELS, GROQ, NVIDIA, etc.)
hermes --version  # Shows "applied N secrets" with key names
env | grep "PEXELS_API_KEY"   # Confirm specific keys are loaded
```

### Common Patterns

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `bw`/`bws` not found, but binary in `~/.hermes/bin/` | `~/.hermes/bin` not in PATH after restart | Add to `.bashrc` before the non-interactive guard |
| Key background process (bw-serve) alive | Container restart preserved the process | PATH issue only — binaries intact |
| Key background process dead | Full container restart or entrypoint failure | Check entrypoint.sh logs |
| `hermes --version` shows secrets | Bitwarden session is valid | Only PATH missing — use full path |

### The `~/.hermes/bin` Binary Directory

Hermes stores custom CLI binaries in `~/.hermes/bin/`. This directory should ALWAYS be in PATH:

```bash
# Must be placed BEFORE the non-interactive guard in ~/.bashrc
export PATH="$HOME/.hermes/bin:$PATH"
```

Typical contents:
```
~/.hermes/bin/
├── bw            (116MB) — Bitwarden CLI
├── bws           (12MB)  — Bitwarden Secrets Manager
├── cloudflared   (39MB)  — Cloudflare Tunnel
└── tirith        (22MB)  — (custom tool)
```

### Verify PATH on Next Shell Start

After fixing `.bashrc`, test with a non-interactive shell (Hermes mode):
```bash
bash -c 'which bw && which bws'
```

## Verification

```bash
# Test from Hermes terminal — should find any installed CLI tool
bash -c 'which opencode && opencode --version'
bash -c 'which <tool> && <tool> --version'

# Also verify ~/.hermes/bin tools
bash -c 'which bw && bw --version 2>&1 | head -3'
bash -c 'which bws && bws --version 2>&1'
```

## When to Use

Use this checklist when any CLI tool is found "command not found" from Hermes terminal but works in an SSH or Docker exec session:

1. **Check if container restarted recently:** `ps -p 1 -o etime=` — if uptime < today, PATH may be the issue
2. Verify the tool is installed on disk: `ls -la ~/.hermes/bin/<tool>` or `npm list -g <package>` or `pip list \| grep <tool>`
3. Check if PATH is the issue: `bash -c 'echo "$PATH"'` (compare with SSH session)
4. Check `~/.hermes/bin` presence in PATH: `echo "$PATH" | tr ':' '\n' | grep '\.hermes/bin'`
5. Apply the two-layer fix above
6. Verify: `bash -c 'which <tool>'`
