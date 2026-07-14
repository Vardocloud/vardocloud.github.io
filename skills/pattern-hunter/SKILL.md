---
name: pattern-hunter
description: "Detect recurring task patterns across sessions, check for skill conflicts, create drafts, and suggest new skills. Gamified pattern hunting system."
category: devops
tags: [pattern-detection, skill-creation, automation, self-improvement, draft]
---

# 🎯 Pattern Hunter

> **Role:** Skill Architect & Pattern Hunter
> **Goal:** Detect reusable patterns before they become repetitive manual work.

## Trigger Mechanism

### Primary — Manual Detection (In-Session)

While working, if I notice I'm doing the same multi-step task for the **2nd+ time**, I pause and check:

| Cue | Example |
|-----|---------|
| "I've done this before" | Processing a YouTube video (3x today) |
| "This feels familiar" | Config change → restart → verify cycle |
| "There's a skill for this somewhere" | Before creating, I check existing skills |

**Checklist before acting:**
1. Is this task ≥ 2 steps? (Single commands don't become skills)
2. Has it occurred ≥ 2 times in recent sessions?
3. Is it generalizable? (Not tied to one specific URL or value)
4. Does an existing skill already cover it? (`skill_view` or `search_files`)

### Secondary — Weekly Cron Scan (Background)

Every Sunday, a cron job scans recent sessions for recurring tool-call sequences:

```
1. session_search for recent sessions (last 7 days)
2. Extract tool call patterns (>2 occurrences of same sequence)
3. Cross-reference with existing skills
4. Report findings as draft entries or confirm "no new patterns"
```

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│                  TRIGGER DETECTED                        │
│  (Manual: 2nd repetition │ Cron: weekly scan)            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│               SKILL CONFLICT CHECK                       │
│  1. skill_view(name) → does a skill with this name exist?│
│  2. search_files("keyword" path="~/.hermes/skills")     │
│  3. If exists: patch existing skill with new info        │
│  4. If partial overlap: decide merge or keep separate    │
└─────────────────────────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        Already covered           New pattern found
              │                         │
              ▼                         ▼
     ┌─────────────────┐     ┌─────────────────────────┐
     │ Log to archive   │     │ Create draft in          │
     │ "already existed"│     │ ~/wiki/skill-drafts/     │
     └─────────────────┘     │ as YYYY-MM-DD-desc.md    │
                             │ Include: detected,        │
                             │ occurrences, evidence,    │
                             │ proposed SKILL.md content │
                             └─────────────────────────┘
                                              │
                                              ▼
                                   ┌──────────────────────┐
                                   │ PRESENT TO EDEL       │
                                   │ "Avladım! [pattern]"  │
                                   │ "Skill yapalım mı?"   │
                                   └──────────────────────┘
                                              │
                                   ┌──────────┴──────────┐
                                   ▼                     ▼
                              Onay                   Red
                                   │                     │
                                   ▼                     ▼
                          skill_manage create     Draft archived
                          Draft removed           Pattern logged
                          README updated          Experience kept
```

## Draft Format

Drafts live in `~/wiki/skill-drafts/` with this frontmatter:

```yaml
---
title: "[DRAFT] skill-name"
description: "One-line description of the pattern"
detected: YYYY-MM-DD
occurrences: N
trigger: "What user action or context triggers this"
role: "Skill Architect"
status: draft
---
```

## Conflict Resolution (Red Lines)

When checking existing skills:

1. **Exact match** → do nothing. Existing skill already covers it.
2. **Partial overlap** → merge the new details into the existing skill via `skill_manage(action='patch')`.
3. **Same domain, different scope** → keep as separate skill with clear boundaries.
4. **Too simple** (< 2 steps OR not generalizable) → reject, log to archive.
5. **Near limit** (140+ skills) → archive an unused skill before creating a new one.

## Pitfalls

- **False positives:** A 3-step task done twice doesn't always warrant a skill. Ask: "Would I save significant time by encoding this?"
- **Overlap blindness:** Always check with `skill_view` and `search_files` — two differently-named skills might do the same thing.
- **Draft rot:** Drafts older than 7 days without user review get auto-cleaned.
- **Language:** All skills must be written in English. Drafts should be in English too.
- **Don't over-engineer:** If the pattern is "check config → restart → verify", that's common sense, not a skill.
