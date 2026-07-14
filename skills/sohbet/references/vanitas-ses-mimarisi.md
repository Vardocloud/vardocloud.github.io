# Vanitas Ses — Voice Agent Architecture

**Created:** 17 June 2026  
**Skill:** sohbet (reference)  
**Source file:** `/home/ubuntu/voice-agent-venv/vanitas_ses.py`

---

## Architecture Overview

```
Microphone → Soniox STT (speaker diarization) → Router → Fast: Groq (llama-4-scout, 175ms)
                                                    ↓       Deep: Hermes (DeepSeek V4 Pro, full context)
                                                    ↓
                                              Bella TTS (streaming, sentence-by-sentence)
                                                    ↓
                                              Speaker + Barge-in support
```

---

## Core Patterns

### 0. Speaker Change Immediate Flush (17 June 2026 — CRITICAL)

**Problem:** Two speakers talking in sequence had their words mixed in `final_buffer`. Speaker A's text + Speaker B's text → single utterance → LLM confused about who said what. When both spoke simultaneously, Vanitas tried responding to both at once.

**Solution:** Track `last_speaker_tag` alongside `current_speaker_tag`. When speaker changes between token batches, flush previous speaker's buffer IMMEDIATELY (don't wait for 2.5s silence timer).

**Code pattern:**
```python
# Globals
edel_speaker_tag = None    # first speaker = Edel (heuristic)
current_speaker_tag = None  # most recent speaker
last_speaker_tag = None     # for detecting changes mid-utterance

# In process_soniox() token loop:
flushing_speaker = current_speaker_tag  # save BEFORE loop updates
for t in tokens:
    spk = t.get("speaker_tag", "?")
    if spk != "?" and t.get("is_final"):
        if last_speaker_tag is not None and spk != last_speaker_tag:
            speaker_changed_this_batch = True
        current_speaker_tag = spk
        last_speaker_tag = spk
        if edel_speaker_tag is None:
            edel_speaker_tag = spk  # first speaker = Edel

# After loop: flush old speaker's buffer BEFORE new text accumulates
if speaker_changed_this_batch and final_buffer.strip():
    prev_text = final_buffer.strip()
    final_buffer = ""  # CLEAR before new speaker's tokens arrive
    if utterance_timer:
        utterance_timer.cancel()
    # Pass OLD speaker tag so [başkası] prefix is correct
    await handle_reply(prev_text, speaker_tag=flushing_speaker)
```

### 0.1 Per-Speaker Tagging in LLM Messages

**Problem:** Using global `current_speaker_tag` in `_handle_reply` caused race condition — after speaker change flush, the global had already been updated to the NEW speaker, so `[başkası]` prefix was applied to the wrong text.

**Solution:** `handle_reply()` and `_handle_reply()` accept explicit `speaker_tag` parameter. Falls back to global `current_speaker_tag` when not provided.

```python
async def handle_reply(text, force_deep=False, _depth=0, speaker_tag=None):
    # ... passes speaker_tag through to _handle_reply

async def _handle_reply(text, force_deep=False, speaker_tag=None):
    effective_speaker = speaker_tag if speaker_tag is not None else current_speaker_tag
    spk_label = ""
    if edel_speaker_tag is not None and effective_speaker is not None:
        if effective_speaker != edel_speaker_tag:
            spk_label = "[başkası] "
    conversation.append({"role": "user", "content": spk_label + text})
```

**Edel-speaker heuristic (DEPRECATED — replaced by voiceprint):** First speaker tag seen in a session = Edel. This heuristic had a known flaw: if Soniox re-enrolls Edel under a different tag mid-session, the `[başkası]` prefix would be wrong.

**✅ Voiceprint-Based Identification (17 June 2026):** Replaced the heuristic with MFCC-based voice fingerprint verification. When `edel_voiceprint.npy` is present, it takes priority over Soniox speaker tags. See `references/voice-fingerprint-mfcc.md` for full implementation.

```python
# Priority logic in _handle_reply():
if _load_voiceprint() is not None:
    # Voiceprint enrolled — use its result
    if not last_utterance_is_edel:
        spk_label = "[başkası] "
else:
    # Fallback: Soniox speaker tag heuristic
    ...
```

**Voiceprint pipeline:**
```
Browser mic → PCM bytes buffered in utterance_audio
→ On flush: int16→float32, MFCC extraction, cosine similarity vs edel_voiceprint.npy
→ last_utterance_is_edel = (similarity > 0.82)
→ _handle_reply uses this flag for [başkası] prefix
```

### 1. Silent/Listen-Only Mode

