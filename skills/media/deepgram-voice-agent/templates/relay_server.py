"""
Vanitas Voice Agent — FastAPI relay server
Browser → WebSocket → this server → Deepgram Voice Agent WS → this server → browser
"""
import json, os, logging, asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import websockets as ws_lib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-agent")

# ─── Secure env reader ───
def _read_env(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        try:
            env_path = Path.home() / ".hermes" / ".env"
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith(key + "="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        except Exception: pass
    return val

app = FastAPI(title="Vanitas Voice Agent")

# ─── HTML Page (inline) ───
# Browser support detection, PCM capture via ScriptProcessorNode, audio queue playback

# ─── API Routes ───
@app.get("/")
async def index():
    """Serve the voice agent HTML page. Replace HTML_PAGE with actual content."""
    return HTMLResponse("<html>...</html>")

@app.get("/health")
async def health():
    return {"status": "ok"}

# ─── WebSocket Relay ───
@app.websocket("/ws")
async def ws_endpoint(browser_ws: WebSocket):
    await browser_ws.accept()
    dg_key = _read_env("DEEPGRAM_API_KEY")
    ds_key = _read_env("DEEPSEEK_API_KEY")
    
    if not dg_key or not ds_key:
        await browser_ws.send_json({"type": "error", "description": "Eksik API key"})
        await browser_ws.close()
        return
    
    try:
        async with ws_lib.connect(
            "wss://agent.deepgram.com/v1/agent/converse",
            additional_headers={"Authorization": f"Token {dg_key}"},
            ping_interval=20, ping_timeout=10, open_timeout=15,
            max_size=10 * 1024 * 1024
        ) as dg_ws:
            # Send settings
            settings = {
                "type": "Settings",
                "audio": {
                    "input": {"encoding": "linear16", "sample_rate": 24000},
                    "output": {"encoding": "linear16", "sample_rate": 24000, "container": "wav"}
                },
                "agent": {
                    "listen": {"provider": {"type": "deepgram", "model": "nova-3"}},
                    "think": {
                        "provider": {"type": "open_ai", "model": "deepseek-chat"},
                        "endpoint": {
                            "url": "https://api.deepseek.com/v1/chat/completions",
                            "headers": {
                                "Authorization": f"Bearer {ds_key}",
                                "Content-Type": "application/json"
                            }
                        },
                        "prompt": "Sen Vanitas'sın. Türkçe, samimi ve doğal konuş. Kısa cevaplar ver."
                    },
                    "speak": {"provider": {"type": "deepgram", "model": "aura-2-athena-en"}}
                }
            }
            await dg_ws.send(json.dumps(settings))
            
            # Wait for Welcome
            welcome = await dg_ws.recv()
            await browser_ws.send_json({"type": "welcome", "message": "Vanitas hazır ✨"})
            
            # Bidirectional relay
            async def browser_to_deepgram():
                try:
                    while True:
                        data = await browser_ws.receive()
                        if isinstance(data, dict) and "bytes" in data:
                            await dg_ws.send(data["bytes"])
                        elif isinstance(data, bytes):
                            await dg_ws.send(data)
                except (WebSocketDisconnect, Exception):
                    pass
            
            async def deepgram_to_browser():
                try:
                    async for msg in dg_ws:
                        if isinstance(msg, bytes):
                            await browser_ws.send_bytes(msg)
                        else:
                            data = json.loads(msg)
                            t = data.get("type", "")
                            if t == "ConversationText":
                                role = data.get("role", "assistant")
                                text = data.get("content") or data.get("text", "")
                                if role == "user":
                                    await browser_ws.send_json({"type": "user_transcript", "text": text})
                                elif text:
                                    await browser_ws.send_json({"type": "agent_text", "text": text})
                            elif t == "UserStartedSpeaking":
                                await browser_ws.send_json({"type": "user_transcript", "text": "..."})
                            elif t == "AgentThinking":
                                await browser_ws.send_json({"type": "agent_thinking"})
                            elif t == "Error":
                                await browser_ws.send_json({"type": "error", "description": data.get("description", "Deepgram hatası")})
                except Exception:
                    pass
            
            await asyncio.wait(
                [asyncio.create_task(browser_to_deepgram()), asyncio.create_task(deepgram_to_browser())],
                return_when=asyncio.FIRST_COMPLETED
            )
    except Exception as e:
        await browser_ws.send_json({"type": "error", "description": str(e)[:200]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    logger.info(f"🚀 Başlıyor → :{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
