# Hermes Prompt Architecture & Cache Behavior (10 Tem 2026)

## Discovery: Source-Code-Level Prompt Structure

Found in `agent/system_prompt.py` (lines 347-363) — the actual 3-layer prompt:

```
STABLE (~8KB) — never changes
  identity, SOUL, tool guidance, skills, platform hints

CONTEXT (~16KB) — stable per session  
  project context files (COMPASS/CLAUDE/etc.)

VOLATILE (~3KB) — may change
  memory snapshot, user profile
  "Conversation started: <date-only>"  ← AT THE END
```

**Key findings from source code:**
- Timestamp is **date-only** (no minute precision) — changes once/day
- Prompt is **built once per session**, then cached (line 350-353)
- Explicit comment: "Layers are ordered cache-friendly: stable first, then context, then volatile" (line 355-358)
- Quote: "The whole string is treated as one cached block — Hermes never rebuilds or reinjects parts of it mid-session, which is the only way to keep upstream prompt caches warm across turns."
- Result: **~89% natural cache hit rate** (24KB stable / 27KB total)

## Conclusion

- Hermes is **already prompt-cache-optimized** by design
- No anchor or reordering needed — the 3-layer structure handles it
- MEMORY.md optimization (44% size reduction) remains the most impactful change
- The only daily cache invalidation: midnight timestamp rollover

## Source

- `agent/system_prompt.py::build_system_prompt()` and `build_system_prompt_parts()`
- `agent/prompt_builder.py::build_context_files_prompt()` (line 1482-1521)