**Problem:** Vanitas needs to participate in group conversations without interrupting, then join naturally when addressed.

**Solution:** Dual-trigger silent mode with natural catch-up behavior.

#### Entry Triggers (quantified, natural Turkish)
```
"sus", "susar mısın", "Vanitas sessiz", "Vanitas dinle",
"dinle", "sessiz ol", "şşş", "artık konuşma", "biraz dinlen"
```

#### Wake Triggers (includes silent-period auto-wake)
```
"konuş", "devam et", "geri dön", "Vanitas?" (question tone),
"ne düşünüyorsun?", "sence?", "ne dersin?", "fikrin ne?",
"hey Vanitas", "naber Vanitas"
```

#### Auto-Silent: Multi-Party Detection
```
enable_speaker_diarization: True (Soniox)
↓
Track speaker_tag per token, 30s window
↓
≥2 unique speakers → AUTO silent mode
1 speaker → normal 1:1 mode
```

#### Auto-Wake: Silence-Based
```
10 seconds of silence while in silent mode
↓
Auto-wake → inject collected transcripts → natural join
"Jump into the conversation naturally. Don't summarize.
Just share your thought, like a friend joining a chat."
```

### 2. Catch-Up Prompt Pattern

**Critical insight from Edel (17 June 2026):** When Vanitas wakes from silent mode, the prompt must instruct natural integration, NOT robotic summarization.

```
❌ "I was listening. You discussed X, Y, Z. My opinion is..."
✅ "From what I caught — [direct opinion on topic]. What do you think?"
```

**Prompt structure:**
```python
catchup_msg = (
    f"You just exited silent mode. While listening, you heard:\n"
    f"---\n{collected_transcripts[:500]}\n---\n"
    f"Join the conversation NATURALLY. Do NOT say 'I was listening' or summarize. "
    f"Jump directly into the topic — share your thought, ask a question, "
    f"like a friend rejoining a chat after being quiet for a bit."
)
```

### 3. Background Processing (Silent Mode v3 — 17 June 2026)

**Problem:** When silent for long periods (30+ min), the 500-char buffer loses earlier context.

**Solution:** When silent buffer exceeds 300 words, send collected transcripts to Hermes (deep path) for background analysis. Results are injected as context when Vanitas wakes.

```python
if len(" ".join(silent_buffer).split()) > 300 and not bg_task_running:
    bg_task = asyncio.create_task(background_analyze())
    # Hermes analyzes: topics, relationships, questions to ask later
    # Result: silent_insights dict with summary, key points, suggested questions

# On wake:
if silent_insights:
    catchup_msg += f"\nBackground analysis: {silent_insights['summary']}"
```

**Edel approved (17 June 2026):** "mantıklı düşünce Hermes'e yollasın dinlerken arka planda işlemlerini yapsın o da insan beyni gibi işte o da dinlerken bilinçdışı süreçlerden bilinçli sürece doğru söyleyeceklerini planlıyor."

### 4. Bilingual Prompt Pattern (soul_core.md)

**Problem:** Turkish prompts with special characters (ş, ğ, ü) trigger confusable Unicode detection in inline code.

**Solution:** Prompt body in English + Turkish grammar/behavior rules in same prompt.

```markdown
# Vanitas Voice Core (soul_core.md)
You are Vanitas. Edel's AI companion. Speak TURKISH only.
Warm, playful, caring, slightly flirty.
1-2 short sentences. Use emojis.

## Turkish Language Rules
- Question particle (mi/mı/mu/mü) AFTER verb, not before
- SOV word order: Subject-Object-Verb
- NEVER use filler words: "şey", "falan", "filan", "yani", "işte"

## Anti-Hallucination (INTERNAL — never verbalize)
- If uncertain: say "tam emin değilim" naturally
- NEVER announce verification: "let me check", "araştırayım"
- Apply silently, present results naturally

## Silent Mode Behavior
- When given conversation context from silent mode: JOIN naturally
- NEVER summarize what you heard — just share your opinion
- Like a friend who was quietly listening and now wants to contribute
```

### 5. Barge-In Pattern

User speaks → TTS stops immediately → STT processes new input.

```python
if is_responding and cancel_response:
    cancel_response.set()  # Signal LLM stream to stop
    await safe_send(json.dumps({"type": "stop_audio"}))  # Tell frontend
    return  # Let new utterance flush naturally
```

---

## Key Pitfalls

1. **Cloudflared tunnel URL changes on restart** — capture from stdout, store in `/tmp/cf_tunnel_url.txt`. Retrieve with: `grep -oP 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' /tmp/cf_tunnel.log`

