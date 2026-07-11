#!/bin/bash
# scripts/deploy-cloud.sh
# Cloud VM'de Vanitas'ı tek komutla başlatır.
# Usage: ./scripts/deploy-cloud.sh
#
# Prerequisites:
#   - git clone torkucloud/vanitas-docker && cd vanitas-docker
#   - scp vanitas-data-portable.tar.gz into this directory
#   - cp .env.template .env && nano .env (fill in API keys)

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE_FILE="docker-compose.yml"
CLOUD_FILE="docker-compose.cloud.yml"
DATA_TAR="vanitas-data-portable.tar.gz"

echo "=== Vanitas Cloud Deployment ==="
echo ""

# Step 1: Check .env
if [ ! -f ".env" ]; then
    echo "ERROR: .env not found!"
    echo "  cp .env.template .env"
    echo "  nano .env  # Fill in API keys, BWS token, Telegram token"
    exit 1
fi

if grep -q "XXXXXXXX" .env; then
    echo "WARNING: .env contains placeholder values (XXX...)"
    echo "  Edit .env and replace all XXXXXXXX with real values."
    echo "  Continue anyway? (y/N)"
    read -r response
    [ "$response" != "y" ] && exit 1
fi

echo "[1/5] .env OK"

# Step 2: Unpack portable data if available
if [ -f "$DATA_TAR" ]; then
    echo "[2/5] Unpacking $DATA_TAR..."
    mkdir -p data/hermes
    tar xzf "$DATA_TAR" -C data/hermes/
    echo "      Data unpacked to data/hermes/"
else
    echo "[2/5] No $DATA_TAR found — starting with fresh config only"
    echo "      (state.db, profiles, cron history will be empty)"
    mkdir -p data/hermes
fi

# Step 3: Ensure SSH keys directory exists
mkdir -p data/ssh data/ssh-keys
if [ ! -f "data/ssh/authorized_keys" ]; then
    echo "[3/5] WARNING: No SSH authorized_keys found."
    echo "      SSH access will not work until you add your public key."
    echo "      echo 'ssh-ed25519 AAA...' > data/ssh/authorized_keys"
else
    echo "[3/5] SSH keys OK"
fi

# Step 4: Build and start
echo "[4/5] Building Docker image (~10 min first time)..."
COMPOSE="docker compose"
if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    echo "ERROR: docker compose not installed"
    exit 1
fi

if [ -f "$CLOUD_FILE" ]; then
    $COMPOSE -f "$COMPOSE_FILE" -f "$CLOUD_FILE" build
    echo "      Starting containers..."
    $COMPOSE -f "$COMPOSE_FILE" -f "$CLOUD_FILE" up -d
else
    $COMPOSE -f "$COMPOSE_FILE" build
    echo "      Starting containers..."
    $COMPOSE -f "$COMPOSE_FILE" up -d
fi

# Step 5: Health check
echo "[5/5] Waiting for gateway to start (45s)..."
sleep 45

HEALTH=$(curl -s http://127.0.0.1:8642/health 2>/dev/null || echo "FAIL")
if echo "$HEALTH" | grep -q "ok"; then
    echo ""
    echo "=== SUCCESS ==="
    echo "Gateway: http://127.0.0.1:8642 (healthy)"
    echo ""
    echo "--- Tailscale Setup ---"
    echo "Run: docker exec vanatis-tailscale tailscale up"
    echo "Authenticate at the URL provided."
    echo ""
    echo "--- Telegram Test ---"
    echo "Send a message to your Telegram bot to verify it's polling."
    echo ""
    echo "--- Access ---"
    echo "  Gateway: curl http://127.0.0.1:8642/health"
    echo "  SSH:     ssh -i data/ssh/vanitas_host_key -p 2222 ubuntu@localhost"
    echo "  Shell:   ./vanitas.sh shell"
    echo "  Logs:    ./vanitas.sh logs"
    echo ""
    echo "DONE! Vanitas is running on cloud."
else
    echo ""
    echo "=== WARNING: Gateway not healthy yet ==="
    echo "Health response: $HEALTH"
    echo ""
    echo "Check logs: ./vanitas.sh logs"
    echo "Wait 60 more seconds and try: curl http://127.0.0.1:8642/health"
fi