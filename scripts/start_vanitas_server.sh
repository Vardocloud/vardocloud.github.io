#!/bin/bash
# Vanitas Server Keeper — idempotent, safe to run every minute
# Handles EADDRINUSE and orphan processes robustly

cd /home/ubuntu/vanitas-web
LOGFILE=/home/ubuntu/vanitas-server-output.log

# Check /proc/net/tcp directly using grep -q (exit code based, no multi-line issues)
check_port_3005() { cat /proc/net/tcp 2>/dev/null | grep -q ":0BBD.*0A" && echo 1 || echo 0; }
check_port_8765() { cat /proc/net/tcp 2>/dev/null | grep -q ":223D.*0A" && echo 1 || echo 0; }

listening_on_3005=$(check_port_3005)
listening_on_8765=$(check_port_8765)

if [ "$listening_on_3005" = "1" ]; then
  # Server is up — check if Node.js process is alive
  node_pid=$(ps aux | grep "node server.mjs" | grep -v grep | awk '{print $2}')
  if [ -n "$node_pid" ]; then
    # All good, nothing to do
    exit 0
  fi
  # Port taken but no Node process — stale socket, force kill
  echo "[$(date)] Stale socket on 3005, force killing..." >> "$LOGFILE"
  fuser -k 3005/tcp 2>/dev/null || true
  sleep 2
fi

# Clean up any orphan Python processes
python_pids=$(ps aux | grep "python3.*soniox-server/main.py" | grep -v grep | awk '{print $2}')
if [ -n "$python_pids" ]; then
  echo "[$(date)] Killing orphan Python: $python_pids" >> "$LOGFILE"
  kill $python_pids 2>/dev/null
  sleep 1
fi

echo "[$(date)] Starting Vanitas server..." >> "$LOGFILE"

# Start Node.js
node server.mjs >> "$LOGFILE" 2>&1 &
NODE_PID=$!
echo "[$(date)] Node.js PID: $NODE_PID" >> "$LOGFILE"

# Wait for ports (up to 45s for VAD warmup)
for i in $(seq 1 45); do
  port_3005=$(check_port_3005)
  port_8765=$(check_port_8765)

  if [ "$port_3005" = "1" ] && [ "$port_8765" = "1" ]; then
    echo "[$(date)] ✅ Both ports ready (${i}s) PID=$NODE_PID" >> "$LOGFILE"
    exit 0
  fi

  if ! kill -0 $NODE_PID 2>/dev/null; then
    echo "[$(date)] ❌ Node.js died (${i}s)" >> "$LOGFILE"
    exit 1
  fi

  sleep 1
done

echo "[$(date)] ⚠️ Timed out waiting for ports" >> "$LOGFILE"
exit 1