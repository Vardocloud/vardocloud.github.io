# HP EliteBook 2730p Power Circuit Reference

## Model Info
- Model: HP EliteBook 2730p (2008, tablet-convertible)
- Processor: Intel Core 2 Duo SL9400/SL9600 (ultra-low-voltage)
- RAM: DDR2 PC2-6400, 2 slots
- Adapter: 18.5V, 65W (HP spare 463958-001)

## Power Circuit Layout

### Key Components (top side, under EMI shield)
- **DCIN1**: DC power input connector (center pin = +19V, outer = GND)
- **U91**: Charging/power management IC — likely BQ24702 or BQ24703 series
- **C491, C486, C484, C485**: Input filter capacitors on 19V rail
- **R316, R317, R318, R319**: Current sense / pull-up resistors for U91
- **Q50**: MOSFET near DCIN1 area (likely one of the power gate FETs)
- **U90**: Secondary IC near the power section

### Physical Location
- DCIN1 is on the top-left area of the motherboard (when viewed from top with keyboard removed)
- Located near the RAM slots and the CPU cooling fan
- The entire power section sits under the copper EMI shield that must be removed for access

### Disassembly Notes
- Must remove keyboard (2 Mylar screw covers + 6 Torx T8 screws)
- Then remove palmrest to access motherboard top side
- EMI shield secured with M2x4 Phillips screws
- Total: 49 screws of 9 different sizes in the entire laptop

## Common Failure: Short on 19V Rail

### Symptoms
- Power LED blinks once then immediately turns off
- No fan spin, no POST, no display
- CMOS reset has no effect
- Battery removed, adapter-only: same behavior

### Diagnostic Path (confirmed on a real unit, 19 Jul 2026)

1. **Continuity test**: DCIN1 center pin → GND = initial BEEP (seemed like short)
2. **Resistance test** (200Ω mode): DCIN1 → GND = ~3Ω initially → **RE-MEASURED = "1" (open)** — first reading was probe contact artifact
3. **Adapter test (disconnected)**: 19.56V — adapter healthy ✅
4. **DCIN1 voltage (connected)**: 19.48V — power reaches board ✅
5. **No short circuit confirmed**: Re-measurement showed open circuit

### FINAL DIAGNOSIS
Power reaches DCIN1 at correct voltage, no short circuit on 19V rail. The power management IC (U91, likely BQ24702 series) or downstream MOSFETs fail to generate 3.3V/5V standby rails. This is a component-level repair requiring soldering equipment.

### CRITICAL LESSON
**A 3Ω continuity reading can be a probe contact artifact.** If re-measuring at a cleaner contact point shows "1" (open), there is NO short circuit. Always re-measure before concluding.

### Finding the Shorted Component
- All components on the 19V rail will show short to ground via continuity
- To find WHICH one is shorted:
  - Method A: Plug adapter 10-15 seconds, touch each MOSFET/capacitor — hot one is shorted
  - Method B: Isopropyl alcohol evaporation test
  - Method C: Desolder components one by one until short clears (last resort)

## DT-830D Multimeter Quick Reference
- **Continuity mode**: Dial to diode/sound-wave symbol (4-5 o'clock). Black→COM, Red→VΩmA. Probes together = beep.
- **DC Voltage 20V**: Dial to DCV 20 (10 o'clock). For adapter and power rail measurement.
- **Resistance 200Ω**: Dial to 200 in Ω section (8 o'clock). Use for precise short measurement.
- ⚠️ Never use 10ADC jack for voltage measurement — only VΩmA.

## Schematics Availability
- HP does not publish schematics publicly
- Badcaps.net has a tested BIOS dump available (requires premium membership)
- Similar HP EliteBook models (2530p, 6930p) may share power circuit design
- eBay listing (item 330978421401) shows DC jack is a wired/pigtail type, not soldered directly to board

## YouTube Resources
- Disassembly video: https://www.youtube.com/watch?v=ToomYCe2_0g (27min, silent, 53k views)
- Battery reset trick: https://www.youtube.com/watch?v=tOkRYQxViJk (SW1 button on battery pack)
- General HP dead motherboard repair: https://www.youtube.com/watch?v=IO_mO5oex1o (MOSFET replacement method)

## DC Jack Type
**This model uses a wired pigtail DC jack, NOT soldered to the board.** The DC jack is a separate cable with a 2-pin connector that plugs into the motherboard at DCIN1. Checking the "solder joints" is irrelevant — check whether the connector is fully seated. This was confirmed by the eBay replacement part listing (item 330978421401).

## Key MOSFETs Near DCIN1
- **PQ2**: First MOSFET after DCIN4 (power gating/ORing). 3-pin SOT-23 package. Located directly below the DCIN4 label.
- **PQ3**: Second MOSFET, same row as PQ2. Located near second mounting hole.
- **U91**: Power management IC (BQ24702 series). Located near DCIN1 in the power section.
- Both MOSFETs tested OK (536Ω to ground on all pins = normal).

## Service Manual
- HP Part Number: 483222-002 (March 2012)
- PDF: https://h10032.www1.hp.com/ctg/Manual/c01976070.pdf
- Key pages: Power connector cable removal (p.46-48), system board (p.63+)
