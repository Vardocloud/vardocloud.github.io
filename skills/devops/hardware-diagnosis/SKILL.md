---
name: hardware-diagnosis
description: "Guide non-technical users through hardware repair — multimeter usage, short circuit detection, photo-based component identification, and step-by-step diagnostic methodology."
version: 1.0.0
metadata:
  hermes:
    tags: [hardware, repair, multimeter, diagnosis, electronics]
    category: devops
---

# Hardware Diagnosis Skill

Guide non-technical users through hardware repair using photos, multimeter readings, and step-by-step instructions. Designed for laptop/desktop motherboard repair scenarios.

## Core Principles

### 🔴 PITFALL: Too Many Steps At Once

When the user is physically working on hardware (holding a screwdriver, probe, or disassembled device), they CANNOT process multiple complex instructions. Give **ONE step at a time**, wait for verification, then give the next step. Never list 5+ diagnostic steps in one message.

**Wrong:** "Önce şunu yap, sonra şunu, eğer olmazsa şuna bak, sonra da multimetreyi şu moda alıp şunları ölç..."
**Right:** "Multimetreyi continuity moduna al. Hazır mısın?" → wait → "Şimdi kırmızı probu DCIN1 orta pinine değdir."

### 🟢 DO: Use Vision Analysis for Component Identification

When the user sends a photo of a PCB/motherboard:
1. Use `vision_analyze` with a detailed question asking for component labels (R/C/L/U/Q codes), connector names, and test point locations
2. Cross-reference with any available schematics or service manuals found via web search
3. Mark up the photo verbally by describing positions relative to visible landmarks

### 🟢 DO: Verify Understanding Before Proceeding

Before giving the next instruction, confirm the user understood the last result:
- "Bip sesi geldi mi?" 
- "Kaç volt görüyorsun?"
- "Hangi parça ısınıyor?"

## Diagnostic Methodology

### Phase 1: Symptom Classification

Common laptop no-power symptoms and their likely causes:

| Symptom | Most Likely Cause |
|---------|-------------------|
| Power LED blinks once then off, no fan | Short circuit on power rail (MOSFET/capacitor) |
| Power LED stays on, no display | RAM, BIOS, or GPU issue |
| No lights at all | DC jack, adapter, or blown fuse |
| Fan spins briefly then stops | Short circuit or overcurrent protection |
| Continuous blinking LED | Error code — count blinks |

### Phase 2: Multimeter Setup (DT-830D and similar)

**Probe Connection:**
- Black probe → COM (bottom jack)
- Red probe → VΩmA (middle jack)

