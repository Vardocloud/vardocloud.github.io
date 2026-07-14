# Echo Loop Prevention (v6 Web Speech API)

## The Problem
STT (Chrome Web Speech API) captures Vanitas's **own TTS output** from the speakers → transcribes it → sends back as user utterance → infinite loop.

### Observed Symptoms (2026-06-16)
```
Proxy log: 2 msgs → 3 msgs → 5 msgs → 7 msgs (escalating)
Assistant: "Selam! Ben iyiyim, sen nasılsın?"
STT captured: "Selam" → sent as new utterance → "Selam! Ben..." again → "Selam" again → 🔁
```

## Root Cause: 3 Interacting Failures

### 1. `recognition.stop()` is async
`stop()` waits for pending results to complete before actually stopping. During that window, TTS audio plays → captured → queued `onresult` fires → echo.

### 2. `onend` auto-restart without pause check
After `abort()` or `stop()`, `onend` fires and immediately calls `recognition.start()` again — even during TTS playback.

### 3. Echo guard too strict (single direction)
Original guard: `cleaned.includes(lastAssistantText.substring(0, 20))`
- "selam" vs "selam! ben iyiyim, sen" → FAILS (short string can't contain long substring)

## 5-Layer Fix (Applied to voice_agent_v6.py)

| Layer | Location | Change | Why |
|-------|----------|--------|-----|
| 1 | `agent_speaking` handler | `recognition.stop()` → `recognition.abort()` | `abort()` is synchronous — stops immediately |
| 2 | `onresult` callback | `if (recognitionPaused) return;` at top | Blocks any queued results during TTS |
| 3 | `onend` handler | Add `!recognitionPaused` guard | Prevents auto-restart after abort during TTS |
| 4 | `onerror` handler | Add `!recognitionPaused` to `no-speech` restart | Prevents restart during TTS |
| 5 | `onresult` echo guard | 3-layer matching (see below) | Catches any echo that slips through |

### Layer 5: Multi-Layer Echo Guard Algorithm

```javascript
// Layer 1: Recognized text IS a substring of assistant's reply
if (lastLower.includes(cleaned)) → BLOCK

// Layer 2: Assistant's reply STARTS WITH recognized text
if (lastLower.startsWith(cleaned)) → BLOCK

// Layer 3: Word overlap > 50%
const asstWords = new Set(lastLower.split(/\s+/));
const userWords = cleaned.split(/\s+/).filter(w => w.length > 1);
const overlap = userWords.filter(w => asstWords.has(w)).length / userWords.length;
if (overlap > 0.5) → BLOCK
```

This catches:
- "selam" matched against "selam! ben iyiyim..." → Layer 2 ✅
- "ben iyiyim" matched against "selam! ben iyiyim..." → Layer 1 ✅
- "selam nasılsın" vs "selam! ben iyiyim, sen nasılsın?" → Layer 3 (67% overlap) ✅

### Supporting Changes

**Debounce (800ms):**
```javascript
if (isProcessing || (now - lastUtteranceTime < 800)) → skip
```
Prevents `continuous: true` mode from sending multiple final results for one speech segment.

**`isProcessing` lock:**
```javascript
isProcessing = true;  // on utterance send
isProcessing = false; // on transcript received OR error
```

**Cooldown increase:** 500ms → 1500ms after TTS audio received before restarting recognition.

## Web Speech API Pitfalls (General)

| Pitfall | Detail | Fix |
|---------|--------|-----|
| `stop()` is async | Results may fire after call | Use `abort()` for immediate stop |
| `onend` after abort | Fires immediately, auto-restart | Guard with pause flag |
| `continuous: true` | Multiple finals per utterance | Debounce with `isProcessing` + timestamp |
| `no-speech` after abort | `abort()` may trigger `no-speech` error | Guard error handler with pause flag |
| TTS plays through speakers | Mic captures it as speech | Mute mic during playback + echo guard |

## Testing the Fix

```bash
# Check v6 is running
ss -tlnp | grep 8765

# Simulate echo scenario via WebSocket
python3 -c "
import asyncio, json, websockets
async def test():
    async with websockets.connect('ws://127.0.0.1:8765/ws?token=TOKEN') as ws:
        await ws.send(json.dumps({'type':'utterance','text':'Selam ne haber'}))
        for _ in range(5):
            reply = await asyncio.wait_for(ws.recv(), timeout=30)
            print(json.loads(reply).get('type','?'))
        await ws.send(json.dumps({'type':'stop'}))
asyncio.run(test())
"
```

Expected: One `text` response, one `audio` response. No loop.
When echo occurs: Proxy log shows escalating message counts (2→3→5→7...).
