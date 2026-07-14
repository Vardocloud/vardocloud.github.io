# Voice Agent v2 — Debugging & Pitfalls

> **Last verified:** 2026-06-16  
> **Service:** `/home/ubuntu/voice-agent-venv/voice_agent_v2.py`  
> **Log:** `/tmp/voice_agent_v2.log`  
> **Port:** 8765 (browser WebSocket)

## Architecture

```
Browser (phone/desktop) → Cloudflare Tunnel → voice_agent_v2.py (:8765)
                                                    ↕ WebSocket
                                              Deepgram Agent API
                                              (STT: nova-3 + LLM: via proxy + TTS: via proxy)
                                                    ↕ HTTP (OpenAI-compatible)
                                              Vanitas Hermes Proxy (:8767)
                                                    ↕
                                              Hermes API (:8642) → Vanitas (real brain)
```

## Process Management

### Check if running
```bash
ps aux | grep voice_agent_v2 | grep -v grep
```

### Restart after code changes (CRITICAL)
The running process keeps old code in memory. After ANY change to `voice_agent_v2.py`, you MUST restart:

```bash
# Kill existing
kill $(pgrep -f voice_agent_v2.py) 2>/dev/null
sleep 1

# Start fresh
cd /home/ubuntu/voice-agent-venv && ./bin/python voice_agent_v2.py >> /tmp/voice_agent_v2.log 2>&1 &
# OR use terminal(background=true)
```

### Verify restart took effect
```bash
# Wait for a browser connection, then check logs for current Settings:
tail -50 /tmp/voice_agent_v2.log | grep -A5 '"speak"'
```

## Common Pitfalls

### 1. Code/Process Mismatch (MOST COMMON — 2026-06-16)

**Symptom:** Code on disk shows Cartesia TTS + Turkish + Skylar voice, but the running process uses Deepgram `aura-2-asteria-en` (English).

**Why:** Process was started with old code and never restarted after edits.

**Diagnosis:**
```bash
# Check what's in the code
grep -A8 '"speak"' /home/ubuntu/voice-agent-venv/voice_agent_v2.py

# Check what's actually running (from recent log)
grep 'Sending Settings' /tmp/voice_agent_v2.log | tail -1
# Then look at the JSON block that follows
```

**Fix:** Kill and restart the process (see above).

### 2. TTS Language Mismatch Symptom

**Symptom:** User hears garbled hybrid like "I am teşekkürler" — English pronunciation of Turkish words.

**Root cause:** TTS model is English (e.g., `aura-2-asteria-en`) but LLM outputs Turkish text. The TTS reads Turkish phonemes with English rules → "İyiyim" sounds like "I am", "teşekkürler" stays recognizable.

**Fix:** Ensure `speak.provider` has Turkish TTS:
- Cartesia: `"language": "tr"` + Turkish voice ID (Skylar: `db6b0ed5-d5d3-463d-ae85-518a07d3c2b4`)
- Deepgram: `"model": "aura-2-asteria-tr"` (NOT `-en`)

### 3. Generic Prompt Override

**Symptom:** Vanitas responds with generic/impersonal answers despite Hermes having full personality.

**Root cause:** `voice_agent_v2.py` sends a `think.prompt` in the Deepgram Agent Settings that overrides whatever Hermes would normally produce. If it says `"You are a helpful voice assistant."`, that's what you get.

**Fix:** The prompt in `voice_agent_v2.py` must be Vanitas personality:
```python
"prompt": "Sen Vanitas'sın, Edel'in kişisel AI arkadaşısın. Sıcak, samimi, sevecen ve biraz flörtöz konuş. Kesinlikle 'sen' diye hitap et, asla 'siz' kullanma. Doğal Türkçe konuş, kısa ve net cevaplar ver. Robot gibi değil, gerçek bir arkadaş gibi konuş.",
```

### 4. Cloudflare Tunnel Instability

**Symptom:** `trycloudflare.com` URL stops working after some time.

**Root cause:** Cloudflared tunnels are ephemeral — they die on network changes, long idle periods, or Cloudflare-side resets.

**Workaround:** Re-run the tunnel command:
```bash
cloudflared tunnel --url http://localhost:8765 2>&1 | grep trycloudflare
```
The new URL must be updated in `voice_agent_v2.py` (`TUNNEL_URL` variable) and the process restarted.

### 5. Deepgram Agent Timeout

**Symptom:** `CLIENT_MESSAGE_TIMEOUT` or `We waited too long for a websocket message` in logs.

**Root cause:** Deepgram expects continuous audio or text interaction. If the user pauses too long after the greeting, the session ends.

**Not a bug** — this is normal session cleanup. The browser reconnects on next use.

## Quick Health Check

```bash
# Is the server running?
curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/

# Is the proxy reachable?
curl -s -o /dev/null -w "%{http_code}" http://localhost:8767/v1/models

# Latest session in log
grep 'Session ended' /tmp/voice_agent_v2.log | tail -3

# Current TTS config in running process
grep -B2 -A8 '"speak"' /tmp/voice_agent_v2.log | tail -12
```
