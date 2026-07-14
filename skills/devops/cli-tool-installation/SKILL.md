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

## Verification

```bash
# Test from Hermes terminal — should find any installed CLI tool
bash -c 'which opencode && opencode --version'
bash -c 'which <tool> && <tool> --version'
```

## When to Use

Use this checklist when any CLI tool is found "command not found" from Hermes terminal but works in an SSH or Docker exec session:

1. Verify the tool is installed: `npm list -g <package>` or `pip list \| grep <tool>`
2. Check if PATH is the issue: `bash -c 'echo "$PATH"'` (compare with SSH session)
3. Apply the two-layer fix above
4. Verify: `bash -c 'which <tool>'`
