# 101 Okey Solver — Implementation Reference

## Game Rules Summary

| Rule | Detail |
|------|--------|
| Deck | 106 tiles: 4 colors × 13 numbers × 2 copies + 2 false jokers |
| Hand | 21 tiles each, dealer's right gets 22 |
| Okey | Indicator tile's number+1 (same color). Wraps: 13→1 |
| Joker value | 50 points |
| Group (Grup) | Same number, different colors, 3-4 tiles |
| Run (Per) | Same color, consecutive numbers, 3+ tiles. No 13-1-2 wrap |
| Min open | 101 points from valid sets |
| Pairs (Çift) | 5 pairs = alt win condition (identical tiles, same number+color) |
| Scoring | -101 for winner, 202 penalty for unopened players |

## Color Naming Convention — Critical

The 4 colors in 101 must use an **unambiguous** scheme. The naive `S` for "Sarı" collides with `S` for "Siyah" — Turkish speakers naturally use `S` for both.

| Color | Code | Rationale |
|-------|------|-----------|
| Kırmızı (Red) | **K** | First letter, unique |
| Sarı (Yellow) | **Y** | From English "Yellow"; avoids S/Siyah collision |
| Mavi (Blue) | **M** | First letter, unique |
| Siyah (Black) | **S** | First letter, unique now that Sarı uses Y |

**Do NOT use `R` for Siyah** — it's unintuitive and nobody guesses it. Always use K/Y/M/S.

In the CLI: `--tiles "S12 S9 M10 S11 OKEY Y2 Y2 M7" --okey 11 --okey-color S`

## Algorithm Structure

### Tile Model
```
Tile(number, color, is_joker, id)
  - number: 1-13 (0 for joker)
  - color: K/Y/M/S (X for joker)
  - is_joker: bool
  - id: unique int (critical for duplicate tile distinction)
```

### Set Model  
```
TileSet(tiles)
  - is_group: same number, all different colors
  - is_run: same color, consecutive numbers (jokers OK to fill gaps)
  - points: sum of tile points (face value or 50 for joker)
  - Validates using TileSet._classify() on construction
```

### Search Flow
```
1. find_groups(hand)
   → Group by number → by color → generate triples/quadruples
   → Add jokers to reach 4-tile groups
   
2. find_runs(hand)
   → Group by color → sort → enumerate consecutive sequences
   → Try lengths 3-7
   → Pad with jokers (before, after, or inside gaps)
   
3. find_best_combinations(hand, target=101)
   → Merge groups + runs → deduplicate → sort by points desc
   → Backtrack: try sets, track used tile IDs, prune optimistically
   → Save ANY combo reaching 101+ (don't return early)
   → Rank: most tiles used > highest points
   
4. analyze_hand(hand) → formatted output
   → Run search → format results → add pair analysis → add tips
```

## Web App for Mobile Input

For real-time game play, typing tiles in a CLI is too slow. The solution is a **Flask web app** served over Tailscale (or Cloudflare Tunnel as fallback):

```
User phone ── Tailscale ── Server (Flask + solver)
User phone ── Cloudflare ── Server (Flask + solver)  [fallback]
```

### Setup
```bash
pip install flask
# Start the app
python3 101_app.py
# Listen on 0.0.0.0:5000
```

### Deployment — Two Methods

#### Method A: Tailscale (preferred)
If both devices are on the same Tailscale network:
```bash
# Make sure the Flask app listens on 0.0.0.0:5000
# User accesses at http://<tailscale-ip-or-hostname>:5000
# e.g., http://sakabato.tail9c7788.ts.net:5000
```

#### Method B: Cloudflare Tunnel (fallback when Tailscale not available)
If the user can't access Tailscale (not installed on phone, network issues):
```bash
# cloudflared is usually pre-installed (~/.hermes/bin/cloudflared)
cloudflared tunnel --url http://localhost:5000
# Gives a URL like: https://random-name.trycloudflare.com
# User opens this URL on their phone — no installation needed
```
The tunnel is ephemeral — it lasts as long as the cloudflared process runs. Restarting generates a new URL.

**Important:** Ensure the Flask app binds to `0.0.0.0` (not `127.0.0.1`) so cloudflared can reach it from localhost.

### Frontend Design (Mobile-First)
- **Color row**: 4 big buttons (🔴K 🟡Y 🔵M ⚫S), tap to select
- **Number grid**: 7-column grid of 1-13 + OKEY button
- **Tile list**: shows entered tiles, tap to remove
- **Okey selector**: dropdown for number + color, shown as a badge
- **Analyze button**: POSTs tiles to `/analyze`, renders results
- Single HTML page served by Flask

### Backend (Flask)
- `GET /` — serves the HTML page
- `POST /analyze` — accepts `{tiles: [...], okey_num, okey_color}`, returns JSON with combos
- Calls the same `find_best_combinations()` from the core solver
- Deduplicates combos, checks pairs, formats for frontend

### When to Use Which

| Situation | Method |
|-----------|--------|
| At desk / computer | CLI: `python3 okey_analyzer.py -t "..." --okey 11 --okey-color Y` |
| At game table, phone in hand | Web app over Tailscale |
| Photo available + okey known | Send photo + okey info → vision_analyze → extract → solve |

