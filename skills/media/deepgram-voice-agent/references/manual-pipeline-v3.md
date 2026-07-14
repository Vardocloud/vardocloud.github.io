# Manual Pipeline v3 — Çalışan Referans Kod (2026-06-14)

Bu kod Deepgram STT + Mistral LLM + Deepgram TTS zincirini manuel olarak kurar.
Agent API kullanılmaz. Her adım loglanır.

## STT — Deepgram Listen WebSocket

```python
stt_url = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=linear16"
    "&sample_rate=24000"
    "&channels=1"
    "&model=nova-3"
    "&language=en"
    "&interim_results=false"
    "&endpointing=300"
)
stt_headers = {"Authorization": f"Token {dg_key}"}

async with websockets.connect(stt_url, additional_headers=stt_headers) as stt_ws:
    async for msg in stt_ws:
        data = json.loads(msg)
        if data.get("type") == "Results":
            alt = (data.get("channel", {}) or {}).get("alternatives", [])
            if alt and alt[0].get("transcript") and data.get("is_final"):
                text = alt[0]["transcript"].strip()
                # → LLM çağrısı
```

## LLM — Mistral

```python
async def call_llm(text: str, llm_key: str) -> str:
    system_prompt = (
        "You are Vanitas, Edel's personal AI assistant. "
        "Be warm, friendly, and VERY concise. 2-3 sentences max. "
        "You are on a voice call — speak naturally, no emojis."
    )
    payload = {
        "model": "mistral-small",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "max_tokens": 256,
        "temperature": 0.8
    }
    headers = {
        "Authorization": f"Bearer {llm_key}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            "https://api.mistral.ai/v1/chat/completions",
            json=payload, headers=headers
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
```

## TTS — Deepgram Speak REST

```python
async def call_tts(text: str, dg_key: str) -> bytes:
    tts_url = (
        "https://api.deepgram.com/v1/speak"
        "?model=aura-2-athena-en"
        "&encoding=linear16"
        "&sample_rate=24000"
    )
    headers = {
        "Authorization": f"Token {dg_key}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            tts_url,
            json={"text": text},
            headers=headers
        )
        resp.raise_for_status()
        return resp.content  # Ham linear16 PCM
```

## Async Yapı — browser_alive flag

```python
browser_alive = True

async def browser_to_stt():
    nonlocal browser_alive
    try:
        while True:
            data = await browser_ws.receive()
            if isinstance(data, dict) and "bytes" in data:
                await stt_ws.send(data["bytes"])
            elif isinstance(data, bytes):
                await stt_ws.send(data)
    except WebSocketDisconnect:
        browser_alive = False

async def stt_to_llm_to_tts():
    async for msg in stt_ws:
        ...  # STT → LLM → TTS
        if browser_alive:
            await browser_ws.send_bytes(audio)

task_b2s = asyncio.create_task(browser_to_stt())
task_s2l = asyncio.create_task(stt_to_llm_to_tts())
done, pending = await asyncio.wait(
    [task_b2s, task_s2l],
    return_when=asyncio.FIRST_COMPLETED
)
for task in pending:
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
```

## Provider Değiştirme

LLM provider değiştirmek için sadece `call_llm` fonksiyonundaki endpoint ve modeli değiştir:

```python
# Pollinations (ücretsiz):
url = "https://gen.pollinations.ai/v1/chat/completions"
model = "openai-large"

# OpenAI (ücretli):
url = "https://api.openai.com/v1/chat/completions"
model = "gpt-4o-mini"
```
