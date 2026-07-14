# Cron Job Iterative Refinement Pattern

## The Pattern

When the user corrects research direction mid-pipeline, don't let stale cron jobs run:

1. **REMOVE** affected queued jobs (`cronjob action=remove job_id=...`)
2. **RECREATE** with refined prompts incorporating feedback
3. **ADJUST** timing so later phases still run after earlier ones
4. **UPDATE** synthesis phase to read new file names

## Example from 2026-05-24 Bardo Session

### Initial attempt (too broad)
```
Faz 2: Google Ads & AI Otomasyon (broad market research)
Faz 3: Alternatif Kanallar & SEO (generic alternatives)
```

### User feedback
Edel: "Faz 2 ve 3 pek efektif değil. GitHub repoları, MCP, AI araçları araştır."

### Refinement loop
```
1. Remove Faz 2 and Faz 3
2. Create Deep 1: GitHub repos + MCP (Tavily)
3. Create Deep 2: AI platforms + Hermes orchestration
4. User feedback again: "Hermes skills de eklensin"
5. Remove Deep 2, recreate + add Deep 2.5 for skills
6. User: "Derinlik arttır" → Add Deep 1.5 (OAuth2/code) + Deep 2.75 (security)
7. Each iteration: update synthesis phase timing and file list
```

## Key Rules

- **Never let stale jobs run** — they waste time and produce irrelevant output
- **Remove before recreate** — `cronjob remove` then `cronjob create`
- **Bump synthesis time** — when adding phases, push the final report later
- **Update synthesis prompt** — add new file names to the `cat` block
- **Check job list** — `cronjob list` after changes to verify no orphans

## Timeline Discipline
- Research phases: 30-70 min apart
- Synthesis: 10-20 min after LAST research phase completes
- If user adds phases: push everything forward
- Don't overlap phases that depend on each other
