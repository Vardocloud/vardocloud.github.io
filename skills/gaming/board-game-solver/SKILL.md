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

### 5. Vision Integration
Two-tier input strategy:
1. **Manual input** (fastest) — user types tiles, you run the solver
2. **Photo → vision** — user sends photo, you use vision_analyze to extract tiles, then run solver

For the photo path, the flow is:
```
User → sends photo + "okey şu taş" → 
You → vision_analyze(image_path, question="list tiles in format K5, S11, ...") →
You → parse extracted tiles → run solver →
You → send strategy result
```

**Always ask for the okey/joker info when photo is involved** — it's rarely visible in the photo.

## Pitfalls

- **Don't share mutable joker lists** across loop iterations — slice `jokers[:]` fresh or use index-based access instead of `.pop()`
- **Don't use `return` on first 101+** — continue searching for higher-tile-use combinations
- **Duplicate tiles require unique IDs** — otherwise set equality checks break and tiles get double-counted
- **Pair counting != occurrence counting** — a "pair" is two identical tiles (same number AND same color). Count `(number, color)` combos, then integer-divide by 2
- **Sort candidate sets by points descending** — this makes the first-found combination the most-points-per-set one, and the search finds better ones by exploring further
- **Combinatorial explosion guard** — with 21+ tiles, prune aggressively (limit lookahead to ~10 sets, skip sets that overlap with used tiles)
- **Vision output needs parsing** — LLM vision responses are free-form. Use a specific prompt template requesting "K5 S11 M3" format

## Reference Files

- `references/101-okey-algorithm.md` — full implementation details for 101 Okey, including the O(tiles × sets) backtracking solver, pair/grup/per detection, and çifte gitme analysis

## Related Skills

- `ai-game-companion` — real-time game watching, different domain (story tracking vs combinatorial analysis)
