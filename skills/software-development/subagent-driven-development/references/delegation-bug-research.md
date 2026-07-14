# Hermes Delegation Bug — Full Research Report

**Date:** 2026-05-30 | **Researcher:** Vanitas | **Hermes version:** v0.14.0

## The Bug

`delegate_task` ignores all delegation model configuration. Subagents always inherit the parent model.

### Affected Issues
| Issue | Status | Date | Notes |
|-------|--------|------|-------|
| [#12440](https://github.com/NousResearch/hermes-agent/issues/12440) | **OPEN (P1)** | Apr 19, 2026 | "Sub-agent model configuration is ignored" |
| [#11999](https://github.com/NousResearch/hermes-agent/issues/11999) | CLOSED | Apr 18, 2026 | "delegate_task ignores subagent model config" — fix committed by briandevans but incomplete |
| [#17685](https://github.com/NousResearch/hermes-agent/issues/17685) | ? | ? | "per-task model override is silently ignored" |

### Configuration Methods Tested (ALL FAIL)
1. `delegation.model` + `delegation.provider` in config.yaml
2. `delegation.base_url` (custom proxy endpoint)
3. `HERMES_MODEL` environment variable
4. `acp_args` in delegate_task call

### Workaround
```bash
hermes chat -q "task description" --model desired-model
```
This correctly uses the specified model but requires manual terminal invocation — not integrated into the agent loop.

## Alternative Frameworks (if delegation stays broken)

| Framework | Stars | Model-Agnostic | Per-Agent Model | Learning Curve | RAM |
|-----------|-------|----------------|-----------------|----------------|-----|
| **CrewAI** | 44K+ | ✅ | ✅ | Low | ~200MB |
| LangGraph | 35K+ | ✅ | ✅ | High | ~500MB |
| AutoGen/AG2 | 45K+ | ✅ | ✅ | Medium | ~400MB |
| Claude Agent SDK | New | ❌ Claude-only | ✅ | Medium | ~300MB |
| OpenAI Agents SDK | New | ❌ OpenAI-only | ✅ | Low | ~300MB |
| AutoGPT | 180K+ | ❌ Single agent | N/A | Medium | ~500MB |

### Recommendation: CrewAI
- Lowest barrier to entry
- `pip install crewai` — simple setup
- Each agent gets independent model assignment
- Works with Pollinations (free) models
- Light enough for Oracle ARM64 (6GB RAM)
- MIT license

## Two-Phase Strategy
1. **Stay on Hermes** — use terminal workaround for model-specific delegation
2. **Pilot CrewAI** — test with 1-2 critical workflows (e.g., LinkedIn post research)