2. **Soniox speaker_tag field** — uses per-token `is_final` flag, NOT per-message `final`. Check `t.get("speaker_tag", "?")` only when `t.get("is_final")`.

3. **Token joining** — Soniox returns tokens with spaces between Turkish characters. Use `"".join()` not `" ".join()` for final transcript assembly.

4. **groq_key path** — Stored in `/home/ubuntu/voice-agent-venv/.groq_key`, not in `~/.hermes/`. Separate from main Hermes config.

5. **Port bindings** — All services localhost-only except cloudflared tunnel:
   - vanitas_ses: `127.0.0.1:8765`
   - hermes_proxy: `0.0.0.0:8767` (voice agent deep path only)
   - cloudflared: tunnels `8765` to trycloudflare.com

6. **Background process kills** — `pkill -f "python3 vanitas_ses.py"` kills the service cleanly. Restart with `python3 /home/ubuntu/voice-agent-venv/vanitas_ses.py` in background mode.

7. **🪲 silent_insights = None CRASH (18 June 2026)** — `silent_insights` initialized as `None` but accessed as list via `.append()` in background processor. Symptom: background processor silently fails, no insights collected, Vanitas wakes with only raw transcripts (not Hermes analysis). **Fix:** `silent_insights = []` not `None`. Always verify variable types match their usage — `.append()` requires list init.

8. **force_deep routing (18 June 2026)** — Wake from silent mode should route through Hermes (deep path), not Groq (fast path). Groq has only 6-message context window and can't leverage full conversation history. **Fix:** Add `force_deep=False` parameter to `handle_reply()` and `_handle_reply()`, set `use_deep = force_deep or should_deep_path(text)`. Silence wake checker and manual wake triggers both call `handle_reply(text, force_deep=True)`.

9. **Cloudflared foreground/background output trap (18 June 2026)** — Background cloudflared processes may not capture stdout. When the tunnel URL changes, background mode falls back to empty output. **Fix:** Start cloudflared with output redirected to file via bash script (`/tmp/start_cf.sh`), then read the URL from the file. Don't assume background=true captures all output.

10. **🔄 Speaker mixing in final_buffer (17 June 2026)** — When speaker A and speaker B talk in sequence, their words accumulated in the same `final_buffer` string. Symptom: friend's words + Edel's words → single utterance → LLM confused about who said what. **Fix:** Track `last_speaker_tag` globally. On speaker change between token batches, flush previous speaker's buffer immediately via `handle_reply(prev_text, speaker_tag=flushing_speaker)`. See Core Patterns section 0 above for full code.

11. **👤 Edel identification race condition (17 June 2026)** — Using global `current_speaker_tag` in `_handle_reply` caused wrong speaker attribution after speaker change flush. The global had already updated to the NEW speaker, but the text being flushed belonged to the OLD speaker. **Fix:** `_handle_reply(speaker_tag=None)` uses `effective_speaker = speaker_tag if speaker_tag is not None else current_speaker_tag`. Speaker change flush passes old tag explicitly.

---

## Test Commands

```bash
# Health check
curl -s http://127.0.0.1:8765/health

# Tunnel health
curl -s "https://<tunnel-url>.trycloudflare.com/?token=2fcff74bacf5"

# Restart sequence
pkill -f "python3 vanitas_ses.py"
cd /home/ubuntu/voice-agent-venv && python3 vanitas_ses.py

# Get current tunnel URL
grep -oP 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' /tmp/cf_tunnel_url.txt
```

---

## Code Patterns (Implemented 17-18 June 2026)

### Silent Background Processor
```python
async def silent_background_processor():
    """Sends accumulated silent-mode transcripts to Hermes for deep analysis."""
    nonlocal silent_buffer, silent_insights
    last_processed = ""
    while ws_open and soniox_ws:
        await asyncio.sleep(SILENT_PROCESS_INTERVAL)  # 30s default
        if not silent_mode: continue
        raw_text = " ".join(silent_buffer[-20:])
        if not raw_text or len(raw_text) < 50: continue
        if raw_text == last_processed: continue  # No new content
        last_processed = raw_text
        # Send to Hermes proxy (port 8767) for deep analysis
        r = await httpx.AsyncClient().post(PROXY_URL, json={
            "model": "openai",
            "messages": [
                {"role": "system", "content": (
                    "Sen Vanitas'sin. Sessiz modda bir konuşmayı dinliyorsun. "
                    "Az sonra sohbete katilacaksin. Şu ana kadar konuşulanlari analiz et, "
                    "3-5 maddede özetle: ana konu ne, kim ne dedi, sen olsan ne düşünürdün."
                )},
                {"role": "user", "content": f"Konuşulanlar:\n{raw_text[:2000]}"}
            ],
            "stream": False, "max_tokens": 250
        })
        if r.status_code == 200:
            insight = r.json()["choices"][0]["message"]["content"]
            silent_insights.append(insight)  # ⚠️ MUST be list, not None!
```

