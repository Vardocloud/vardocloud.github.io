# Deepgram Voice Agent — Custom LLM Format Requirements

**Date:** 2026-06-14
**Source:** [GitHub Discussion #1034](https://github.com/orgs/deepgram/discussions/1034), [Deepgram LLM Models Docs](https://developers.deepgram.com/docs/voice-agent-llm-models), practical testing

## The Problem

Deepgram Voice Agent's `agent.think` endpoint MUST return responses in a **FLAT format**, NOT OpenAI's nested Chat Completions structure.

### ✅ Deepgram Expects (FLAT):
```json
{"type": "ConversationText", "role": "assistant", "content": "Your response here"}
```

### ❌ Mistral / OpenAI Return (NESTED — Deepgram IGNORES):
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "choices": [{
    "message": {"role": "assistant", "content": "Your response here"},
    "finish_reason": "stop",
    "index": 0
  }],
  "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
}
```

## Additional Requirements

1. **Streaming (SSE) is MANDATORY** — A plain JSON response won't work. Endpoint must:
   - Set `Content-Type: text/event-stream`
   - Stream `data: {...}\n\n` chunks
   - End with `data: [DONE]\n\n`
2. **No nested JSON** — `choices[0].message` wrapping causes Deepgram to silently ignore the response
3. **No metadata fields** — `id`, `object`, `created`, `usage`, `model` are not recognized and may cause issues

## Why Direct Mistral Fails

Mistral's API (`api.mistral.ai/v1/chat/completions`) returns OpenAI-compatible nested format. Even with `agent.think.provider.type: "open_ai"` and `endpoint.url` pointing to Mistral directly, Deepgram cannot extract the assistant response because it looks for flat format at the top level.

## The Proxy Pattern (Confirmed Working)

A local proxy between Deepgram and Mistral:
1. Receives Deepgram's OpenAI-format request (model: `gpt-4o-mini`, Deepgram-accepted name)
2. Rewrites `model` to `mistral-small`
3. Adds `Authorization: Bearer MISTRAL_API_KEY` header
4. Forwards to `https://api.mistral.ai/v1/chat/completions`
5. Extracts `choices[0].message.content` from nested response
6. Returns `{"type": "ConversationText", "role": "assistant", "content": "..."}`
7. Must stream as SSE

**Proxy location:** `/home/ubuntu/voice-agent-venv/mistral_proxy.py` (port 8766)

## Settings Config Validation Issues (Separate from format)

Deepgram also validates the Settings JSON before making any API calls:

| Error | Cause | Fix |
|-------|-------|-----|
| `UNPARSABLE_CLIENT_MESSAGE` | `temperature` at `think` level (not inside `provider`) | Move into `provider` object |
| `UNPARSABLE_CLIENT_MESSAGE` | Unknown model name (e.g., `mistral-small`) | Use Deepgram-recognized name (`gpt-4o-mini`) |
| `UNPARSABLE_CLIENT_MESSAGE` | Extra fields in `provider` (e.g., `max_tokens`) | Only `type`, `model`, `temperature` |

## Supported Provider Types

Deepgram supports these `agent.think.provider.type` values:
- `open_ai` — OpenAI Chat Completions format
- `anthropic`
- `google`
- `groq` (endpoint required)
- `nvidia`
- `aws_bedrock` (endpoint required)

**Source:** https://developers.deepgram.com/docs/voice-agent-llm-models

## Recommendation

If building a voice agent with custom LLM (Mistral), use **LiveKit Agents** instead of Deepgram Voice Agent:
- LiveKit has an official `mistralai` plugin — no format issues
- LiveKit has official `deepgram` plugins for STT and TTS
- No proxy needed, no flat format conversion, no Settings validation quirks

**Source:** https://docs.livekit.io/agents/models/llm/mistralai
