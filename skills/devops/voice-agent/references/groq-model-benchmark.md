# Groq Model Benchmark — Voice Agent (June 2026)

## Test Setup
- API: `https://api.groq.com/openai/v1/chat/completions`
- Prompt: 300B system + "Nasilsin bugun?" user
- Mode: streaming (first token) + non-streaming (total)

## Results

| Model | First Token (stream) | Total (non-stream) | Turkish Quality | Verdict |
|-------|---------------------|-------------------|-----------------|---------|
| **llama-3.3-70b-versatile** | **112ms** | 216ms | Good ("İyiyim, teşekkür ederim.") | ✅ PRIMARY |
| meta-llama/llama-4-scout-17b-16e-instruct | 151ms | 753ms | Medium | ⚠️ Fallback |
| llama-3.1-8b-instant | 202ms | 202ms | Weak (lowercase, cutoff) | ❌ Not for voice |

## Surprising Finding

llama-3.3-70b (70B params) is FASTER than llama-4-scout (17B params):
- First token: 112ms vs 151ms
- Total: 216ms vs 753ms
- Quality: Better Turkish morphology

Groq's LPU architecture favors the 70B model for unknown reasons (possibly better batching/throughput).

## Model Name Format (Critical)

Groq requires fully-qualified model IDs:
```python
✅ "meta-llama/llama-4-scout-17b-16e-instruct"
✅ "llama-3.3-70b-versatile"
✅ "llama-3.1-8b-instant"
❌ "llama-4-scout-17b-16e-instruct"      # 404
❌ "llama4-scout-17b-16e-instruct"       # 404
❌ "mixtral-8x7b-32768"                  # 400 (deprecated)
```

## API Key

Stored in Bitwarden as `GROQ_API_KEY` → extracted to `voice-agent-venv/.groq_key` (chmod 600).
Free tier: ~30 req/min, 14K RPM token limit. More than sufficient for single-user voice.

## Compared Alternatives (Rejected)

| Alternative | First Token | Why Rejected |
|-------------|-------------|--------------|
| OpenCode Go deepseek-v4-flash | 9580ms | Proxy overhead too high |
| Pollinations gemma | 1500ms | Proxy overhead, few models |
| DeepSeek API direct | 618ms (empty) | Response format mismatch |
