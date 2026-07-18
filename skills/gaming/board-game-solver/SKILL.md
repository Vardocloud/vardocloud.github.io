---
name: board-game-solver
description: Build combinatorial game analysis tools for board/card/tile games — set-finding algorithms, optimal-play search, vision integration for physical boards
triggers: [101 okey, 101 hesapla, oyun algoritması, taş analizi, per grup kombinatorik, board game solver, card game algorithm, tile game analysis, en iyi hamle, oyun kazanma algoritması]
owner: Edel
status: active
---

# Board Game Solver

Build combinatorial game analysis tools that find optimal groupings, sets, and strategies for board/card/tile games — especially games like 101 Okey where the challenge is finding valid tile combinations that meet a target score.

## Architecture Pattern

```
Input Layer → Analysis Engine → Strategy Output
  │               │
  ├─ Manual      ├─ Set enumeration (groups, runs, pairs)
  ├─ Photo/      ├─ Combinatorial search (backtracking)
  └─ Vision      └─ Optimization (most tiles used)
```

## General Workflow

### 1. Game Rule → Data Model
Translate game rules into classes before writing any search logic:
- `Tile` — number, color, is_joker, unique_id
- `GameSet` — a valid grouping (run/group/pair), with validity check
- `Hand` — collection of tiles with analysis helpers

**Key design decisions:**
- Give every tile a **unique ID** so duplicate tiles (two copies of K5 in 101) are distinguishable
- Make set validation a **property/method on the set class**, not a separate function — keeps rules self-contained
- Sort sets by **points descending** before search — high-value sets first improves pruning

### 2. Set Enumeration
Find ALL valid sets a hand can form:
- **Groups** — same number, different colors, 3+ tiles
  - Group tiles by number, then by color
  - Generate all unique-color combinations with `itertools.combinations`
  - Handle duplicate color-tiles with `itertools.product`
- **Runs** — same color, consecutive numbers, 3+ tiles
  - Group tiles by color, sort by number
  - For each start position, try lengths 3–7
  - Check consecutiveness before building combinations
- **Joker integration** — jokers fill gaps or extend existing sets
  - For groups: jokers add to reach 4-tile group
  - For runs: jokers pad start/end OR fill gaps between numbers (gap ≤ joker count)

```python
# Pattern for generating tile combinations across colors
by_color = defaultdict(list)
for t in tiles:
    by_color[t.color].append(t)

for color_combo in itertools.combinations(colors_available, r):
    choices = [by_color[c] for c in color_combo]
    for selection in itertools.product(*choices):
        # selection is one tile from each color
```

### 3. Combinatorial Search (Backtracking)
Given all candidate sets, find the optimal combination:

```
backtrack(start_idx, selected, used_ids, current_points):
    if current_points >= target:
        save combination
        # CONTINUE searching — don't return! Better combos may exist
        # (more tiles used = better strategy)
    
    for each remaining set:
        if all its tiles are unused:
            select it
            backtrack(next_idx, ...)
            deselect it
    
    prune: estimate max future points from remaining sets
           if current + max_future < target → skip
```

**Critical: continue after reaching target.** Returning on first valid combination misses better outcomes (more tiles used, less remaining hand).

### 4. Deduplication
The same visual combination can appear multiple times from different tile-id permutations. Deduplicate the final result list:

```python
seen = set()
unique = []
for c in combinations:
    sig = frozenset(
        (s.type_name, tuple(sorted(t.short() for t in s.tiles)))
        for s in c['sets']
    )
    if sig not in seen:
        seen.add(sig)
        unique.append(c)
```

### 5. Input Strategy — Three-Tier

For board/card/tile game solvers, there are three input approaches ranked by speed:

1. **Manual input** (fastest during development) — user types tile codes, you run the solver
2. **Photo → vision** — user sends photo, you use vision_analyze to extract tiles, then run solver
3. **Mobile web app** (fastest at the game table) — Flask app served over Tailscale, user taps tiles on their phone

#### Tier 2: Photo → vision

For the photo path, the flow is:
```
User → sends photo + "okey şu taş" → 
You → vision_analyze(image_path, question="list tiles in format K5, Y11, M3, ...") →
You → parse extracted tiles → run solver →
You → send strategy result
```

**Always ask for the okey/joker info when photo is involved** — it's rarely visible in the photo.

**Vision pitfalls specific to tile games:**
- Color ambiguity under artificial light (Mavi looks like Siyah — use the "3 copies rule" to detect: each tile appears exactly twice in the deck)
- Lighting shifts yellow → orange (user might say "turuncu" for yellow)
- The false joker has a distinctive star symbol

See `references/101-okey-algorithm.md` → "Vision Integration — Pitfalls for 101" for the full prompt template and detection strategies.

#### Tier 3: Mobile web app (Tailscale + Flask)

When the user must input tiles in seconds during live play:
```
User phone → Tailscale → Flask server (your machine) → solver engine
```

The frontend is a single HTML page with big tap targets (color buttons + number grid). The backend is a Flask app that calls the same solver functions and returns JSON.

Key design for the app:
- 4 color buttons (🔴K 🟡Y 🔵M ⚫S) — tap to select
- 7-column number grid (1-13 + OKEY) — tap to add tile
- Tile list shows entered tiles, tap to remove
- Okey dropdown shown as a badge
- All logic in a single Flask file; no database, no state

See `references/101-okey-algorithm.md` → "Web App for Mobile Input" for setup instructions and the full frontend/backend description.

## Pitfalls

- **Don't share mutable joker lists** across loop iterations — slice `jokers[:]` fresh or use index-based access instead of `.pop()`
- **Don't use `return` on first 101+** — continue searching for higher-tile-use combinations
- **Duplicate tiles require unique IDs** — otherwise set equality checks break and tiles get double-counted
- **Pair counting != occurrence counting** — a "pair" is two identical tiles (same number AND same color). Count `(number, color)` combos, then integer-divide by 2
- **Sort candidate sets by points descending** — this makes the first-found combination the most-points-per-set one, and the search finds better ones by exploring further
- **Combinatorial explosion guard** — with 21+ tiles, prune aggressively (limit lookahead to ~10 sets, skip sets that overlap with used tiles)
- **Vision output needs parsing** — LLM vision responses are free-form. Use a specific prompt template requesting "K5 Y11 M3" format
- **Color naming must be unambiguous** — don't use `S` for both "Sarı" and "Siyah". Use K/Y/M/S: K(Kırmızı), Y(Sarı), M(Mavi), S(Siyah). Never use `R` for Siyah — Turkish speakers won't guess it.
- **Python module names can't start with digits** — `101_analyzer.py` cannot be imported (`from 101_analyzer import ...` is a syntax error). Rename to start with a letter (e.g., `okey_analyzer.py`)
- **Cloudflared path** — the binary is at `~/.hermes/bin/cloudflared`, not in the general PATH. Use the full path or add `~/.hermes/bin` to PATH when deploying tunnels.

## Reference Files

- `references/101-okey-algorithm.md` — full implementation details for 101 Okey: game rules, K/Y/M/S color convention, backtracking solver, pair/grup/per detection, çifte gitme analysis, Flask web app setup, vision integration pitfalls, and Cloudflare Tunnel deployment

## Related Skills

- `ai-game-companion` — real-time game watching, different domain (story tracking vs combinatorial analysis)
