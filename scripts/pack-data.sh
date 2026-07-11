#!/bin/bash
# scripts/pack-data.sh
# Vanitas'in taşınabilir data paketini üretir.
# PC'de çalışır. Çıktı: vanitas-data-portable.tar.gz (~80MB)
#
# Dahil:
#   - state.db (ana session, 30MB)
#   - profiles/ (tüm profil state.db'leri, memories, plans)
#   - cron/jobs.json + cron/jobs.db (cron config)
#   - kanban.db (kanban board)
#   - channel_directory.json (Telegram channel map)
#   - response_store.db (agent response cache)
#
# Hariç (rebuild edilir/gerekmez):
#   - bin/, bw-cli/, node_modules/ → Dockerfile'da indirilir
#   - audio_cache/, .codegraph/, image_cache/ → cache
#   - logs/, chrome_profile_notebooklm/ → gerekmez
#   - backups/ → gerekmez
#   - secrets/, .env → MANUEL transfer (güvenlik)

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$ROOT_DIR/data/hermes"
OUTPUT="$ROOT_DIR/vanitas-data-portable.tar.gz"

cd "$DATA_DIR"

echo "=== Vanitas Portable Data Packager ==="
echo "Source: $DATA_DIR"
echo "Output: $OUTPUT"
echo ""

# Check critical files exist
CRITICAL_FILES=(
    "config.yaml"
    "state.db"
    "SOUL.md"
    "MEMORY.md"
    "AGENTS.md"
)

for f in "${CRITICAL_FILES[@]}"; do
    if [ ! -f "$f" ]; then
        echo "WARNING: $f not found — migration may be incomplete"
    fi
done

# Create temp manifest
MANIFEST=$(mktemp)
cat > "$MANIFEST" <<EOF
# Vanitas Data Package — $(date -u +%Y-%m-%dT%H:%M:%SZ)
# Created by: pack-data.sh
#
# Contents:
#   - config.yaml, SOUL.md, MEMORY.md, AGENTS.md, USER.md, MIGRATION.md
#   - state.db + state.db-wal + state.db-shm
#   - profiles/ (state.db, memories, plans, skills, hooks — NOT caches/logs)
#   - cron/jobs.json, cron/jobs.db
#   - kanban.db + kanban.db-shm + kanban.db-wal
#   - scripts/ (all Python/bash scripts)
#   - tools/ (MCP server scripts)
#   - skills/ (all Hermes skills)
#   - agents/ (agent definitions)
#   - prompts/ (prompt templates)
#   - memories/ (MEMORY.md, USER.md)
#   - golden/ (jobs.json, golden_commit.txt, scripts/)
#   - hooks/ (post-update.sh)
#   - platforms/ (pairing)
#   - kanban/ (kanban board files)
#   - channel_directory.json
#   - response_store.db*
#   - sessions.db*
#   - cron.db*
#   - pairring/ (if exists)
#
# NOT included (rebuild or manual transfer):
#   - bin/, bw-cli/ → Dockerfile downloads
#   - node_modules/ → npm install
#   - audio_cache/, image_cache/, .codegraph/ → cache
#   - logs/, chrome_profile_notebooklm/ → not needed
#   - backups/ → not needed
#   - secrets/ → MANUAL (contains .gpg, tokens)
#   - .env → MANUAL (contains API keys)
#   - data/local/ → pip installs, rebuild
#   - data/projects/ → project-specific, transfer separately if needed
EOF

# Pack everything
echo "Packing..."
tar czf "$OUTPUT" \
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

# Append manifest
echo ""
echo "Appending manifest..."
tar rf "${OUTPUT%.gz}" "$MANIFEST" 2>/dev/null || true

# Get size
if [ -f "$OUTPUT" ]; then
    SIZE=$(du -h "$OUTPUT" | cut -f1)
    echo ""
    echo "=== DONE ==="
    echo "Package: $OUTPUT ($SIZE)"
    echo ""
    echo "Next steps:"
    echo "  1. git push (code to GitHub)"
    echo "  2. scp $OUTPUT user@cloud-vm:~/"
    echo "  3. On cloud VM: git clone torkucloud/vanitas-docker && ./scripts/deploy-cloud.sh"
    echo ""
    echo "IMPORTANT: Transfer .env and secrets/ MANUALLY (they contain API keys)"
else
    echo "ERROR: Package creation failed"
    exit 1
fi

rm -f "$MANIFEST"