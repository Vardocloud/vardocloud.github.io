# Vintage Laptop RAM Compatibility

Covers DDR2-era (2005-2010) laptop RAM diagnostics when preparing an old machine for Linux installation. The wrong RAM is the #1 cause of "no display after upgrade" on these machines.

## Reading a DDR2 SODIMM Label

Example labels from the 19 Temmuz 2026 session:

| Label Text | Means |
|---|---|
| `2GB 2Rx8 PC2-6400S-666-13-ZZ` | 2 GB, **double rank** (2Rx8), **800 MHz** (PC2-6400), CL6 (666), 13 column address |
| `512MB 2Rx16 PC2-5300S-555-12-A3` | 512 MB, **double rank** (2Rx16), **667 MHz** (PC2-5300), CL5 (555), 12 column address |
| `KVR667D2S5/2G` | Kingston, **667 MHz** (PC2-5300), **2 GB** |

### Decoder

| Field | Meaning |
|---|---|
| **PC2-5300** | DDR2-667 (effective 667 MHz, 5.3 GB/s) |
| **PC2-6400** | DDR2-800 (effective 800 MHz, 6.4 GB/s) |
| **2Rx8** | Double rank, 8-bit chip width |
| **2Rx16** | Double rank, 16-bit chip width |
| **CL5 / CL6** | CAS latency (5 = 555, 6 = 666) |
| **200-pin** | SODIMM form factor (laptop RAM) |

## Intel 945 Chipset Family Limits

The most common chipset on 2006-2009 laptops. Edel's Acer Aspire 5570Z uses Intel **945GM**; ASUS Eee PC 1000HA uses Intel **945GSE**.

| Chipset | Max Speed | Max RAM | Notes |
|---------|-----------|---------|-------|
| **Intel 945GM** | DDR2-667 (PC2-5300) | **4 GB** (2×2 GB, 64-bit OS) | Must use 667 MHz or slower. 800 MHz may or may not downclock — test solo first. |
| **Intel 945GSE** | DDR2-667 (PC2-5300) | **2 GB** (1 GB onboard + 1 GB slot) | Atom N270/N280 companion. 800 MHz will NOT work. 4 GB is physically impossible. |

**Key rule:** If the chipset says max 667 MHz, a 800 MHz stick is NOT guaranteed to downclock. Some boards (like Edel's Acer 5570Z) accept it solo; others refuse to POST.

## RAM Testing Methodology

When diagnosing a "no display after RAM upgrade" on vintage laptops:

### Step 1: Test Each Stick Solo

Always start with one stick in slot 0 (usually the bottom slot, closer to the motherboard).

| Test | Purpose |
|---|---|
| Original RAM solo | Confirms the slot works |
| Candidate RAM solo | Tests if the stick is compatible at all |
| Candidate in other slot | Tests slot functionality |

### Step 2: Test Pairs

- **Same brand + same speed** → highest chance of working
- **Different brand + different speed** → low chance. Chipset may not handle mixed ranks/timings.
- **Single-rank + double-rank mix** → often fails on 945 chipsets even if speeds match

### Step 3: Interpret "No Display"

| Symptom | Likely Cause |
|---|---|
| Power LED on, fan spins, **no display** | RAM incompatibility (wrong speed, rank, or dead stick) |
| Power LED on, fan spins briefly then stops | Short circuit on motherboard (not RAM) |
| Power LED blinks once then off | Short circuit or overcurrent protection |

### Step 4: Downclock Behavior

An 800 MHz stick plugged into a 667 MHz-only board can have three outcomes:

1. **POSTs fine, downclocks silently** → works. Check with `sudo dmidecode --type memory` or `cat /proc/meminfo` after boot.
2. **POSTs solo but fails in a pair** → the board can downclock one stick but not two mismatched sticks simultaneously.
3. **Refuses to POST entirely** → chipset won't negotiate the higher speed at all. Try a 667 MHz stick.

## Real-World Test Results (19 Temmuz 2026)

From Edel's Acer Aspire 5570Z (Intel 945GM, max 667 MHz):

| Configuration | Result |
|---|---|
| Samsung 512 MB 667 MHz solo | ✅ POST |
| Kingston 2 GB 667 MHz solo | ✅ POST |
| Micron 2 GB 800 MHz solo | ✅ POST (downclocked!) |
| Kingston 2 GB + Samsung 512 MB (both 667) | ❌ No display (rank mismatch: 2Rx8 + 2Rx16) |
| Micron 2 GB + Kingston 2 GB (800+667) | ❌ No display (speed mismatch) |

**Lesson:** Solo sticks of any speed (667 or 800) worked, but pairs failed when ranks or speeds differed. Always test solo first.

## Vintage Laptop Quick Reference

| Model | CPU | Chipset | Max RAM | RAM Type | Notes |
|---|---|---|---|---|---|
| Acer Aspire 5570Z | Pentium Dual-Core T2060/T2080 | 945GM | 4 GB (64-bit OS) | DDR2 667 MHz | SATA HDD, 15.6" |
| ASUS Eee PC 1000HA | Atom N270 (1.6 GHz) | 945GSE | 2 GB (1 GB on-board + 1 slot) | DDR2 667 MHz | PATA/IDE, 10" |
| HP EliteBook 2730p | Core 2 Duo L9400 | GM45 | 8 GB | DDR2 800 MHz | 1.8" Micro SATA, 12" |

## Processor Comparison

When deciding which old laptop to use for Linux:

| CPU | Cores/Threads | Passmark | Relative to Atom N270 |
|---|---|---|---|
| Intel Atom N270 | 1C/2T @ 1.6 GHz | ~150 | **1× (baseline)** |
| Pentium Dual-Core T2060 | 2C/2T @ 1.6 GHz | ~450 | **3× faster** |
| Core 2 Duo L9400 | 2C/2T @ 1.86 GHz | ~800 | **5× faster** |
| Core 2 Duo T7400 | 2C/2T @ 2.16 GHz | ~1000 | **6.5× faster** |

**Bottom line:** Avoid Atom N-series for desktop Linux. Even a low-end Pentium Dual-Core from the same era is dramatically faster. Xubuntu (XFCE) is usable on Pentium Dual-Core with 2+ GB RAM. On Atom N270, even Xubuntu feels sluggish.
