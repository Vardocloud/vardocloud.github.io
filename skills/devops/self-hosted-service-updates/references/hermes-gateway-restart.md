# Hermes Gateway Restart After Venv Package Updates

## Problem

After updating pip packages in the hermes-agent venv, `systemctl --user restart hermes-gateway` consistently times out (30s+). The gateway stops cleanly but systemd can't confirm the new process started within the timeout window.

## Root Cause

The gateway's drain timeout (60s default) plus Telegram background task unwind can push the stop phase past systemd's default `TimeoutStopSec`. When systemd sends SIGKILL after timeout, it marks the service as `failed`, and subsequent `start` commands also time out because the failed state blocks normal start.

## Workaround

Always use the two-step reset-then-start pattern:

```bash
systemctl --user reset-failed hermes-gateway
systemctl --user start hermes-gateway
sleep 3
systemctl --user is-active hermes-gateway
```

**Never use `systemctl restart`** after venv package updates — it will timeout.

## When This Applies

- After `pip install --upgrade` in the hermes-agent venv
- After any venv modification that might affect running gateway imports
- Anytime `systemctl restart` produces a 30s timeout

## Verification

```bash
# Gateway should show "active"
systemctl --user is-active hermes-gateway

# Check recent logs for clean startup (no import errors)
journalctl --user -u hermes-gateway --no-pager -n 10
```
