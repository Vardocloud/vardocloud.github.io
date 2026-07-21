# Media Watch Newsletter — Compilation Processing (21 Tem 2026)

APA Media Watch is a **compilation newsletter**, not original APA content. It aggregates 10-20
external news stories where APA, APA members, or APA research are cited in the press. The
processing strategy differs fundamentally from Monitor articles, Practice Update, or Press Releases.

## Signal Extraction

### ✅ HIGH VALUE — extract these into the wiki file

- Named APA member/researcher with **direct quote** (e.g. "Kelly Rohan says extreme heat...")
- "APA Journals in the News" research references (shows what academic research reaches public)
- APA press release picked up by major national outlets
- Newsworthy APA official position/statement on a current event

### ❌ LOW VALUE — skip these without extraction

- Generic "according to the American Psychological Association" passing mentions
  → no named person, no unique quote, no new information
- "APA Members in the News" segment without substantive content
  → just namedropping "Dr. X was interviewed by Y" without the actual substance
- Wire service articles (AP, Reuters) that just recycle APA press releases
  → the press release itself is the primary source, not the wire coverage
- Stories that mention APA only in one tangential sentence
  → e.g. "student at university that has APA accreditation"

## Processing Rules

1. **Create ONE wiki file per issue** — `YYYY-MM-DD-media-watch.md`, not per-item files
2. **Extract 2-5 highest-signal items** from the typical 10-20 total citations
3. **Each extracted item format:**
   - **Topic:** one-line summary
   - **Source:** named member/researcher + outlet
   - **Key quote/conclusion:** what they said (1-2 sentences)
   - **Why it matters:** clinical or research relevance (1 sentence)
4. **For NotebookLM:** ONE source entry with compiled content, not per-item
5. **Skip items where the APA connection is tangential** — no need to document every single mention

## Why This Matters

Without explicit guidance, a pipeline run would:
- Create 15+ separate wiki files for each news clip → index clutter
- Make 15+ tool calls for extraction → budget waste
- Flood NotebookLM with 15+ trivial source entries → noise

The actual signal in a typical Media Watch issue is 3-6 entries with named members.
This rule preserves the signal while avoiding tool budget and index pollution.

## Confirmed Pattern (21 Tem 2026)

The July 10-17 Media Watch had 15+ citations. High-value items extracted:

| # | Topic | Named Source | Outlet |
|---|-------|-------------|--------|
| 1 | Heat Waves & Mental Health (ER visits +8%) | Kelly Rohan (UV), Susan Clayton (Wooster) | CNN, NBC News |
| 2 | Teens Turning to AI Chatbots (1 in 5) | Mitch Prinstein (APA Chief Science Officer) | NPR |
| 3 | Romance Scams $1.3B in losses | Julianne Holt-Lunstad (BYU) | NBC News |
| 4 | "Maxxing" Optimization Trend | Jennifer Hartstein | Good Morning America |

All four had named APA members with **direct quotes** giving expert commentary. The remaining 10+
items were generic "according to APA" passing mentions in wire stories — skipped.

## Relation to Other Formats

| Content Type | Processing | Files per Item | NBLM Entries |
|-------------|-----------|---------------|--------------|
| Monitor article | Full extraction + wiki | 1 file per article | 1-2 entries (EN + TR) |
| Practice Update | Full extraction + wiki | 1 file per issue | 1 entry |
| Press Release | Full extraction + wiki | 1 file per release | 1 entry |
| **Media Watch** | **Filtered extraction** | **1 file per issue** | **1 entry** |
| Events listing | Brief metadata | 1 file per month | 1 entry |
