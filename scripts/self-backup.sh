#!/bin/bash
# scripts/self-backup.sh
# Vanitas'in kendi içinde çalıştırabileceği self-recovery script.
# Container içinden çağrılır: docker exec vanatis-hermes bash /home/ubuntu/.hermes/scripts/self-backup.sh
#
# Ne yapar:
#   1. Kritik config + state dosyalarını tar'lar
#   2. backups/ altına timestamp'li snapshot koyar
#   3. (Opsiyonel) GitHub releases'e push eder — BWS_ACCESS_TOKEN veya GH token gerekir
#
# "Kendini yedekle" veya "kendini kurtar" komutunda çalıştırılır.

set -e

HERMES_DIR="${HOME}/.hermes"
BACKUP_DIR="${HERMES_DIR}/backups"
TS=$(date +%Y%m%d_%H%M%S)
SNAPSHOT="${BACKUP_DIR}/vanitas-snapshot-${TS}.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "=== Vanitas Self-Backup ==="
echo "Creating snapshot: $SNAPSHOT"

cd "$HERMES_DIR"

# Pack critical files only (not caches/logs)
tar czf "$SNAPSHOT" \
    --exclude='bin' \
    --exclude='bw-cli' \
    --exclude='node_modules' \
    --exclude='audio_cache' \
    --exclude='.codegraph' \
    --exclude='image_cache' \
    --exclude='chrome_profile_notebooklm' \
    --exclude='cache' \
    --exclude='document_cache' \
    --exclude='downloaded_files' \
    --exclude='context_index' \
    --exclude='logs' \
    --exclude='backups' \
    --exclude='backup-vanitas-*' \
    --exclude='state-snapshots' \
    --exclude='secrets' \
    --exclude='.env' \
    --exclude='.env.bak*' \
    --exclude='*.bak' \
    --exclude='*.bak.*' \
    --exclude='config.yaml.backup*' \
    --exclude='config.yaml.bak*' \
    --exclude='SOUL.md.bak*' \
    --exclude='gateway.lock' \
    --exclude='gateway.pid' \
    --exclude='auth.lock' \
    --exclude='processes.json' \
    --exclude='gateway_state.json' \
    --exclude='gateway_voice_mode.json' \
    --exclude='.restart_last_processed.json' \
    --exclude='.update_check' \
    --exclude='.scratch_tip_shown' \
    --exclude='.hermes_history' \
    --exclude='pollinations_status' \
    --exclude='models_dev_cache.json' \
    --exclude='provider_models_cache.json' \
    --exclude='ollama_cloud_models_cache.json' \
    --exclude='context_length_cache.yaml' \
    --exclude='package.json' \
    --exclude='package-lock.json' \
    --exclude='.channel_directory*.tmp' \
    --exclude='profiles/*/audio_cache' \
    --exclude='profiles/*/image_cache' \
    --exclude='profiles/*/logs' \
    --exclude='profiles/*/sandboxes' \
    --exclude='profiles/*/sessions' \
    --exclude='cron/output' \
    --exclude='cron/watchdog.log' \
    --exclude='cron/watchdog_cron.log' \
    --exclude='cron/keepalive.log' \
    --exclude='cron/health_status.txt' \
    --exclude='cron/watchdog.lock' \
    --exclude='cron/keepalive_count' \
    --exclude='cron/watchdog_count' \
    --exclude='cron/.tick.lock' \
    config.yaml \
    SOUL.md \
    MEMORY.md \
    AGENTS.md \
    USER.md \
    MIGRATION.md \
    state.db* \
    sessions.db* \
    response_store.db* \
    kanban.db* \
    cron.db* \
    channel_directory.json \
    scripts/ \
    tools/ \
    skills/ \
    agents/ \
    prompts/ \
    memories/ \
    golden/ \
    hooks/ \
    platforms/ \
    kanban/ \
    pairing/ \
    cron/jobs.json \
    cron/jobs.db* \
    profiles/ \
    2>/dev/null || true

SIZE=$(du -h "$SNAPSHOT" | cut -f1)
echo ""
echo "=== Snapshot Created ==="
echo "File: $SNAPSHOT ($SIZE)"
echo ""

# Optional: GitHub release push
if [ -n "$GITHUB_TOKEN" ] && command -v gh >/dev/null 2>&1; then
    echo "Pushing to GitHub releases..."
    REPO="${VANITAS_GH_REPO:-torkucloud/vanitas-docker}"
    gh release create "snapshot-${TS}" "$SNAPSHOT" \
        --repo "$REPO" \
        --title "Vanitas Snapshot ${TS}" \
        --notes "Self-backup snapshot created by Vanitas at $(date -u)" \
        2>/dev/null && echo "GitHub release created: snapshot-${TS}" || echo "GitHub push failed (non-critical)"
else
    echo "GitHub push skipped (no GITHUB_TOKEN or gh CLI)"
    echo "Snapshot is local at: $SNAPSHOT"
fi

echo ""
echo "=== Recovery Instructions ==="
echo "To restore on a new VM:"
echo "  1. git clone https://github.com/torkucloud/vanitas-docker.git"
echo "  2. cp $SNAPSHOT vanitas-docker/data/hermes/"
echo "  3. cd vanitas-docker"
echo "  4. tar xzf data/hermes/vanitas-snapshot-${TS}.tar.gz -C data/hermes/"
echo "  5. cp .env.template .env && nano .env"
echo "  6. ./scripts/deploy-cloud.sh"