**Key Modes:**
- **Continuity (buzzer):** Dial to diode/sound-wave symbol (usually 4-5 o'clock position). Probes touching = beep. Use for short circuit detection.
- **DC Voltage 20V:** Dial to DCV 20. Use for adapter output and power rail measurement.
- **Resistance 200Ω:** Dial to 200 in Ω section. Use for precise short circuit measurement (0-3Ω = dead short).

### Phase 3: Short Circuit Detection

1. **Continuity test first:** Red probe on power rail (DCIN center pin), black probe on ground (any screw hole). Beep = short circuit.
2. **Resistance test:** Switch to 200Ω mode, measure same points. < 10Ω = confirmed short.
3. **Adapter test:** Measure adapter output directly. If voltage is significantly below rated (e.g. 14V instead of 18.5V), adapter may be failing or crowbar-protecting against the short.

### Phase 4: Finding the Shorted Component

**Method A — Finger Test (no tools needed):**
1. Plug in adapter for 10-15 seconds MAX (short heats up fast)
2. Touch MOSFETs, capacitors, and power IC with finger
3. The HOT one is the shorted component
4. ⚠️ Do NOT leave adapter plugged in > 15 seconds — component can burn

**Method B — Alcohol Evaporation (preferred):**
1. Apply a few drops of isopropyl alcohol (or high-proof kolonya) to the power circuit area
2. Plug in adapter
3. Watch which drop evaporates first — that component is overheating

**Method C — Voltage Injection (advanced, for electronics technicians):**
1. Use a bench power supply set to 1V, 1-2A current limit
2. Inject voltage into the shorted rail
3. Use thermal camera or alcohol method to find hot component

### Phase 5: Common Failure Points on Laptop Motherboards

1. **MOSFETs** — Power gate transistors (3-pin SMD packages near DCIN). Most common failure.
2. **Ceramic capacitors** — Can short internally. Look near power connectors and VRM area.
3. **Charging IC** — BQ24700 series (HP), ISL series, etc. Controls power sequencing.
4. **DC jack solder joints** — Cracked or cold solder joints on the connector pins.

## Web Research for Old Hardware

When searching for repair information on old/obscure models:
- YouTube: search for model number + "disassembly", "no power", "repair", "dead motherboard"
- Badcaps.net forums: search for model + "BIOS dump", "schematic", "boardview"
- eBay/AliExpress: search for model + "DC jack" to see what the replacement part looks like (shows if it's wired or soldered)
- HP service manuals: `h10032.www1.hp.com/ctg/Manual/c0XXXXXXX.pdf` pattern

## Verification After Repair

After replacing a component:
1. Check continuity again — short should be gone
2. Measure resistance — should be in kΩ or MΩ range
3. Power on with adapter only (no battery) for first test
4. Monitor for unusual heat for first 5 minutes

## Phase 6: Part Salvage and Reuse (Dead Motherboard)

When the motherboard repair is beyond practical repair (no schematics, component-level soldering needed, user lacks tools), pivot to salvage mode. Evaluate each removable part for reuse value.

### Evaluation Criteria
- **Standard interface?** (USB, SATA, 5V, PS/2) → easier reuse. Proprietary pinouts → harder.
- **Common form factor?** (SODIMM, 2.5" SATA) → reusable elsewhere. Custom (1.8" Micro SATA) → limited.
- **Voltage compatibility?** 5V parts work with USB. 12V/19V parts need separate power.
- **Independent operation?** A webcam on USB is standalone. A keyboard with a 40-pin flex connector is not.

### Typical Laptop Part Salvage Value

| Part | Score | Reuse |
|------|:-----:|-------|
| RAM (SODIMM) | ⭐⭐⭐ | Check DDR version compatibility with other machines |
| Adapter | ⭐⭐⭐ | Universal if voltage matches (19V is standard for most laptops) |
| HDD/SSD | ⭐⭐⭐ | USB enclosure → external drive. Check form factor (2.5" vs 1.8") |
| Cooling fan | ⭐⭐⭐ | If 5V: wire to USB for desk fan. If 12V: needs separate PSU |
| Webcam module | ⭐⭐⭐ | Usually USB-connected. Solder to USB cable → external webcam |
| Fingerprint reader | ⭐⭐⭐ | Often USB internally. Can be modded for Windows Hello |
| Touchpad (Synaptics) | ⭐⭐ | Usually PS/2 protocol. Arduino-compatible with pin mapping |
| Speakers | ⭐⭐ | Small, reusable in audio projects |
| CMOS battery | ⭐⭐ | Standard CR2032, keep as spare |
| LCD panel | ⭐⭐ | LVDS controller board (~$30) → external monitor. Touch/pen usually won't work |
| WiFi card | ⭐ | Old standard, Mini PCIe — limited modern use |
| Bluetooth module | ❌ | Custom connector, not worth effort |
| Keyboard | ❌ | Proprietary flex connector, unusable standalone |
| Heatsink/heatpipe | ❌ | CPU-specific, cannot repurpose |
| Hinges | ⭐ | Sturdy metal — robot/mechanical projects |

### Salvage Workflow
1. **Photograph everything** before and during disassembly
2. **Remove cables carefully** — ZIF connectors: lift latch before pulling. Friction-fit: pull straight.
3. **Adhesive-mounted parts** (touchpad, fingerprint reader): apply heat (hair dryer, 30-40s), lift with plastic spudger, not metal
4. **Sort parts** as you remove them: keep / maybe / discard piles
5. **Label or bag** small parts immediately so they don't get lost

### When to Stop Repairing and Start Salvaging
- After 3+ hours of diagnostic work without clear root cause
- When component-level repair requires soldering and user lacks equipment
- When replacement motherboard costs more than the laptop is worth
- **User fatigue signal**: "Sıkıldım ya", "PC'yi toplucaz olmuyor" → pivot immediately. Don't push.

## 🔴 PITFALL: False Short Circuit Readings

A low-resistance reading (~1-5Ω) between power rail and ground can be a **false positive** caused by:
- Poor probe contact on oxidized pads
- Measuring through a low-resistance path that isn't actually a short (e.g., CPU VCore rail ~2Ω normally)
- Probe tips touching adjacent pins

**Always re-measure** before concluding a short exists. Move probes to fresh contact points, clean pad with alcohol if needed. A reading that jumps between 1Ω and "1" (open) is probe contact, not a real short.

If the first reading shows 3Ω and a re-measure shows "1" (open) — **there is no short.** The first reading was probe artifacts.

## 🔴 PITFALL: Adapter Voltage Drop Misinterpretation

When an adapter reads below rated voltage (e.g., 14V instead of 19V), there are two possible causes:
1. **Adapter is failing** — internal capacitors degraded
2. **Adapter's crowbar protection** — it detects a short on the output and drops voltage to protect itself

Measure the adapter **disconnected from the laptop** first. If it reads normal (19V) when disconnected but drops when connected → there IS a short on the board. If it reads low even when disconnected → adapter is bad.
