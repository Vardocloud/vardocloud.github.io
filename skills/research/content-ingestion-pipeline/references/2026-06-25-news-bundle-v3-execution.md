# Bundle Gündem v3 — 25 Haziran 2026 Execution Reference

## Context
- **Cron job**: 25 Haziran 2026 Perşembe, scheduled run
- **Format**: Bundle Gündem İşleme v3 — Akıllı Haber Filtreleme + 5N1K Anlatım
- **Goal**: 8-10 news items, min 6 from tech/science
- **User instruction**: Tech/science heavy, economy 1-2 max, gossip/sports skip

## Source Strategy (This Run)

Bypassed BBC entirely due to persistent ERR_BLOCKED_BY_CLIENT issues on previous runs.
Used instead:

### Primary Sources
1. **ScienceDaily** (sciencedaily.com) — main page + individual article extraction
   - Front page: lists ~30-40 headlines with 2-3 sentence summaries
   - Individual articles: full text via web_extract on `/releases/2026/06/*.htm` URLs
   - Strong for: space, health, biology, neuroscience, geology, physics
2. **Web search** (`web_search`) — targeted queries for specific topics
   - "OpenAI chip Broadcom" → TechCrunch/Reuters results
   - "Micron Qualcomm AI chip" → Reuters
3. **BBC News** — only via web_search results, NOT direct web_extract (BBC pages return ERR_BLOCKED_BY_CLIENT)

### What Worked
- ScienceDaily's individual article URLs extract cleanly (no JS, no blocking)
- web_search returns publishable article URLs even for BBC/Reuters
- Parallel web_search queries for different topics (AI chip, corporate news, science breakthroughs)
- write_file for batch wiki entries (6 files in parallel, no issues)

### What Didn't Work
- BBC web_extract: Still blocked by edigitalsurvey.com script (ERR_BLOCKED_BY_CLIENT)
- BBC sub-pages: `/news/technology` and `/news/business` return empty content
- Solution: Use web_search to find BBC stories, cite them from the search snippet + source attribution

## 5N1K Output Format Used

Each item followed this exact pattern:

```
**🔬/📱/📊/🌿 [Category] — [Headline]**

[3-4 sentence 5N1K summary: what happened, who did it, where/how, why it matters]

📎 [Source Name]
```

Items separated by `---` divider.
Final section: "Öne çıkan tema" summarizing the overall trend.

## Wiki Storage

7 files created under `~/wiki/news/`:
- `science/2026-06-25-placebo-memory.md` — Placebo effect study
- `science/2026-06-25-lucy-donaldjohanson-asteroid.md` — NASA Lucy asteroid water
- `science/2026-06-25-dev-black-coral.md` — 400-year-old coral discovery
- `science/2026-06-25-osteopenia.md` — Osteopenia global prevalence
- `science/2026-06-25-sardis-unesco.md` — Sardis UNESCO heritage site
- `tech/2026-06-25-openai-jalapeno-chip.md` — OpenAI Broadcom chip
- `tech/2026-06-25-micron-qualcomm-ai-chip-rally.md` — Chip stock rally

Each file has: YAML frontmatter (source, date), Özet, Veriler (data/statistics), Çıkarım (takeaway).

## processed_titles.md Status
- File size: ~29,011 chars at session start
- Status: ABOVE 15K threshold — rotation due
- Lesson: Add rotation monitoring to the skill's startup checklist

## Lessons for Future Runs
1. BBC direct extraction is unreliable — use web_search to find BBC stories, cite from snippets
2. ScienceDaily individual article URLs are the best science source (clean extraction, detailed content)
3. Tech news best sourced via web_search (multiple outlets: TechCrunch, Reuters, WSJ)
4. When BBC fails entirely, ScienceDaily + web_search can still produce 10 science+tech items
5. processed_titles.md at ~29K needs rotation before next run
6. write_file is safe for batch wiki entries in cron mode (used 6 parallel writes)
7. The compaction summary mechanism can break (401 CreditsError on DeepSeek V4) — deterministic fallback works but loses detail
