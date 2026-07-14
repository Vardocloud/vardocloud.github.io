# OpenRouter Free Models — Live Status & Model Proxy Pattern

## Live Model Availability (June 2026)
Tested via `POST https://openrouter.ai/api/v1/chat/completions` with `/tmp/.or_key`:

| Model | Status | Notes |
|-------|--------|-------|
| `nvidia/nemotron-3-super-120b-a12b:free` | ✅ Working | 1M ctx, agentic MoE. Only reliable free model for voice. |
| `google/gemma-4-31b-it:free` | ⚠️ Rate-limited | Was working, now returns 429 upstream rate-limit |
| `qwen/qwen3-next-80b-a3b-instruct:free` | ❌ Provider error | Returns errors on free tier |
| `meta-llama/llama-3.3-70b-instruct:free` | ❌ Provider error | Returns errors on free tier |
| `openai/gpt-oss-120b:free` | ❌ Untested | May work, test before using |

**Key insight:** Free model availability fluctuates rapidly. Always test live before deploying. The check command:
```bash
curl -s -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $(cat /tmp/.or_key)" \
  -H "Content-Type: application/json" \
  -d '{"model":"MODEL:free","messages":[{"role":"user","content":"say OK"}],"max_tokens":5}'
```

## The Model Proxy Pattern

**Problem:** Deepgram Voice Agent's `open_ai` provider validates model names. Only recognizes OpenAI models (gpt-4o-mini, gpt-5-nano, etc.). OpenRouter free model IDs like `google/gemma-4-31b-it:free` are REJECTED with `UNPARSABLE_CLIENT_MESSAGE`.

**Solution:** A local HTTPS proxy that:
1. Accepts requests from Deepgram (model="gpt-4o-mini")
2. Rewrites model to a free model ID
3. Forwards to OpenRouter
4. Streams response back

**Architecture:**
```
Deepgram → cloudflared HTTPS → local proxy (8767) → OpenRouter
         (model: gpt-4o-mini)    (model → nemotron:free)   (free model)
```

**Proxy implementation:** `/home/ubuntu/voice-agent-venv/model_proxy.py`
- Uvicorn on port 8767
- `POST /v1/chat/completions` → rewrites model → forwards to OpenRouter
- `GET /health` for health checks
- Static `TARGET_MODEL` configurable at top of file

**Startup:**
```bash
cd /home/ubuntu/voice-agent-venv && ./bin/python model_proxy.py &
/usr/local/bin/cloudflared tunnel --url http://127.0.0.1:8767 > /tmp/cf_proxy_url.txt 2>&1 &
# Extract URL: cat /tmp/cf_proxy_url.txt | grep trycloudflare
```

**Deepgram Settings with proxy:**
```json
"think": {
  "provider": {"type": "open_ai", "model": "gpt-4o-mini", "temperature": 0.8},
  "endpoint": {
    "url": "https://xxx.trycloudflare.com/v1/chat/completions",
    "headers": {"Content-Type": "application/json", "Authorization": "Bearer OR_KEY"}
  },
  "prompt": "You are Vanitas..."
}
```

**Cloudflared dependency:** Multiple tunnels may need management. Kill old ones with `pkill -f "cloudflared.*8767"`.

## Pitfalls
- Proxy needs `aiohttp` (`pip install aiohttp`) — not in default venv
- Cloudflared tunnels die on server restart — recreate after reboot
- Deepgram's validation checks model BEFORE sending to endpoint — proxy can't help with validation, only routing
- `use_openrouter` flag in voice_agent_v2.py must be `True` to use proxy endpoint
