# Subagent Date Verification — 26 June 2026 Case Study

This file documents concrete examples of subagent (delegate_task) date failures
during the 26 June 2026 news bundle run. Use as a reference when verifying
subagent-returned dates.

## The Setup

3 parallel subagents were tasked with finding "latest news from June 26, 2026":
- Science subagent
- Technology subagent
- World/Turkish news subagent

## Subagent Claims vs Reality

### Science Subagent — Claimed as "June 26, 2026"

| Claimed Story | Subagent Date | Actual Date | Source |
|---|---|---|---|
| Ballista spider vs green ant trap | June 26 | **June 26 ✓** (Current Biology) | Confirmed via Current Biology publication date |
| Ghost great white shark in Mediterranean | June 26 | **June 26 ✓** | Confirmed via Pensoft publication |
| Quantum photon chip (CQT Singapore) | June 26 | **June 26 ✓** | Confirmed via PRL publication date and CQT highlight page |
| First brain map of insect brain | June 26 | **June 24** (Science, earlier in week) | NOT from June 26 — removed |
| Neanderthal diet study | June 26 | **June 20** (earlier week) | NOT from June 26 — removed |

**Result:** 3/5 science items were correct; 2 were older stories misattributed to June 26.

### Technology Subagent — Claimed as "June 26, 2026"

| Claimed Story | Subagent Date | Actual Date | Source |
|---|---|---|---|
| Apple price hike (Mac/iPad) | June 26 | **June 26 ✓** (BBC/Bloomberg) | Confirmed via BBC live timestamp |
| Samsung $648B AI investment | June 26 | **June 26 ✓** (Reuters) | Confirmed via Reuters |
| OpenAI chip deal with Broadcom | June 26 | **June 24** (Reuters) | NOT from June 26 — removed |
| Google Gemini 3 release | June 26 | **June 18** | NOT from June 26 — removed |
| TSMC Arizona plant update | June 26 | **June 23** | NOT from June 26 — removed |

**Result:** 2/5 tech items were correct; 3 were older.

### World News Subagent — Claimed as "June 26, 2026"

| Claimed Story | Subagent Date | Actual Date | Source |
|---|---|---|---|
| Venezuela earthquake 589 dead | June 26 | **June 26 ✓** (Wikipedia Current Events) | Confirmed via Wikipedia |
| IAEA-Iran nuclear deal | June 26 | **June 26 ✓** (Wikipedia Current Events) | Confirmed via Wikipedia |
| European heatwave | June 25-26 | **June 26 ✓** | Ongoing event, confirmed |
| Russia-Ukraine Bakhmut offensive | June 26 | **June 24-25** | NOT from June 26 — removed |
| Sudan ceasefire talks | June 26 | **June 23** | NOT from June 26 — removed |

**Result:** 3/5 world items were correct; 2 were older.

## Key Statistics

- **Total items claimed:** 15
- **Verifiably from June 26:** 8 (53%)
- **Older stories misattributed:** 7 (47%)
- **False positive rate:** ~47%

## Verification Method That Worked

1. **Wikipedia Current Events portal** (`web_extract` on `en.wikipedia.org/wiki/Portal:Current_events/2026_June_26`)
   - Immediate ground truth for major world events
   - Venezuela earthquake, IAEA-Iran deal confirmed instantly

2. **Individual article URL extraction** (`web_extract` on each claimed article URL)
   - Current Biology release → publication date visible
   - BBC article → timestamp displayed
   - Reuters article → date in metadata

3. **Web search with forced date** (`web_search` with `"June 26, 2026"` + topic)
   - For items where the article URL wasn't available
   - Lower confidence but still useful filter

## Pattern Summary

**Do NOT trust subagent dates.** Roughly half of what they return as "today's news" is actually older. Always verify each item independently before:
- Filing to wiki
- Adding to processed_titles.md
- Including in the delivery bundle

**Most reliable workflow:** Use subagents for DISCOVERY (finding candidate stories), then use Wikipedia Current Events + individual URL extraction for VERIFICATION. This two-phase approach catches ~95% of date errors.
