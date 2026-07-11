#!/bin/bash
# Vanitas Infrastructure Control Script
# Gateway + Proxy restart, status, start, stop — no approval needed
# Usage: infra.sh [restart|start|stop|status|reset|health|proxy-restart|proxy-status|full-restart|full-status|dashboard-restart]

export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus

case "${1:-status}" in
    restart)
        systemctl --user restart hermes-gateway
        sleep 3
        NEW_STATUS=$(systemctl --user is-active hermes-gateway)
        echo "Gateway restarted. Status: ${NEW_STATUS}"
        ;;
    start)
        systemctl --user start hermes-gateway
        sleep 3
        NEW_STATUS=$(systemctl --user is-active hermes-gateway)
        echo "Gateway started. Status: ${NEW_STATUS}"
        ;;
    stop)
        systemctl --user stop hermes-gateway
        echo "Gateway stopped."
        ;;
    reset)
        systemctl --user reset-failed hermes-gateway
        systemctl --user start hermes-gateway
        sleep 3
        NEW_STATUS=$(systemctl --user is-active hermes-gateway)
        echo "Gateway reset+started. Status: ${NEW_STATUS}"
        ;;
    health)
        HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8642/health --connect-timeout 5 --max-time 10 2>/dev/null)
        echo "Gateway health: HTTP ${HTTP_CODE}"
        # Proxy health check
        PRX_CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 --max-time 10 http://127.0.0.1:19999/v1/models 2>/dev/null)
        echo "Proxy health:    HTTP ${PRX_CODE}"
        ;;
    status)
        systemctl --user status hermes-gateway --no-pager
        ;;
    # --- Proxy management ---
    proxy-restart)
        systemctl --user restart hermes-pollinations-proxy
        sleep 2
        PRX_STATUS=$(systemctl --user is-active hermes-pollinations-proxy)
        PRX_CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 --max-time 10 http://127.0.0.1:19999/v1/models 2>/dev/null)
        echo "Proxy restarted. Status: ${PRX_STATUS} | HTTP: ${PRX_CODE}"
        ;;
    proxy-status)
        systemctl --user status hermes-pollinations-proxy --no-pager
        ;;
    proxy-start)
        systemctl --user start hermes-pollinations-proxy
        sleep 2
        PRX_STATUS=$(systemctl --user is-active hermes-pollinations-proxy)
        echo "Proxy started. Status: ${PRX_STATUS}"
        ;;
    proxy-stop)
        systemctl --user stop hermes-pollinations-proxy
        echo "Proxy stopped."
        ;;
    # --- Combined operations ---
    full-restart)
        systemctl --user restart hermes-pollinations-proxy
        sleep 1
        systemctl --user restart hermes-gateway
        sleep 3
        GW_STATUS=$(systemctl --user is-active hermes-gateway)
        PRX_STATUS=$(systemctl --user is-active hermes-pollinations-proxy)
        echo "Full restart done. Gateway: ${GW_STATUS} | Proxy: ${PRX_STATUS}"
        ;;
    full-status)
        echo "=== Gateway ==="
        systemctl --user status hermes-gateway --no-pager 2>&1 | head -5
        echo ""
        echo "=== Proxy (port 19999) ==="
        systemctl --user status hermes-pollinations-proxy --no-pager 2>&1 | head -5
        echo ""
        echo "=== Health Check ==="
        GW_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8642/health --connect-timeout 5 --max-time 10 2>/dev/null)
        PRX_CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 --max-time 10 http://127.0.0.1:19999/v1/models 2>/dev/null)
        echo "Gateway: HTTP ${GW_CODE} | Proxy: HTTP ${PRX_CODE}"
        ;;
    dashboard-restart)
        systemctl --user restart hermes-dashboard
        sleep 2
        NEW_STATUS=$(systemctl --user is-active hermes-dashboard)
        echo "Dashboard restarted. Status: ${NEW_STATUS}"
        ;;
    *)
        echo "Usage: $0 {restart|start|stop|reset|health|status|proxy-restart|proxy-status|proxy-start|proxy-stop|full-restart|full-status|dashboard-restart}"
        exit 1
        ;;
esac