## Vision Integration — Pitfalls for 101

When reading tiles from a photo, 4 specific problems arise:

1. **Color ambiguity**: Under artificial/warm light, **Mavi (blue) tiles look almost identical to Siyah (black)**. A tile you'd swear is Siyah 9 might be Mavi 9.

2. **The "3 copies" reality check**: Each tile appears exactly twice in the deck. If vision reports 3 copies of any `(number, color)` combo, at least one is actually a different color (Mavi masquerading as Siyah). Use this as a signal to re-examine.

3. **Lighting shifts Sarı → Turuncu**: Yellow tiles look orange under warm indoor light. The user might say "turuncu 11" — that's Sarı 11.

4. **Sahte Okey detection**: The false joker tiles have a distinctive star/dot symbol on them. When vision sees "11 with a star", that's the false joker (50 points), not a regular 11.

### Vision Analysis Prompt Template

When extracting tiles from a photo, use this specific prompt:

```
This is a 101 Okey player's hand from a photo. List every tile on the rack.
Be careful about color: under artificial light, MAVI (blue) looks almost identical to SIYAH (black).
Use the "3 copies rule" — each tile appears only twice, so if you see 3 of one combo, one must be blue.

Format: COLOR+NUMBER for each tile, space-separated.
Colors: K(Kırmızı/red), Y(Sarı/yellow), M(Mavi/blue), S(Siyah/black)
Example: "S12 S9 M10 S11 Y2 Y2 M7 K6 K5 K5 K6"

Mark the false joker as "OKEY" if it has a star symbol.
```

## Known Fixes Applied

| Bug | Fix |
|-----|-----|
| Joker list mutation crash | Don't `pop()` from joker list; access by `jokers[i]` or copy fresh each iteration |
| First-found=best was wrong | Remove `return` after reaching 101; let backtracking continue for better combos |
| Duplicate combo display | Deduplicate with `frozenset((type, sorted_tile_strings))` signature |
| Pair counting off | Count `(number, color)` tuples, not just number frequency |
| Okey not marked in display | Check `--okey` and `--okey-color` args when parsing tiles |
| Group overlap confusion | Each tile has unique `id`; backtrack uses `set.intersection` for conflict detection |
| Invalid Python module name | Rename from `101_analyzer.py` → `okey_analyzer.py` (Python can't `import` names starting with digits) |
| Color naming collision | Changed from `K/S/M/R` to `K/Y/M/S` — `R` for Siyah is unintuitive and `S` for Sarı collides with Siyah |
| Tailscale unreachable | Use `cloudflared tunnel --url http://localhost:5000` for a public `*.trycloudflare.com` URL — no client installation needed |

## Field Notes

- **Pruning heuristic**: look ahead at most 10 remaining sets × their max potential points. Prevents exponential blowup on 21-tile hands.
- **Duplicate tiles matter for groups**: with 2×K5, 2×M5, 2×Y5, 2×S5 you can form TWO 4-tile groups (K+M+Y+S each). The unique-id system handles this naturally.
- **Çifte gitme (pairs)**: separate analysis, not fed into the main set search. Needs 5 identical pairs (same number + same color). Detected post-search from tile frequency.
- **Module import name**: Python files starting with a number (like `101_analyzer.py`) cannot be imported with `from ... import`. Always rename to a letter-starting name (e.g., `okey_analyzer.py`).
- **Output delivery**: via Telegram text.

## Test Hands

```bash
# 21 tiles, should find 108p with 18 tiles used
python3 okey_analyzer.py -t "K1 K1 K2 K3 M3 M4 M5 Y2 Y3 Y4 S5 S6 S7 K8 K9 K10 M11 M12 M13 Y7 S10" --okey 5 --okey-color K

# Joker-heavy, elden bitme candidate
python3 okey_analyzer.py -t "K5 K5 M5 M5 Y5 Y5 S5 S5 K11 K12 K13 M11 M12 M13"

# Can't reach 101 — test failure path
python3 okey_analyzer.py -t "K1 K2 K3 Y1 Y2 Y3 M1 M2 M3 K10 K11 K12"

# Two jokers, multiple combo paths
python3 okey_analyzer.py -t "K10 K11 K12 M5 M6 M7 Y9 Y10 Y11 OKEY K13 M8" --okey 13 --okey-color K

# Photo test — 20-tile hand, okey=11-Y, should find 144p with 13t used
python3 101_app.py
# Then POST: {"tiles":["S12","S9","M10","S11","OKEY","Y2","Y2","M7","K6","K5","K5","K6","S9","S9","S12","S12","S10","S10","K4","K4"],"okey_num":11,"okey_color":"Y"}
```

## Script Locations

| File | Purpose |
|------|---------|
| `/home/ubuntu/okey_analyzer.py` | Core solver — CLI tool, algorithm engine |
| `/home/ubuntu/101_app.py` | Flask web app for mobile input |
| `~/.hermes/bin/cloudflared` | Cloudflare Tunnel binary (deployment fallback) |

Usage: `python3 okey_analyzer.py -t "K5 K5 M5 R5 Y6 Y7 Y8 M7 M8 M9 K10 K11 K12 S1 S2 S3"`
