# HP EliteBook 2730p Salvage Reference

## Final Diagnostic Resolution (19 Jul 2026)

After 3+ hours of systematic diagnostic work:

| Test | Result | Conclusion |
|------|--------|-----------|
| Adapter (disconnected) | 19.56V | ✅ Adapter healthy |
| DCIN1 center pin voltage (connected) | 19.48V | ✅ Power reaches board |
| DCIN1 → GND continuity | No beep (re-measured) | ✅ No short circuit |
| DCIN1 → GND resistance (200Ω) | "1" (open) | ✅ Confirmed no short |
| Initial reading was 3Ω | Probe contact artifact | ⚠️ False alarm |

**True failure**: Power reaches DCIN1 but 3.3V/5V rails never come up. U91 (charging IC, likely BQ24702) or downstream MOSFETs failed. This requires soldering equipment and component-level repair — beyond what can be done without proper tools.

**Decision**: Pivot to salvage mode. Keep reusable parts, discard motherboard.

## Parts Salvaged

| Part | Spec | Reuse Plan |
|------|------|-----------|
| RAM x2 | DDR2 PC2-6400 2GB 200-pin SODIMM | Eee PC 1000HA / Acer Aspire 5570Z compatible |
| Adapter | 19V 4.74A 90W HP | Acer Aspire 5570Z (same 19V input) |
| HDD | Toshiba MK1214GSG 120GB 1.8" Micro SATA | USB enclosure → external drive |
| Fan | SUNON 5V 1.6W MagLev | USB desk fan (5V = direct USB solder) |
| Touchpad | Synaptics 920-001045-01 RevA | PS/2 protocol, Arduino-compatible |
| CMOS battery | Standard | Spare |
| Webcam | In display bezel | USB conversion (DIY Perks method) |
| Speakers | In chassis | Audio projects |
| LCD panel | SU-12W18A-04X 12.1" WXGA | LVDS controller board → external monitor |
| WiFi antennas | U.FL connectors | Salvage for RF projects |

## Parts NOT Salvaged

- WiFi card (Intel 512AN — old 802.11n, Mini PCIe)
- Bluetooth module (custom connector, low value)
- Keyboard (proprietary flex, unusable)
- Heatsink (CPU-specific)
- Ses kontrol paneli (touch key bar — proprietary)
- ExpressCard slot
- Motherboard (dead)

## LCD Panel Details

- Model: SU-12W18A-04X (also seen as SU-12W18A-03X)
- Size: 12.1" WXGA (1280x800)
- Interface: LVDS
- Touch: Wacom EMR digitizer + capacitive touch
- **LVDS controller board compatibility**: Search AliExpress for "SU-12W18A LVDS controller"
- **Touch support**: Capacitive touch may work with USB touch controller. Wacom EMR pen WILL NOT work without proprietary Wacom controller.
- **Reuse as wall display**: Viable. LVDS board + Raspberry Pi + 3D-printed frame → Home Assistant dashboard / family calendar.

## DC Jack Type

HP 2730p uses a **wired pigtail DC jack** (not soldered to motherboard). Part is shared with HP 2530p, 6930p, 8530p series. eBay item 330978421401 shows the replacement part — it's a cable with a 2-pin connector, not a solder-in jack.

## Key Diagnostic Lesson

When diagnosing "no power" on this model:
1. Don't assume the DC jack solder joints are the problem — it's a wired connector
2. The EMI shield must be completely removed to access the power circuit
3. A 3Ω reading can be a probe artifact — ALWAYS re-measure before concluding short circuit
4. If continuity beep disappears on re-measure, there's no short — look elsewhere (U91, power sequencing)
