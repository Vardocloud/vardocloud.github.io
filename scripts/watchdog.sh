#!/bin/bash
# Vanitas Watchdog v2 — Cooldown'lu, spam yapmaz
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus

LOG="/home/ubuntu/.hermes/logs/watchdog.log"
STATE_DIR="/home/ubuntu/.hermes/data/watchdog"
RESTART_THRESHOLD=3
WINDOW_MINUTES=5
LOAD_LIMIT=4.0
LOAD_CRITICAL=8.0
WARP_CHILD_LIMIT=5

# Cooldown (saniye)
COOLDOWN_LOAD=1800       # 30dk
COOLDOWN_WARP=1800       # 30dk
COOLDOWN_CRASH=600       # 10dk
COOLDOWN_GW=600          # 10dk

mkdir -p "$STATE_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"
}

# Cooldown kontrol: 0=izin var, 1=bekle
cooldown_check() {
    local key="$1"
    local cooldown="$2"
    local stamp_file="$STATE_DIR/${key}.stamp"
    local now=$(date +%s)

    if [[ -f "$stamp_file" ]]; then
        local last=$(cat "$stamp_file")
        if (( now - last < cooldown )); then
            return 1  # bekle
        fi
    fi
    echo "$now" > "$stamp_file"
    return 0  # izin var
}

# 1. Crash-loop tespiti
while IFS= read -r unit; do
    [[ -z "$unit" ]] && continue

    state_file="$STATE_DIR/${unit}.state"
    restarts=$(journalctl --user -u "$unit" --since "${WINDOW_MINUTES}min ago" 2>/dev/null | grep -c "Started\|activating.*auto-restart")
    active=$(systemctl --user is-active "$unit" 2>/dev/null)

    if [[ "$active" == "failed" ]] || [[ "$active" == "activating" ]]; then
        if [[ "$restarts" -ge "$RESTART_THRESHOLD" ]]; then
            log "CRASH-LOOP: $unit ($restarts restarts in ${WINDOW_MINUTES}m) — DISABLED"
            systemctl --user stop "$unit" 2>/dev/null
            systemctl --user disable "$unit" 2>/dev/null
            if cooldown_check "crash_${unit}" "$COOLDOWN_CRASH"; then
                log "🛑 ALERT: $unit crash-loop — otomatik DISABLE edildi"
            fi
        fi
    fi
done < <(systemctl --user list-units --type=service --no-legend 2>/dev/null | awk '{print $1}')

# 2. Load average kontrolü
load=$(cat /proc/loadavg | awk '{print $1}')
if (( $(echo "$load > $LOAD_LIMIT" | bc -l 2>/dev/null) )); then
    top_proc=$(ps aux --sort=-%cpu | head -4 | tail -1 | awk '{print $11, $3"%"}')
    log "YUKSEK LOAD: ${load} — Top: ${top_proc}"

    if (( $(echo "$load > $LOAD_CRITICAL" | bc -l 2>/dev/null) )); then
        if cooldown_check "load_critical" "$COOLDOWN_LOAD"; then
            top3=$(ps aux --sort=-%cpu | head -4 | tail -3 | awk '{print $11, $3"%"}' | tr '\n' ' ')
            log "🔴 KRİTİK LOAD: ${load} — Top3: ${top3}"
        fi
    fi
fi

# 3. WARP child process kontrolü
warp_children=$(ps -eo pid,ppid,cmd | grep -c "[w]arp_proxy.py")
if [[ "$warp_children" -gt "$WARP_CHILD_LIMIT" ]]; then
    log "WARP CHILD PATLAMASI: ${warp_children} process — restart yapılıyor..."
    sudo systemctl restart warp-proxy 2>/dev/null
    sleep 2
    new_count=$(ps -eo pid,ppid,cmd | grep -c "[w]arp_proxy.py")
    if cooldown_check "warp_children" "$COOLDOWN_WARP"; then
        log "🟡 WARP restart yapıldı: ${warp_children} → ${new_count} process"
    fi
fi

# 4. Gateway health check
GATEWAY_STATUS=$(systemctl --user is-active hermes-gateway 2>/dev/null)
if [[ "$GATEWAY_STATUS" == "failed" ]]; then
    log "GATEWAY FAILED — resetting and restarting"
    systemctl --user reset-failed hermes-gateway 2>/dev/null
    systemctl --user start hermes-gateway 2>/dev/null
    sleep 5
    NEW_STATUS=$(systemctl --user is-active hermes-gateway 2>/dev/null)
    if [[ "$NEW_STATUS" != "active" ]]; then
        if cooldown_check "gw_failed" "$COOLDOWN_GW"; then
            log "⚠️ Gateway restart başarısız! Status: ${NEW_STATUS}"
        fi
    else
        log "Gateway restart başarılı"
    fi
fi

exit 0
