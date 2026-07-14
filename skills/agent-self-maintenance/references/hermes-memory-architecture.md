# Hermes Memory Architecture Reference

For authoritative details and full quoted excerpts, query the "Hermes Docs" NotebookLM notebook directly (notebook_id stored in the bundled hermes-agent skill). This file is just an index to that source.

## Key concepts

- **3-bucket information model:** Memory holds *facts* (auto-injected by relevance), Skills hold *procedures* (recalled by task similarity), Context files hold *identity* and *project rules*.
- **Memory snapshot is frozen at session start** and scanned for prompt-injection patterns. Poisoned entries get a `[BLOCKED: ...]` placeholder in the system prompt but remain visible in the live state so the user can audit and remove.
- **Self-nudging pattern:** the agent is designed to record important knowledge from interactions to memory or skills.
- **Honcho dialectic:** user model deepens across sessions.
- **External memory providers** are available when built-in lossy summarization is insufficient. Only one at a time, not auto-activated.
- **Profiles** isolate memory, session DB, and skills per domain. Bot tokens are profile-exclusive.
- **Compaction** has a runaway-session safety valve (hygiene hard message limit) and a protect-first-n setting to keep the opening exchange visible.

## Memory sizing rule of thumb

For models with very large context windows (1M+ tokens), raise the memory char limit to 3,000-4,000 — the system docs explicitly recommend raising it for large contexts. The default 2,200 (~800 tokens) is conservative.

## What this skill is NOT

This file is not a copy of the Hermes docs. It is a navigation pointer. For specifics, ask the notebook.

## Citation sources for further reading

The underlying NotebookLM notebook has three source documents covering: memory & skills overview, configuration reference, and Hermes features. Query the notebook with a narrow question to get cited quotes.
