# Voice Agent v8: Echo Prevention & STT Reliability

## Architecture (v8 Final)
```
Browser STT (Web Speech API) → v6 :8765 → Proxy :8767 → Hermes :8642 → Vanitas
```
The proxy handles auth server-side. v6 must route through proxy, never direct to Hermes.

## v8 Key Decision: `continuous: false`

`continuous: true` caused multiple problems:
- Multiple `onresult` finals per utterance → duplicate messages
- Abort/restart cycles confused the API
- Turkish STT noticeably less reliable
- `no-speech` errors during TTS abort → restart loops

Switching to `continuous: false` fixed all of these:
- One utterance, one `onresult`, auto-stop
- Clean lifecycle, no abort needed
- Better Turkish recognition quality
- Manual restart after TTS + cooldown

## Echo Prevention: 5 Layers (v8)

| # | Layer | Mechanism |
|---|-------|-----------|
| 1 | `continuous: false` | Auto-stop after speech, no abort chaos |
| 2 | `recognitionPaused` on send | Paused immediately when utterance sent |
| 3 | `onend` pause guard | `if (!recognitionPaused)` before restart |
| 4 | `onerror` pause guard | `no-speech` and `aborted` respect pause |
| 5 | 3-layer echo matching | Substring, prefix, word overlap >50% |

## Guard Ordering: ALL Before DOM

```javascript
// CORRECT ORDER (v8):
if (final) {
    // 1. Debounce FIRST (800ms)
    if (isProcessing || (now - lastUtteranceTime < 800)) return;
    
    // 2. Echo guard SECOND (3 layers)
    if (lastAssistantText) {
        const lastLower = lastAssistantText.toLowerCase();
        if (lastLower.includes(cleaned)) return;      // substring
        if (lastLower.startsWith(cleaned)) return;     // prefix
        // word overlap > 50%
        const asstWords = new Set(lastLower.split(/\s+/));
        const userWords = cleaned.split(/\s+/).filter(w => w.length > 1);
        if (userWords.filter(w => asstWords.has(w)).length / userWords.length > 0.5) return;
    }
    
    // 3. THEN update DOM and send
    recognitionPaused = true;
    addMessage('user', final);
    ws.send(JSON.stringify({type:'utterance', text:final}));
}
```

**Critical bug fixed (v7→v8):** Previously `addMessage('user', final)` ran BEFORE the debounce check, so duplicate `onresult` calls created duplicate visual messages ("kendi kendini kopyaladı").

## Lifecycle (v8)

```
User speaks → onresult final → recognitionPaused=true → send utterance
  → recognition auto-stops → onend (paused, no restart)
  → server responds → transcript → isProcessing=false
  → agent_speaking → TTS plays → audio received
  → setTimeout 1500ms → recognitionPaused=false → recognition.start()
```

## Timing Fix: Pause on Send, Not on Response

```
BEFORE (v6-v7): Wait for agent_speaking → then recognitionPaused=true
                 Race: onend fires before agent_speaking arrives

NOW (v8):       recognitionPaused=true immediately when utterance sent
                 onend fires → paused → no restart. Clean.
```

## Web Speech API Pitfalls

| Pitfall | Fix |
|---------|-----|
| `continuous: true` instability | Use `continuous: false` |
| `stop()` async, results fire after | Not needed with `continuous: false` |
| `onend` auto-restart during TTS | Guard with `recognitionPaused` flag |
| `no-speech` after TTS silence | Guard with `recognitionPaused` flag |
| TTS captured by mic | Echo guard + pause during TTS |
| Debounce after DOM update | Guards BEFORE `addMessage()` |
| Direct Hermes call → 401 | Route through auth-enabled proxy |
| WebSocket close during TTS | "Cannot call send once close sent" → check state |

## 401 Error Pattern

Symptom: Every utterance logs `❌ Hermes 401` in v6 logs.
Root cause: v6 calls Hermes :8642 directly without auth.
Fix: Change `HERMES_URL` to `PROXY_URL` — proxy has auth, v6 doesn't need it.

## Testing

```bash
# Verify both services
ss -tlnp | grep -E '8765|8767'

# Health checks
curl -s http://127.0.0.1:8767/health
curl -s http://127.0.0.1:8765/health

# WebSocket test (v6 uses 'utterance' type, not 'text')
python3 -c "
import asyncio, json, websockets
async def test():
    async with websockets.connect('ws://127.0.0.1:8765/ws?token=TOKEN') as ws:
        await ws.send(json.dumps({'type':'utterance','text':'Merhaba'}))
        for _ in range(5):
            reply = await asyncio.wait_for(ws.recv(), timeout=30)
            data = json.loads(reply)
            print(data.get('type','?'), ':', str(data.get('text',''))[:80])
        await ws.send(json.dumps({'type':'stop'}))
asyncio.run(test())
"
```

## Version Log (This Session)

| Version | Change | Result |
|---------|--------|--------|
| v6 (start) | Web Speech API, Hermes direct | 401 + echo loop |
| v6.1 | Proxy routing | 401 fixed, echo remains |
| v6.2 | 5-layer guard + abort() | Echo reduced, still occasional |
| v7 | Debounce before DOM | Duplicate messages fixed, STT unreliable |
| v8 | `continuous: false` + pause on send | Clean lifecycle, reliable STT |
