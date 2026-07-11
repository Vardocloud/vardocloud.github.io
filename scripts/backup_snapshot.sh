#!/bin/bash
# backup_snapshot.sh — Full system snapshot for update resilience
# Usage: bash ~/.hermes/scripts/backup_snapshot.sh
set -euo pipefail

SNAP_DIR="$HOME/.hermes/backups/snapshots/$(date +%Y-%m-%d_%H%M%S)"
mkdir -p "$SNAP_DIR"

log() { echo "[$(date +%H:%M:%S)] $1"; }

log "Creating snapshot in $SNAP_DIR"

# Core config files
for f in config.yaml .env SOUL.md AGENTS.md; do
    src="$HOME/.hermes/$f"
    if [ -f "$src" ]; then
        cp "$src" "$SNAP_DIR/"
        log "  Backed up $f"
    fi
done

# Golden config (restore reference)
if [ -f "$HOME/.hermes/scripts/golden_config.yaml" ]; then
    cp "$HOME/.hermes/scripts/golden_config.yaml" "$SNAP_DIR/"
    log "  Backed up golden_config.yaml"
fi

# Systemd services
mkdir -p "$SNAP_DIR/systemd"
for f in "$HOME/.config/systemd/user"/hermes-*.service \
         "$HOME/.config/systemd/user"/xvfb-*.service \
         "$HOME/.config/systemd/user"/chrome-*.service; do
    [ -f "$f" ] && cp "$f" "$SNAP_DIR/systemd/"
done
if [ -d "$HOME/.config/systemd/user/hermes-gateway.service.d" ]; then
    cp -r "$HOME/.config/systemd/user/hermes-gateway.service.d" "$SNAP_DIR/systemd/"
fi

# Crontab
crontab -l > "$SNAP_DIR/crontab.txt" 2>/dev/null || true
log "  Backed up crontab"

# Symlinks
mkdir -p "$SNAP_DIR/symlinks"
for bin in nlm notebooklm-mcp hermes; do
    if [ -L "$HOME/.local/bin/$bin" ]; then
        readlink -f "$HOME/.local/bin/$bin" > "$SNAP_DIR/symlinks/$bin.txt"
        ls -la "$HOME/.local/bin/$bin" >> "$SNAP_DIR/symlinks/$bin.txt"
    fi
done

# Scripts
mkdir -p "$SNAP_DIR/scripts"
for s in restore_config.py smart_update.sh verify_system.sh backup_snapshot.sh \
         post-update-fix.sh infra.sh; do
    for dir in "$HOME/.hermes/scripts" "$HOME"; do
        if [ -f "$dir/$s" ]; then
            cp "$dir/$s" "$SNAP_DIR/scripts/"
            break
        fi
    done
done
# All custom scripts
mkdir -p "$SNAP_DIR/scripts_all"
if [ -d "$HOME/.hermes/scripts" ]; then
    for s in "$HOME/.hermes/scripts"/*.py "$HOME/.hermes/scripts"/*.sh; do
        [ -f "$s" ] && cp "$s" "$SNAP_DIR/scripts_all/"
    done
    log "  Backed up all scripts"
fi
# Auth scripts
for s in refresh_auth.sh browser_manager.sh; do
    [ -f "$HOME/$s" ] && cp "$HOME/$s" "$SNAP_DIR/scripts/"
done

# Cron scripts
if [ -d "$HOME/.hermes/cron" ]; then
    cp -r "$HOME/.hermes/cron" "$SNAP_DIR/cron"
    log "  Backed up cron scripts"
fi

# Hooks
if [ -d "$HOME/.hermes/hooks" ]; then
    cp -r "$HOME/.hermes/hooks" "$SNAP_DIR/hooks"
fi

# Skills
if [ -d "$HOME/.hermes/skills" ]; then
    cp -r "$HOME/.hermes/skills" "$SNAP_DIR/skills"
    log "  Backed up skills"
fi

# NLM auth data
mkdir -p "$SNAP_DIR/nlm/profiles"
cp -r "$HOME/.notebooklm-mcp-cli/profiles/"* "$SNAP_DIR/nlm/profiles/" 2>/dev/null || true
cp -r "$HOME/.notebooklm/profiles/"* "$SNAP_DIR/nlm/profiles/" 2>/dev/null || true

# Manifest: file list + checksums
(cd "$SNAP_DIR" && find . -type f -exec sha256sum {} \; > manifest.txt 2>/dev/null || true)

# Service status snapshot
{
    echo "=== Service Status $(date) ==="
    systemctl --user status hermes-gateway 2>/dev/null | head -5 || true
    echo "---"
    systemctl --user status hermes-pollinations-proxy 2>/dev/null | head -5 || true
    echo "---"
    systemctl --user status hermes-dashboard 2>/dev/null | head -5 || true
    echo "=== Disk ==="
    df -h / | tail -1
    echo "=== Hermes Version ==="
    hermes --version 2>/dev/null || echo "unknown"
} > "$SNAP_DIR/status.txt" 2>/dev/null || true

# Retention: keep 30 days
find "$HOME/.hermes/backups/snapshots" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true

log "Snapshot complete: $SNAP_DIR"
log "Files: $(wc -l < "$SNAP_DIR/manifest.txt" 2>/dev/null || echo '?') files, $(du -sh "$SNAP_DIR" 2>/dev/null | cut -f1)"