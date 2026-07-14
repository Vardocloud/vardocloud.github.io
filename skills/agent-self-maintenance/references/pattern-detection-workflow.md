# Pattern Detection Workflow (09 Jun 2026)

Detect recurring task patterns and convert them into skills.

## Red Lines (immutable rules)

1. **Uniqueness** — No two skills do the same thing. If overlap found, update existing skill instead.
2. **Single scope** — One skill = one task. No scope creep.
3. **Hierarchy** — Specific > General. Newer > Older (equal specificity). User-approved > Auto-detected.
4. **Approval gate** — Auto-detected patterns become DRAFT only. User must approve before becoming skill.
5. **Hard limit** — 150 skills max. New skill = old/stale skill archived.
6. **Threshold** — ≥2 repetitions, ≥2 steps, generalizable.

## Detection Flow

```
1. Pattern repeats 2+ times → recognize
2. Search existing skills for overlap → search_files
3. No overlap → save draft to ~/wiki/skill-drafts/draft-YYYY-MM-DD-slug.md
4. Present to user: "I noticed this pattern, turn it into a skill?"
5. Approved → skill_manage create, remove from drafts
6. Rejected → keep in /tmp/raw/ for reference, remove from drafts
7. 7 days unapproved → auto-cleanup draft
```

## Draft Template

```markdown
---
title: "[DRAFT] skill-name"
description: "Concise description"
detected: YYYY-MM-DD
occurrences: N
trigger: "What triggers this pattern"
role: "Skill Architect"
status: draft
---

## Detected Pattern
[How many times, in what contexts]

## Proposed SKILL.md
[Full proposed skill content]

## Evidence
[Sessions, examples]

## Overlap Check
[Existing skills checked, overlap status]
```
