#!/bin/bash
# Security Scan — combined daily + weekly
# Usage: security_scan.sh --daily   (6 checks, ~30s)
#        security_scan.sh --weekly  (11 checks, ~2min)
MODE="${1:---daily}"
SCORE=0

report_line() {
    local emoji="$1" status="$2" msg="$3"
    echo "$emoji $status: $msg"
}

fail() { SCORE=$((SCORE + 1)); report_line "$1" FAIL "$2"; }
pass() { report_line "$1" OK "$2"; }

# --- Port check ---
check_ports() {
    local known="sshd|hermes-gateway|opencode-go|pollinations|docker|kube|python3.*19997|caddy"
    local unknown
    unknown=$(ss -tlnp 2>/dev/null | grep LISTEN | grep -vE "$known" || true)
    if [ -n "$unknown" ]; then
        fail "🔌" "Unexpected listening services: $unknown"
    else
        pass "🔌" "No unexpected ports"
    fi
}

# --- Docker ---
check_docker() {
    if ! command -v docker &>/dev/null; then
        pass "🐳" "Docker not available (container mode)"
        return
    fi
    local down
    down=$(docker ps --format "{{.Names}} {{.Status}}" 2>/dev/null | grep -v "Up " || true)
    if [ -n "$down" ]; then
        fail "🐳" "Containers not running: $down"
    else
        pass "🐳" "All containers healthy"
    fi
}

# --- Disk ---
check_disk() {
    local warn=""
    for mount in / /home; do
        if [ -d "$mount" ]; then
            local pct
            pct=$(df "$mount" 2>/dev/null | awk 'NR==2 {print $5}' | tr -d '%')
            if [ "$pct" -gt 85 ]; then
                warn="$warn $mount=${pct}%"
            fi
        fi
    done
    if [ -n "$warn" ]; then
        fail "💾" "Disk critical:$warn"
    else
        pass "💾" "Disk usage OK"
    fi
}

# --- Memory ---
check_memory() {
    local swap
    swap=$(free -h | awk '/Swap/ {print $3}')
    if [ "$swap" != "0B" ] && [ -n "$swap" ]; then
        fail "🧠" "Swap in use: $swap"
    else
        pass "🧠" "Memory OK"
    fi
}

# --- Services (container-safe) ---
check_services() {
    local warn=""
    # Process-based check (works in container, no DBUS needed)
    for svc in "hermes gateway" "opencode-go"; do
        if ! pgrep -f "$svc" >/dev/null 2>&1; then
            # Skip opencode-go as it's started on-demand by hermes-gateway
            [ "$svc" = "opencode-go" ] && continue
            warn="$warn hermes-gateway"
        fi
    done
    # Check proxy via process (ss not available in container)
    if ! pgrep -f "literouter_proxy|pollinations_proxy" >/dev/null 2>&1; then
        warn="$warn pollinations-proxy"
    fi
    if [ -n "$warn" ]; then
        fail "⚙️" "Down services:$warn"
    else
        pass "⚙️" "All services running"
    fi
}

# --- Weekly-only checks ---
check_ufw()      { command -v ufw &>/dev/null && sudo ufw status verbose 2>/dev/null | head -5 || echo "UFW not available (container)"; }
check_fail2ban() { command -v fail2ban-client &>/dev/null && sudo fail2ban-client status 2>/dev/null | head -5 || echo "fail2ban not available"; }
check_ssh()      { [ -f /var/log/auth.log ] && grep "Failed password" /var/log/auth.log 2>/dev/null | tail -5 || echo "No auth.log"; }
check_processes(){ ps aux --sort=-%mem 2>/dev/null | head -10; }

# ============ MAIN ============
echo "🔐 Security Scan — $(date)"
echo "Duration: $MODE"
echo ""

check_docker
check_ports
check_disk
check_memory
check_services

if [ "$MODE" = "--weekly" ]; then
    echo ""
    echo "=== Weekly Extended Checks ==="
    check_ufw
    check_fail2ban
    check_ssh
    echo "=== Top Processes ==="
    check_processes
fi

echo ""
echo "Score: $SCORE / 5"
