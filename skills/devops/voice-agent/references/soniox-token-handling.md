# Soniox Token Handling — Pitfalls & Correct Patterns

## Token Format (v2 API)

Soniox real-time API returns per-token `is_final`, NOT per-message:

```json
{
  "tokens": [
    {"text": "Mer", "is_final": true},
    {"text": " ", "is_final": true},
    {"text": "hab", "is_final": false},
    {"text": "a", "is_final": false}
  ],
  "final_audio_proc_ms": 4800,
  "total_audio_proc_ms": 5250
}
```

## Critical Mistakes

### 1. Message-level `final` check (DOES NOT WORK)
```python
# ❌ NEVER: there is no "final" field on the message
is_final = msg.get("final", False)  # Always False → no transcripts
```

### 2. Space-join on subword tokens (PRODUCES GIBBERISH)
```python
# ❌ " ".join() produces "Mer  hab a" for Turkish
transcript = " ".join(t["text"] for t in tokens)
```

### 3. Array-based utterance queue (DUPLICATES)
```python
# ❌ Array append creates clones — "Merhaba" appears twice
utterance_queue.append(transcript)
```

## Correct Patterns

### 1. Per-token is_final check
```python
final_tokens = [t for t in tokens if t.get("is_final")]
nonfinal_tokens = [t for t in tokens if not t.get("is_final")]
```

### 2. Direct concatenation (no spaces)
```python
# ✅ "".join() — subword tokens already contain space tokens
transcript = "".join(t["text"] for t in final_tokens)
```

### 3. Cumulative string buffer with deduplication
```python
final_buffer = ""  # Cumulative, NOT an array

new_text = "".join(t["text"] for t in final_tokens)
# Only append NEW text — Soniox may resend previous final tokens
if new_text and not final_buffer.endswith(new_text):
    final_buffer += new_text

transcript = final_buffer.strip()
```

### 4. Interim display
```python
if nonfinal_tokens:
    interim = "".join(t["text"] for t in nonfinal_tokens).strip()
    if interim:
        await safe_send({"type": "interim", "text": interim})
```

## Why This Matters for Turkish

Soniox uses subword tokenization. Turkish is an agglutinative language:
- "Merhaba" → ["Mer", "haba"] or ["Mer", "hab", "a"]
- "Nasılsın" → ["Nas", "ıl", "sın"]
- "geliyorum" → ["gel", "iyor", "um"]

Space tokens (" ") are separate tokens with `is_final: true`. Direct concatenation naturally produces correct text because space tokens provide the word boundaries.

## Silence Timing

`delayed_flush(2.5)` seconds — Turkish speakers take ~2-3 seconds between thoughts. 0.8s is too short and interrupts mid-sentence.