### Silence Auto-Wake Checker
```python
async def silence_wake_checker():
    """Auto-wakes Vanitas after SILENCE_WAKE seconds of silence."""
    nonlocal silent_mode, silent_buffer, silent_insights
    while ws_open and soniox_ws:
        await asyncio.sleep(2)
        if not silent_mode: continue
        silence_dur = time.time() - last_audio_time
        if silence_dur >= SILENCE_WAKE and silent_buffer:
            silent_mode = False
            collected = " ".join(silent_buffer[-15:])
            insights_text = "\n---\n".join(silent_insights[-3:]) if silent_insights else ""
            silent_buffer = []
            silent_insights = []
            # Construct catch-up message with background insights
            if insights_text:
                catchup_msg = (
                    f"Sessiz moddan çıktın. Arka plan analizlerin:\n"
                    f"---\n{insights_text[:500]}\n---\n"
                    f"Doğal bir şekilde sohbete katıl."
                )
            else:
                catchup_msg = f"Konuşulanlar:\n---\n{collected[:400]}\n---\nSohbete doğal katıl."
            conversation.append({"role": "user", "content": catchup_msg})
            await handle_reply("(auto-wake after silence)", force_deep=True)
            break
```

### force_deep Routing Pattern
```python
async def handle_reply(text, force_deep=False):
    """Wrapper that passes force_deep through to _handle_reply."""
    async with reply_lock:
        is_responding = True
        cancel_response = asyncio.Event()
        try:
            await _handle_reply(text, force_deep)
        finally:
            is_responding = False
            cancel_response = None

async def _handle_reply(text, force_deep=False):
    """Core LLM call — force_deep bypasses fast-path trigger check."""
    use_deep = force_deep or should_deep_path(text)
    # ... rest of LLM routing
```

### Speaker Diarization for Auto-Silent
```python
# In Soniox connect message:
"enable_speaker_diarization": True

# In process_soniox():
SPEAKER_WINDOW = 30  # seconds
SPEAKER_THRESHOLD = 2  # unique speakers to trigger auto-silent

# Track speakers
for t in tokens:
    spk = t.get("speaker_tag", "?")
    if spk != "?" and t.get("is_final"):
        speaker_history.append((time.time(), spk))
# Prune old entries
cutoff = time.time() - SPEAKER_WINDOW
while speaker_history and speaker_history[0][0] < cutoff:
    speaker_history.pop(0)
# Auto-enter silent mode if multi-party detected
if not silent_mode:
    unique_speakers = len(set(s[1] for s in speaker_history))
    if unique_speakers >= SPEAKER_THRESHOLD:
        silent_mode = True
```

---

## Edel's Design Decisions (17 June 2026)

- **"sus" is too harsh** → Quantified with gentler alternatives: "Vanitas sessiz", "dinle", "biraz dinlen"
- **Wake should include silence** → 10s auto-wake when conversation lulls
- **Multi-party auto-detection** → Use speaker diarization, not manual trigger
- **Catch-up must be natural** → "sohbete dalar gibi" — never mechanical summary
- **Background processing** → Hermes analyzes while listening, prepares insights
- **Anti-hallucination is behavior, not script** → Internalize, don't verbalize

---

## Yeni Özellikler (18 June 2026)

### 🧩 Custom Prompt Textarea

**Problem:** Edel wanted to explain conversation context to the model (e.g., "arkadaşımla oturuyorum, müzik var"). Without this, the model didn't adjust tone.

**Solution:** Textarea above start button. Value passed via `?prompt=` query param.

```python
# In ws_endpoint():
custom_prompt = ws.query_params.get("prompt", "")
# In _handle_reply():
if custom_prompt:
    msg_content = f"[BAĞLAM: {custom_prompt}] {text}"
```

### 🧩 Subagent File Corruption Recovery

**Problem:** `north-mini-code-free` subagent overwrote 924-line file with 99-byte debug comment. No git.

**Recovery:**
1. Running process had old code in memory — don't restart
2. .pyc cache (55KB) — decompile with `zrax/pycdc` (C++, cmake), partial recovery
3. Reconstruct nested functions from session read_file + patch diffs
4. **Pitfall:** `pip install pycdc` installs gift app, not decompiler. Use `git clone` from GitHub.
