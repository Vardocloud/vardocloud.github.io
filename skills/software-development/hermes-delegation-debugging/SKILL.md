---
name: hermes-delegation-debugging
description: "Debug Hermes delegation/subagent failures — provider resolution, base_url inheritance, content filter blocks."
version: 1.0.0
author: Vanitas
metadata:
  hermes:
    tags: [debugging, delegation, subagent, provider, troubleshooting]
    related_skills: [systematic-debugging, subagent-driven-development, hermes-agent]
---

# Hermes Delegation Debugging

> **PITFALL:** During diagnostics, use `hermes config get <key>` for single values — never paste raw config file contents into messages. Edel considers this a security violation. Also: prefer `web_extract` (Firecrawl) over `browser_navigate` for reading docs when possible.

## Overview

When `delegate_task` subagents fail (blocked, 404, timeout), the root cause is almost always in the **credential/provider resolution chain** — not in the subagent goal or toolsets. This skill covers the systematic approach to diagnosing and fixing delegation failures.

## When to Use

- `delegate_task` returns `"Your request was blocked."`, `"error"`, or empty results
- Subagents fail with HTTP 403/404 before making any tool calls
- Subagents die immediately with `max_iterations` but `tokens=0`
- Provider appears as `custom` in logs when you expected a specific provider

## The Diagnostic Pipeline

### Step 1: Read the Logs

The logs tell you exactly where the request went:

```bash
grep "subagent\|provider=.*base_url=" ~/.hermes/logs/agent.log | tail -20
```

Look for lines like:
```
provider=custom base_url=https://api.deepseek.com/v1 ... HTTP 404
provider=pollinations base_url=https://gen.pollinations.ai/v1 ... HTTP 403
```

Key signals:
- `provider=custom` instead of expected provider → delegation config isn't resolving correctly
- `base_url` pointing to wrong endpoint → `delegation.base_url` is empty, inherited from parent
- `HTTP 403: Your request was blocked` → content safety filter on the provider side
- `HTTP 404: Oh no, there's nothing here` → wrong base_url, hitting incorrect endpoint

### Step 2: Verify Delegation Config

```bash
hermes config get delegation
```

**CRITICAL PITFALL — `base_url` inheritance:**
In `delegate_tool.py` line 1023:
```python
effective_base_url = override_base_url or parent_agent.base_url
```
When `delegation.base_url` is empty (`""`), the subagent inherits the **parent agent's base_url**, which belongs to a completely different provider. This is the #1 cause of "wrong endpoint" failures.

**Fix:**
```bash
hermes config set delegation.base_url "https://CORRECT_PROVIDER_URL/v1"
```

### Step 3: Isolate Provider vs Content Filter

After fixing `base_url`, if you still get blocks:

1. **Test the provider directly** (bypass Hermes delegation): use `execute_code` with Python `requests` to call the provider's chat completions endpoint — first with a simple message, then with tools. If both work, the provider API is fine.

2. **If direct API works but Hermes delegation fails** → provider content filter is rejecting Hermes's large system prompt. This is a provider-side policy issue, not a Hermes bug.

3. **Resolution paths for content filter blocks:**
   - Contact provider support for whitelist
   - Use a different provider for delegation (OpenRouter, direct Mistral, etc.)
   - Check provider's safety settings dashboard

### Step 4: Check API Key Scope

The `delegation.api_key` is separate from `custom_providers` API keys. Verify:
- `delegation.api_key` is set and valid
- The key has the necessary permissions (sk_ for server-side)
- The key isn't tied to a different tier/region restriction

```bash
hermes config get delegation.api_key
```

## Common Failure Patterns

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `provider=custom` in logs | `delegation.provider` not resolving to custom_providers entry | Set `delegation.base_url` explicitly |
| `HTTP 404: Oh no, there's nothing here` | base_url points to wrong provider | Set correct `delegation.base_url` |
| `HTTP 403: Your request was blocked` | Provider content filter rejecting system prompt | Contact provider, or switch provider |
| `Connection error` after retries | Network/firewall, or wrong base_url | Verify base_url, check proxy |
| `max_iterations` with `tokens=0` | Child never reached first API call | Check base_url, provider, auth |

## Provider-Specific Quirks

See `references/` for provider-specific investigation reports:
- `references/pollinations-content-filter.md` — Pollinations 403 block investigation
