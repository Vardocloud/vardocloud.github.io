# Interim Transcript Display — "Anında Yazmıyor" Fix

## Problem (Discovered 2026-06-16)

User reported: "her söylediğimi anında yazmıyor" (not writing everything I say instantly).

## Root Cause

v10.4-v10.6 code only processed `is_final=True` Deepgram results. **Interim results were completely ignored:**

```python
# ❌ v10.4-v10.6: Only process final results
if transcript and is_final:
    utterance_queue.append(transcript)
    # Schedule delayed flush (0.6s silence gap)
    utterance_timer = asyncio.create_task(delayed_flush(0.6))
```

Even though `interim_results=true` was set in the Deepgram URL, the code never forwarded interim transcripts to the frontend. Users saw nothing until the utterance was finalized AND a 0.6s silence gap elapsed. Total delay: up to 1.6 seconds before text appeared.

## Fix (v10.7, applied 2026-06-16)

Send EVERY transcript immediately — interim and final:

```python
# ✅ v10.7: Send ALL transcripts instantly
if transcript:
    if is_final:
        utterance_queue.append(transcript)
        last_audio_time = time.time()
        # Send final transcript instantly
        await safe_send(json.dumps({"type": "transcript", "text": transcript}))
        # Schedule LLM reply after silence gap (0.8s)
        utterance_timer = asyncio.create_task(delayed_flush(0.8))
    else:
        # Send interim transcript instantly — real-time display
        await safe_send(json.dumps({"type": "interim", "text": transcript}))
```

## Key Design Decisions

1. **Two message types**: `"transcript"` for final, `"interim"` for partial. Frontend can style differently (e.g., gray italic for interim, black for final).
2. **LLM reply only on final**: Interim transcripts are display-only. The LLM is only triggered after 0.8s silence gap following a final transcript.
3. **Delayed flush increased to 0.8s**: Slightly longer gap compensates for instant display — user sees text immediately so they're more likely to continue speaking naturally.
4. **Frontend must handle both types**: The HTML frontend should update the transcript area for both `"interim"` and `"transcript"` messages. Interim text can be overwritten by the next interim or final.

## Testing

After fix, user sees real-time text as they speak. The "type: interim" messages arrive within ~100ms of speech, giving instant visual feedback. The "type: transcript" message confirms the final recognized text that will be sent to the LLM.
