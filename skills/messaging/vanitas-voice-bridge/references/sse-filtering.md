# SSE Filtering for Hermes API → Deepgram Bridge

## Problem
Hermes API SSE stream includes custom events that break Deepgram parsing:
```
data: {"choices": [{"delta": {"content": "Hi"}}]}
event: hermes.tool.progress              ← Deepgram chokes here
data: {"tool": "skill_view", ...}
event: hermes.tool.progress
data: {"tool": "skill_view", ...}
data: {"choices": [{"delta": {"content": " Ed"}}]}
```

Deepgram expects pure OpenAI-compatible SSE: only `data:` lines with standard `choices[].delta.content` format. Any `event:` lines cause silent TTS failure.

## Solution: Filter in voice agent proxy endpoint

```python
# In voice_agent_v2.py — proxy_chat endpoint
async def stream_gen():
    async for line in resp.content:
        decoded = line.decode("utf-8", errors="replace")
        
        # ONLY pass "data:" lines — skip "event:" lines entirely
        if decoded.startswith("data:"):
            yield decoded
            if decoded.strip() == "data: [DONE]":
                break
        # event: hermes.tool.* → silently dropped
```

## Verification
```bash
# Should show ONLY data: lines, no event: lines
curl -s -N https://<tunnel>/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"X","messages":[{"role":"user","content":"hi"}],"stream":true}'
```

## Alternative: Disable tools in Hermes API request
If filtering isn't practical, add `"tool_choice": "none"` or `"enabled_toolsets": []` to the payload sent to Hermes API. But this limits functionality for actual chat sessions. Filtering at the bridge level is preferred.
