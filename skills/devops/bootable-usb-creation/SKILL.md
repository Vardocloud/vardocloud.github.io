---
name: bootable-usb-creation
description: Create bootable USB drives for OS installation — Ventoy (multi-ISO, recommended) and single-ISO methods. Covers Windows GUI and Linux terminal workflows, SHA256 verification, and old-hardware distro selection.
---

# Bootable USB Creation

## Trigger

User wants to create a bootable USB to install an OS, put multiple ISOs on one stick, verify an ISO download, or choose a distro for old/low-RAM hardware.

## Decision: Ventoy vs Single-ISO

**Use Ventoy when:** you may need multiple ISOs (Xubuntu + Tails + Windows), want to update ISOs without reformatting, or want drag-and-drop on Windows.

**Use single-ISO (dd / Rufus) when:** one ISO, one-time use, or Ventoy has a known compatibility issue.

---

## Method A: Ventoy (Recommended)

### Windows (GUI)

1. Go to https://github.com/ventoy/Ventoy/releases
2. Download `ventoy-x.y.z-windows.zip` from Assets (~16 MB)
3. Extract to a folder, plug in USB
4. Right-click **Ventoy2Disk.exe** → Run as Administrator
5. Select USB device → Install (erases all data — confirm)
6. Copy ISO files onto the "Ventoy" USB — done

**Direct download pattern:**
`https://github.com/ventoy/Ventoy/releases/download/v{version}/ventoy-{version}-windows.zip`

### Linux

See `references/ventoy-linux-commands.md` for the full terminal workflow (requires sudo — destructive to target device).

---

## Method B: Single ISO

See `references/single-iso-commands.md` for dd (Linux) and Rufus (Windows) workflows. Ventoy is preferred for repeat use.

---

## SHA256 Verification

**Windows (Command Prompt):**
```cmd
certutil -hashfile distro.iso SHA256
```

**Linux:**
```bash
sha256sum distro.iso
```

Compare against the official checksum from the distro's SHA256SUMS file.
See `references/distro-checksums.md` for current release checksums.

---

## Remote Desktop: Tablet → PC

When the user wants to control their PC from an Android tablet with keyboard,
Parsec in Trackpad Mode is the best solution. Full details in `references/remote-desktop-tablet.md`.

---

## Old Hardware Distro Selection

For machines with 4 GB RAM or less:

| Distro | Idle RAM | Min RAM | Notes |
|--------|----------|---------|-------|
| Xubuntu (XFCE) | ~400 MB | 1 GB | Best balance: light + full Ubuntu repos |
| Lubuntu (LXQt) | ~300 MB | 512 MB | Lighter, sparser |
| Debian + XFCE | ~350 MB | 512 MB | More manual, lighter base |
| Bodhi Linux | ~250 MB | 512 MB | Ultra-light |
| Qubes OS | 4+ GB | 16 GB | Will NOT boot on old machines |

Rule of thumb: RAM below 2 GB → Bodhi or Debian+LXDE. RAM 2 GB+ → Xubuntu.

---

## Companion Node Post-Install

When the goal is to set up the machine as a remote-controlled AI companion node (Edel tablet → Vanitas SSH), run a post-install script after first boot. The script template at `templates/post-install-setup.sh` installs:

1. System updates + base tools (curl, git, vim, htop)
2. **SSH server** — Vanitas remote terminal access
3. **UFW firewall** — allow SSH only
4. **Tailscale** — secure VPN tunnel (no port forwarding needed)
5. **Parsec** — tablet-to-desktop remote control with Trackpad Mode
6. **Power config** — disable sleep on lid close, disable screen lock (server mode)
7. Language pack (if needed)

**Offline workflow:** Copy the script + an install guide (template at `templates/offline-install-guide.txt`) onto the Ventoy USB alongside the ISO. Boot → install → mount USB → run script. Use USB tethering from phone if no WiFi.

### Post-install connectivity checklist

| Step | Command |
|------|---------|
| Internet | Phone USB tethering (auto-detected) |
| SSH | `sudo systemctl enable ssh --now` |
| Firewall | `sudo ufw allow ssh && sudo ufw enable` |
| Tailscale | `tailscale up` → share the 100.x.x.x IP |
| Parsec | Launch from app menu, login, enable hosting |

See `scripts/xubuntu-hp-companion.sh` for the ready-to-run HP 2730p version.

## Pitfalls

- **UEFI Secure Boot warnings on pre-2012 machines:** Core 2 Duo era uses Legacy BIOS. Ventoy's key enrollment warnings don't apply.
- **USB not detected at boot:** Enter BIOS (F2/F10/F12/Del), change boot order, disable Secure Boot.
- **Ventoy Install erases all data:** No undo. Verify the correct device.
- **ISO copy alone is not bootable:** Ventoy must be installed to USB first.
- **64-bit on old CPUs:** Core 2 Duo and later support 64-bit. Pentium M / early Atom may need 32-bit ISOs.
- **Offline installs:** Uncheck "Download updates while installing" — it hangs without internet. Use phone USB tethering post-install.
- **"isteyeyim mi" hatası:** Soru sorarken 1. tekil istek kipi değil, 2. tekil geniş zaman soru kipi kullan: "ister misin?", "bakayım mı?" değil "bakmamı ister misin?".
