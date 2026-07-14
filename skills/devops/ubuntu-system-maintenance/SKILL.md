---
name: ubuntu-system-maintenance
title: Ubuntu System Maintenance
description: "Ubuntu system update control, security verification, and package management — check pending updates, apply upgrades, verify unattended-upgrades, check release upgrades, and perform post-upgrade validation."
trigger: "User asks to check/apply Ubuntu updates. User asks about system security status. User asks about release upgrades. Routine server maintenance."
---

# Ubuntu System Maintenance

## Overview

Routine maintenance for Ubuntu 24.04 LTS (Oracle Cloud ARM64). Covers checking for pending updates, applying them safely, verifying unattended-upgrades (security auto-updates), checking for release upgrades, and validating post-upgrade health.

## Checking Pending Updates

```bash
# List all pending
apt list --upgradable 2>/dev/null

# Count
apt list --upgradable 2>/dev/null | grep -c "\[upgradable"

# Security-only count
apt list --upgradable 2>/dev/null | grep "security" | wc -l
```

## Release Upgrade Check

Ubuntu LTS → LTS upgrades are gated by `/etc/update-manager/release-upgrades`:

| Prompt= | Behavior |
|---------|----------|
| `lts` (default) | Only check for LTS→LTS upgrades (e.g. 24.04 → 26.04) |
| `never` | Never check |
| `normal` | Check for any release upgrade (LTS and non-LTS) |

```bash
# Current setting
grep "Prompt" /etc/update-manager/release-upgrades

# Check for available release
do-release-upgrade -c 2>&1
# → "no development version of an LTS available" = no update
```

## Security Auto-Updates (unattended-upgrades)

### What It Does
- Checks for security updates daily at ~06:21
- Applies only `*-security` and `*-infra-security` origin packages
- Does NOT automatically reboot (Automatic-Reboot: false)
- Logs everything to syslog and `/var/log/unattended-upgrades/`

### Verification

```bash
# Is it installed?
dpkg -l unattended-upgrades 2>/dev/null

# Package list refresh & auto-upgrade flags
cat /etc/apt/apt.conf.d/20auto-upgrades
# Update-Package-Lists "1" = daily
# Unattended-Upgrade "1" = daily

# Which origins are allowed
cat /etc/apt/apt.conf.d/50unattended-upgrades | head -30

# Timer status (systemd)
systemctl status apt-daily.timer
systemctl status apt-daily-upgrade.timer

# Recent activity
tail -20 /var/log/unattended-upgrades/unattended-upgrades.log
# "All upgrades installed" = success
# "Lock could not be acquired" = another apt was running

# History
grep -E "Start-Date|End-Date" /var/log/apt/history.log | tail -10
```

## Applying System Upgrades

### Safe Upgrade Sequence

```bash
# 1. Refresh package lists
sudo apt update

# 2. Verify pending list
apt list --upgradable

# 3. Apply ALL upgrades (security + regular)
sudo apt upgrade -y

# 4. Remove orphaned packages
sudo apt autoremove -y

# 5. Snap updates (if installed)
sudo snap refresh 2>/dev/null

# 6. Check reboot requirement
ls /var/run/reboot-required 2>/dev/null
# Empty file → minor touch, no actual reboot needed
# Has content → kernel/libc updated, reboot recommended
cat /var/run/reboot-required.pkgs 2>/dev/null || echo "no package list"
```

### Post-Upgrade Validation Checklist

- [ ] `apt list --upgradable` returns empty (everything current)
- [ ] Disk usage dropped (typical: 89% → 81%, ~4GB freed)
- [ ] `reboot-required` checked and understood
- [ ] Docker daemon restarts cleanly after containerd/Compose upgrade: `sudo systemctl restart docker && sleep 3 && docker ps`
- [ ] All expected containers running: `docker ps --format "table {{.Names}}\t{{.Status}}"`
- [ ] Hermes gateway responsive (`systemctl --user status hermes-gateway`)
- [ ] WARP proxy running
- [ ] Open WebUI accessible (port 3000 / Tailscale) — if container was removed, confirm `docker ps -a` shows nothing stale

## Special Cases

### containerd + docker-compose-v2 Updates
These may restart the Docker daemon. Containers with `restart=always` or `on-failure` recover automatically within seconds. Brief disruption is normal.

### libfwupd2 (firmware updater) Removal
`apt autoremove` often finds `libfwupd2` is no longer required on Oracle Cloud (no firmware updates). Safe to remove — it reclaims ~2MB.

### Disk Space Recovery
A full `apt upgrade` + `autoremove` typically recovers 3-5GB on a 45GB root disk. If disk is critically low (<5% free), run autoremove BEFORE upgrade to avoid install failures.

## Pitfalls

- **Don't skip `apt update` before `apt upgrade`:** Running `apt list --upgradable` without a fresh `apt update` shows stale cache. Always refresh first.
- **`reboot-required` can be stale:** An empty `/var/run/reboot-required` file means a package touched it but no actual package list was written — no reboot needed. Check `reboot-required.pkgs` for real requirements.
- **`do-release-upgrade -c` needs TTY:** Some versions require `-f DistUpgradeViewNonInteractive` for non-TTY contexts. If it hangs, use the non-interactive flag.
- **pip/npm/uv araçlarının güncellemeleri apt kapsamında DEĞİL:** Bu skill apt paketlerini yönetir. Pip/npm/uv araçlarının sürüm takibi için ayrıca `references/pip-npm-uv-version-monitoring.md` dosyasına bak. Otomatik takip henüz yok.
