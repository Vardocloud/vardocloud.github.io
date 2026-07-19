# Acer Legacy Boot Details — Aspire 5570Z & Similar

## Hardware Profile (Aspire 5570Z era)

| Feature | Detail |
|---------|--------|
| Model | Acer Aspire 5570Z series (model ZR1) |
| CPU | Intel Core 2 Duo / Core i3 (2nd gen) |
| RAM | DDR2 200-pin SODIMM (max 4 GB — 2×2 GB) |
| Era | ~2007-2010, Windows Vista/7 |
| BIOS | Legacy BIOS only — **no UEFI, no Secure Boot** |
| Disk | SATA II (2.5") |
| USB Boot | Requires Legacy USB boot enabled in BIOS |

## BIOS Access

- **BIOS Setup:** Press **F2** immediately after power-on (repeatedly)
- **Boot Menu:** Press **F12** (may need enabling in BIOS first under "Boot → F12 Boot Menu" → Enabled)
- If F12 doesn't work: Enter BIOS via F2 → navigate to Boot tab → set USB drive as first priority

## RAM Upgrade

- Original RAM: often 1×1 GB DDR2-667 or 1×2 GB DDR2-800
- Max supported: 4 GB (2×2 GB DDR2-800 200-pin SODIMM)
- Adding 2 GB to a 2 GB machine → 4 GB, enough for Xubuntu/Lubuntu
- ⚠️ DDR2 SODIMM ≠ DDR3 SODIMM — physically incompatible

## Disk

- Original: 80-160 GB SATA HDD (2.5", 5400 RPM)
- SSD upgrade: Any 2.5" SATA SSD works — transforms performance
- No M.2 slot on this era

## Windows COA Sticker

- Located on the bottom panel (white/silver sticker with Microsoft hologram)
- Contains the Windows product key — **photograph before wiping disk**
- Useful for: re-activating Windows if dual-boot needed later, or legal transfer

## Xubuntu Install Notes

| Setting | Value |
|---------|-------|
| Partition table | **MBR** (not GPT — Legacy BIOS requires MBR) |
| File system | ext4 |
| Swap | 4 GB (or swap file if SSD) |
| UEFI partition | ❌ Not needed — Legacy BIOS |

## Common Boot Issues

1. **USB not detected:** Enter BIOS → Boot tab → ensure USB boot is enabled, move USB device to top
2. **F12 boot menu not working:** BIOS → Advanced → "F12 Boot Menu" → Enabled
3. **Black screen after selecting USB:** Try a different USB port (USB 2.0 ports work best; some old BIOS can't boot from USB 3.0)
4. **Ventoy not booting:** Try single-ISO (Rufus in DD mode or `dd` on Linux) instead
