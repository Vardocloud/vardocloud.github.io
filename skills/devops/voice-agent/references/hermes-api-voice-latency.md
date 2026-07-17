# Hermes API Voice Latency Test Results

## Test Setup
- Model: deepseek-v4-pro
- Context: ~56K tokens (full Vanitas SOUL.md + skills + memory)
- `tool_choice: "none"` — no effect, tools still load
- Endpoint: `http://127.0.0.1:8642/v1/chat/completions`

## Results

| Test | Stream | Latency | Content | Notes |
|---|---|---|---|---|
| "Who are you" | true | 6.7s | Turkish, tool events present | `data:` lines contain tool events |
| "Hi" | true | 7.8s | Turkish with emojis | Filtered tools, still slow |
| "Kimsin" | true | 6.2s | Turkish | Tool events filtered OK |
| "Say hi in 3 words" | false | 6.8s | Empty | Model proxy SSE parse bug |

## Root Cause

Hermes API loads the full agent context (system prompt, skills, memory, etc.) for every request. This produces significant first-token latency. `tool_choice: "none"` is documented but doesn't prevent tool loading in practice.

## Deepgram Voice Agent Timeout

Deepgram Voice Agent's think step has a ~5 second timeout for streaming responses. Hermes API's 6-9 second latency consistently exceeds this.

## Failed Workarounds

1. `tool_choice: "none"` — tools still load
2. `max_tokens: 10` — doesn't reduce context processing time
3. Non-streaming mode — same latency, Deepgram also times out with `CLIENT_MESSAGE_TIMEOUT`
4. Filtering tool events from SSE — works but latency still too high

## Conclusion

Hermes API is architecturally unsuitable for real-time voice at current context sizes (>50K tokens). For voice, use direct provider APIs (OpenRouter free models, etc.) with condensed system prompts.
