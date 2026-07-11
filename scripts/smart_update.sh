#!/bin/bash
# ═════════════════════════════════════════════════════════════
# 🔒 UPDATE SEAL (KATI KURAL) — Yalnızca EDEL yetkilendirebilir
#   Çalıştırmak için: EDEL=benimoğlum bash smart_update.sh
#   Aksi halde script anında çıkar, hiçbir işlem yapılmaz.
# ═════════════════════════════════════════════════════════════
if [ "${EDEL:-}" != "benimoğlum" ]; then
    echo "🔒 MÜHÜRLÜ (KATI KURAL): Hermes update yalnızca EDEL tarafından yetkilendirilebilir."
    echo "   İzin:    EDEL=benimoğlum bash smart_update.sh"
    echo "   Ret:     Bu mühür AGENTS.md'de tanımlı katı kurala tabidir."
    echo "   Yetkisiz erişim kaydedildi: $(date '+%Y-%m-%d %H:%M:%S')" >> "$HOME/.hermes/logs/unauthorized_update_attempts.log" 2>/dev/null || true
    exit 1
fi

# smart_update.sh — Safe Hermes update pipeline
# Called by /update quick command (config.yaml)
# Steps: snapshot -> git pull -> pip install -> restart -> wait -> restore -> restart -> verify
set -euo pipefail

export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus

LOG="$HOME/.hermes/logs/smart_update.log"
mkdir -p "$(dirname "$LOG")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"
}

send_alert() {
    local msg="$1"
    /home/ubuntu/.hermes/hermes-agent/venv/bin/python3 -c "
import requests
requests.post('https://api.telegram.org/bot7927784182:AAHes4QI2vR6m5mTJyJFfpyFOpEgoFH7Miyk/sendMessage', json={'chat_id': '6306976553', 'text': '"'$msg'"'})
" 2>/dev/null || true
}

SNAPSHOT_ID=""
GATEWAY_SERVICE="hermes-gateway.service"

cleanup_on_failure() {
    log "UPDATE FAILED - attempting rollback..."
    send_alert "Hermes update BASARISIZ - rollback yapiliyor..."

    if [ -n "$SNAPSHOT_ID" ] && [ -d "$HOME/.hermes/backups/snapshots/$SNAPSHOT_ID" ]; then
        SNAP="$HOME/.hermes/backups/snapshots/$SNAPSHOT_ID"
        log "Rolling back from snapshot: $SNAP"

        if [ -f "$SNAP/config.yaml" ]; then
            cp "$SNAP/config.yaml" "$HOME/.hermes/config.yaml"
            log "  Restored config.yaml"
        fi
        if [ -f "$SNAP/.env" ]; then
            cp "$SNAP/.env" "$HOME/.hermes/.env"
            chmod 600 "$HOME/.hermes/.env"
            log "  Restored .env"
        fi
        for f in SOUL.md AGENTS.md; do
            if [ -f "$SNAP/$f" ]; then
                cp "$SNAP/$f" "$HOME/.hermes/$f"
                log "  Restored $f"
            fi
        done

        systemctl --user restart "$GATEWAY_SERVICE" 2>/dev/null || true
        log "  Gateway restarted with rollback config"
    else
        log "No snapshot available for rollback!"
    fi

    send_alert "Hermes update rollback tamamlandi. Manuel kontrol gerekli."
    exit 1
}

trap cleanup_on_failure ERR

# ─── Step 1: Pre-update snapshot ─────────────────────────────
log "=== SMART UPDATE START ==="
log "Step 1: Creating pre-update snapshot..."
bash "$HOME/.hermes/scripts/backup_snapshot.sh"
SNAPSHOT_ID=$(ls -t "$HOME/.hermes/backups/snapshots/" | head -1)
log "  Snapshot: $SNAPSHOT_ID"

# ─── Step 2: Git pull ──────────────────────────────────────────
log "Step 2: git pull..."
cd "$HOME/.hermes/hermes-agent"
BEFORE_VERSION=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
git pull
AFTER_VERSION=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
log "  Version: $BEFORE_VERSION -> $AFTER_VERSION"

if [ "$BEFORE_VERSION" = "$AFTER_VERSION" ]; then
    log "  No code changes. Skipping rest of update."
    send_alert "Hermes update: Already up to date ($AFTER_VERSION)"
    exit 0
fi

# ─── Step 3: pip install ──────────────────────────────────────
log "Step 3: pip install -e . ..."
pip install -e . 2>&1 | tail -5 | tee -a "$LOG"

# ─── Step 4: Restart gateway (triggers migration) ──────────────
log "Step 4: Restarting gateway (triggers _config_version migration)..."
systemctl --user restart "$GATEWAY_SERVICE"

# ─── Step 5: Wait for migration ─────────────────────────────────
log "Step 5: Waiting 10s for migration to complete..."
sleep 10

# ─── Step 6: Restore config ────────────────────────────────────
log "Step 6: Restoring config from golden values..."
python3 "$HOME/.hermes/scripts/restore_config.py" --restore

# ─── Step 7: Restart gateway (with restored config) ────────────
log "Step 7: Restarting gateway with restored config..."
systemctl --user restart "$GATEWAY_SERVICE"
sleep 5

# ─── Step 8: Post-update health checks ─────────────────────────
log "Step 8: Running post-update health checks..."
bash "$HOME/.hermes/scripts/post-update-fix.sh"

# ─── Step 9: Verification ─────────────────────────────────────
log "Step 9: Running system verification..."
bash "$HOME/.hermes/scripts/verify_system.sh" 2>&1 | tee -a "$LOG"
VERIFY_EXIT=$?

# ─── Step 10: Final config check ───────────────────────────────
log "Step 10: Final config alignment check..."
python3 "$HOME/.hermes/scripts/restore_config.py" --check
CHECK_EXIT=$?

# ─── Summary ───────────────────────────────────────────────────
if [ $VERIFY_EXIT -eq 0 ] && [ $CHECK_EXIT -eq 0 ]; then
    log "=== UPDATE SUCCESSFUL ==="
    send_alert "Hermes update basarili: $BEFORE_VERSION -> $AFTER_VERSION"
else
    log "=== UPDATE COMPLETED WITH WARNINGS ==="
    send_alert "Hermes update tamamlandi (uyarilar var): $BEFORE_VERSION -> $AFTER_VERSION"
fi

log "=== SMART UPDATE END ==="