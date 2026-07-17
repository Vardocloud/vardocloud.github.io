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

## Algorithm Structure

### Tile Model
```
Tile(number, color, is_joker, id)
  - number: 1-13 (0 for joker)
  - color: K/S/M/R (X for joker)
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

## Known Fixes Applied

| Bug | Fix |
|-----|-----|
| Joker list mutation crash | Don't `pop()` from joker list; access by `jokers[i]` or copy fresh each iteration |
| First-found=best was wrong | Remove `return` after reaching 101; let backtracking continue for better combos |
| Duplicate combo display | Deduplicate with `frozenset((type, sorted_tile_strings))` signature |
| Pair counting off | Count `(number, color)` tuples, not just number frequency |
| Okey not marked in display | Check `--okey` and `--okey-color` args when parsing tiles |
| Group overlap confusion | Each tile has unique `id`; backtrack uses `set.intersection` for conflict detection |

## Field Notes

- **Pruning heuristic**: look ahead at most 10 remaining sets × their max potential points. Prevents exponential blowup on 21-tile hands.
- **Duplicate tiles matter for groups**: with 2×K5, 2×M5, 2×S5, 2×R5 you can form TWO 4-tile groups (K+M+S+R each). The unique-id system handles this naturally.
- **Cifte gitme (pairs)**: separate analysis, not fed into the main set search. Needs 5 identical pairs (same number + same color). Detected post-search from tile frequency.
- **Output delivery**: via Telegram text. Use `medya:` paths only for photo-sharing to vision model, not for result delivery.

## Test Hands

```
# 21 tiles, should find 108p with 18 tiles used
K1 K1 K2 K3 M3 M4 M5 S2 S3 S4 R5 R6 R7 K8 K9 K10 M11 M12 M13 S7 R10 --okey 5 --okey-color K

# Joker-heavy, elden bitme candidate
K5 K5 M5 M5 S5 S5 R5 R5 K11 K12 K13 M11 M12 M13

# Can't reach 101 — test failure path
K1 K2 K3 S1 S2 S3 M1 M2 M3 K10 K11 K12

# Two jokers, multiple combo paths
K10 K11 K12 M5 M6 M7 S9 S10 S11 OKEY K13 M8 --okey 13 --okey-color K
```

## Script Location

`/home/ubuntu/101_analyzer.py` — production-ready CLI tool.
Usage: `python3 101_analyzer.py -t "K5 K5 M5 R5 S6 S7 S8 M7 M8 M9 K10 K11 K12 R1 R2 R3"`
