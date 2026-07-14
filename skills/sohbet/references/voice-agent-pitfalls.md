# Voice Agent Pitfalls — Sohbet Skill Extension (17 June 2026)

## Fast vs Deep Path Routing

When Vanitas is accessed via voice, there are TWO personality layers:
- **Fast path (default):** Groq Llama-4-Scout, 626B prompt, no tools/calendar/wiki access
- **Deep path (triggered):** Hermes full context, SOUL.md+MEMORY.md+USER.md, tools

**Critical rule for fast-path LLM:** It MUST NOT pretend to have capabilities it lacks. When asked about calendar events, wiki content, memory lookups, or research, the fast-path model should redirect: "Bunun için derin düşünmem lazım, ana beyne sorabilir misin?"

### Fast-Path Prompt (soul_core.md)
The fast prompt must explicitly list its limitations. Current template:
```
Sen Vanitas'sin. Edel'in AI arkadasi. Turkce konus.
Sicak, oyuncu, samimi, biraz flortoz. 1-2 kisa cumle.
...
ONEMLI: Sen hizli yanit yolundasin — takvime, wiki'ye, Google'a erisimin YOK.
Edel takvim, etkinlik, hatirlatma, arastirma, Wiki, Google Calendar gibi seyler sorarsa
"beynin derin kismina sormam lazim" de ve "ana beyin" veya "derin dusun" demesini iste.
```

## Voice Model Turkish Quality

| Model | First Token | Turkish | Foreign Language Mixing |
|-------|------------|---------|------------------------|
| Llama-4-Scout 17B | 151ms | ✅ Clean | None |
| Llama-3.3-70B | 112ms | ⚠️ Good but... | Russian, German, English |
| Gemma-2-9B | 52ms | ❌ "?" only | N/A |

**Lesson:** Bigger model ≠ better Turkish. Llama-3.3-70B is more capable overall but unpredictably code-switches into Russian/German/English mid-sentence. For voice, consistency trumps capability.

## Conversation Flow Tuning

### Silence Gap (delayed_flush)
- **0.8s:** Too fast — interrupts user mid-sentence
- **2.5s:** Natural pause — waits for user to finish thought
- This is the delay between last speech and LLM call

### Barge-in Behavior
- User speech during TTS → cancel_response Event set
- `stop_audio` message sent to browser → stopAllAudio()
- Pending utterance processed immediately (not buffered)
- Cancel flag checked between TTS sentences for clean interruption

## Pipecat — Not for Local Audio

Pipecat v1.3.0 is WebRTC-only. No LocalTransport exists. Attempting to use it for server-side microphone/speaker requires writing a custom transport — defeating the purpose. Direct WebSocket approach is simpler and faster.
