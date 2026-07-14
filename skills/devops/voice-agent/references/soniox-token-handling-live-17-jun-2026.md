# Soniox Token Handling — Live Debug Log (17 June 2026)

## Issue: Turkish Subword Tokens

Soniox uses subword tokenization for Turkish. Tokens arrive like:
```
["Mer", "hab", "a"]  → should become "Merhaba"
```

### Wrong: Space Join
```python
❌ " ".join(tokens) → "Mer hab a" (harfler ayrı, okunaksız)
```

### Right: Direct Concatenation
```python
✅ "".join(tokens) → "Merhaba"
```

## Issue: Cumulative Final Buffer

Final tokens are cumulative — each message includes ALL previously finalized tokens plus new ones:
```
Message 1: tokens=[{"text":"Mer","is_final":true}]
Message 2: tokens=[{"text":"Mer","is_final":true}, {"text":"haba","is_final":true}]
```

### Wrong: Append Every Time
```python
❌ utterance_queue.append("".join(final_tokens))  # "Mer" then "Merhaba" → duplicate!
```

### Right: Deduplicate
```python
final_buffer = ""
new_text = "".join(t["text"] for t in final_tokens)
if new_text and not final_buffer.endswith(new_text):
    final_buffer += new_text  # Only add new part
```

## Issue: is_final Location

The `is_final` flag is on each TOKEN, not on the message:
```json
{
  "tokens": [
    {"text": "Mer", "is_final": true},
    {"text": "haba", "is_final": false}
  ]
}
```

### Wrong: Message-Level Check
```python
❌ is_final = msg.get("final", False)  # Never True — field doesn't exist
```

### Right: Per-Token Check
```python
✅ final_tokens = [t for t in tokens if t.get("is_final")]
```

## Issue: Empty Token Messages

Soniox sometimes sends messages with empty `tokens` array. Always check:
```python
tokens = msg.get("tokens", [])
if not tokens:
    continue  # Skip empty messages
```

## Debug: Raw Soniox Messages

First few messages from a live session (Turkish, 16kHz PCM):
```
msg#1: {"tokens":[], "final_audio_proc_ms":0, "total_audio_proc_ms":0}
msg#2: {"tokens":[{"text":"M","is_final":false}], "total_audio_proc_ms":250}
msg#3: {"tokens":[{"text":"Mer","is_final":true},{"text":"hab","is_final":false}], ...}
```

Key observations:
- Message 1 is always empty (connection confirmation)
- Non-final tokens appear first as guesses
- Final tokens accumulate over messages
- Spaces between words are their own tokens: `{"text":" ", "is_final":true}`
