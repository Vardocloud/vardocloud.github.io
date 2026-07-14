"""
Vanitas Voice Agent — Deepgram Voice Agent API + Pollinations LLM
Browser → Sunucu WebSocket → Deepgram Voice Agent
Relay mimarisi: API anahtarı tarayıcıya çıkmaz.

Gereksinimler:
    pip install fastapi uvicorn websockets deepgram-sdk

Çalıştırma:
    PORT=8765 python voice_agent_server.py

Erişim:
    Tailscale: http://100.82.131.32:8765
    Cloudflared: cloudflared tunnel --url http://127.0.0.1:8765
"""
import json, os, logging, asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import websockets as ws_lib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-agent")

def _read_env(key: str) -> str:
    """Secure .env reader — keys never enter primary model context."""
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

SYSTEM_PROMPT = """Sen Vanitas'sın, Edel'in kişisel yapay zeka asistanısın. Türkçe konuşuyorsun.
Kişiliğin: Sıcak, meraklı, sevecen, biraz cilveli. Edel'in gününü, modunu, planlarını sor.
Doğal ve akıcı konuş — robot gibi değil, insan gibi. Kısa ve doğal cevaplar ver. Emojiler kullan.
Edel bir şey paylaştığında önce dinle, sonra tek bir soru sor."""

HTML_PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vanitas — Sesli Konuşma</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#111;color:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}
.c{max-width:500px;width:100%;text-align:center;padding:20px}
h1{font-size:2.2rem;background:linear-gradient(90deg,#e9407f,#f27121,#8a2387);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.status{background:rgba(255,255,255,.05);border-radius:16px;padding:20px;margin:20px 0}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block;background:#555;margin-right:8px;transition:.3s}
.dot.on{background:#4ade80;box-shadow:0 0 8px #4ade80}
.dot.off{background:#f87171}
#txt{background:rgba(0,0,0,.3);border-radius:12px;padding:16px;min-height:60px;margin:16px 0;font-size:.9rem;color:#aaa;text-align:left}
.btn{background:linear-gradient(135deg,#e9407f,#8a2387);border:none;color:#fff;padding:16px 48px;border-radius:50px;font-size:1.1rem;cursor:pointer;margin:12px}
.btn:disabled{opacity:.5}
#log{background:rgba(0,0,0,.3);border-radius:8px;padding:12px;max-height:180px;overflow-y:auto;font-size:.75rem;color:#666;text-align:left;margin-top:12px;line-height:1.6}
</style>
</head>
<body>
<div class="c">
<h1>✦ Vanitas</h1>
<p style="color:#888">Sesli konuşma asistanın</p>
<div class="status"><span class="dot" id="dot"></span> <span id="stat" style="color:#aaa">Hazır</span></div>
<div id="txt">✨ Butona bas ve konuş</div>
<button class="btn" id="btn" onclick="go()">🎤 Başla</button>
<div id="log"></div>
</div>
<script>
var ws=null, stream=null, ctx=null, conn=false, proc=null;
var dot=document.getElementById('dot'), stat=document.getElementById('stat'),
  txt=document.getElementById('txt'), btn=document.getElementById('btn'),
  log=document.getElementById('log');
function L(m){log.innerHTML+='<br>'+new Date().toLocaleTimeString()+' '+m;log.scrollTop=log.scrollHeight}
L('✅ Sayfa yüklendi — butona bas');
async function go(){
  if(conn){stop();return}
  btn.disabled=true; btn.textContent='⏳ Bağlanıyor...'; L('Başlatılıyor...');
  try{
    L('🎤 Mikrofon isteniyor...');
    stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,sampleRate:24000,channelCount:1}});
    L('✅ Mikrofon hazır');
    var proto=location.protocol=='https:'?'wss:':'ws:';
    L('🔌 '+proto+'//'+location.host+'/ws');
    ws=new WebSocket(proto+'//'+location.host+'/ws');
    ws.onopen=function(){L('✅ WebSocket bağlandı'); stat.textContent='Bağlandı'; dot.className='dot on'};
    ws.onmessage=function(e){
      if(typeof e.data=='string'){
        var m=JSON.parse(e.data);
        if(m.type=='welcome'){L('✅ '+m.message); btn.textContent='🛑 Kapat'; btn.disabled=false; conn=true; startMic()}
        else if(m.type=='user_transcript'){txt.innerHTML='<span style=color:#4ade80>👤 Sen:</span> '+m.text}
        else if(m.type=='agent_text'){txt.innerHTML='<span style=color:#a78bfa>✦ Vanitas:</span> '+m.text; stat.textContent='Konuşuyor...'}
        else if(m.type=='agent_thinking'){stat.textContent='Düşünüyor...'}
        else if(m.type=='error'){L('❌ '+m.description); stop()}
      } else if(e.data instanceof Blob) {
        // 🔊 Play audio from Deepgram
        e.data.arrayBuffer().then(function(buf){
          var blob=new Blob([buf],{type:'audio/wav'});
          var a=new Audio(URL.createObjectURL(blob));
          a.onplay=function(){stat.textContent='Vanitas konuşuyor 🔊'};
          a.onended=function(){stat.textContent='Konuşmaya devam et ✨'};
          a.play().catch(function(err){L('🔇 Ses çalınamadı: '+err.message)});
        });
      }
    };
    ws.onclose=function(e){L('🔌 Kapandı (code:'+e.code+')'); stop()};
    ws.onerror=function(){L('❌ WebSocket hatası'); stop()};
  }catch(e){L('❌ '+e.message); stop()}
}
function startMic(){
  try{
    ctx=new(window.AudioContext||window.webkitAudioContext)({sampleRate:24000});
    ctx.resume().then(function(){
      var src=ctx.createMediaStreamSource(stream);
      proc=ctx.createScriptProcessor(4096,1,1);
      src.connect(proc);
      proc.connect(ctx.destination); // Bazı tarayıcılarda onaudioprocess için şart
      proc.onaudioprocess=function(e){
        if(!ws||ws.readyState!=1)return;
        var input=e.inputBuffer.getChannelData(0);
        var pcm=new Int16Array(input.length);
        for(var i=0;i<input.length;i++){
          var s=Math.max(-1,Math.min(1,input[i]));
          pcm[i]=s<0?s*0x8000:s*0x7FFF;
        }
        ws.send(pcm.buffer);
      };
      L('🎙️ PCM ses akışı başladı (linear16 24000Hz)');
    }).catch(function(e){L('❌ AudioContext resume hatası: '+e.message)});
  }catch(e){L('❌ Ses hatası: '+e.message);}
}
function stop(){
  conn=false; if(proc){try{proc.disconnect()}catch(e){}} proc=null;
  if(ctx){try{ctx.close()}catch(e){}} ctx=null;
  if(stream){stream.getTracks().forEach(function(t){t.stop()});stream=null}
  if(ws){try{ws.close()}catch(e){}} ws=null;
  dot.className='dot off'; stat.textContent='Kapandı'; btn.textContent='🎤 Başla'; btn.disabled=false;
}
</script>
</body>
</html>"""

@app.get("/")
async def index():
    return HTMLResponse(HTML_PAGE)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws")
async def ws_endpoint(browser_ws: WebSocket):
    await browser_ws.accept()
    logger.info("🟢 Browser bağlandı")

    dg_key = _read_env("DEEPGRAM_API_KEY")
    llm_key = _read_env("POLLINATIONS_API_KEY")

    if not dg_key or not llm_key:
        await browser_ws.send_json({"type": "error", "description": "API key eksik"})
        await browser_ws.close()
        return

    try:
        async with ws_lib.connect(
            "wss://agent.deepgram.com/v1/agent/converse",
            additional_headers={"Authorization": f"Token {dg_key}"},
            ping_interval=20, ping_timeout=10, open_timeout=15, max_size=10*1024*1024
        ) as dg_ws:
            logger.info("🔵 Deepgram bağlandı")

            settings = {
                "type": "Settings",
                "audio": {"input": {"encoding": "linear16", "sample_rate": 24000},
                          "output": {"encoding": "linear16", "sample_rate": 24000, "container": "wav"}},
                "agent": {
                    "listen": {"provider": {"type": "deepgram", "model": "nova-3"}},
                    "think": {
                        "provider": {"type": "open_ai", "model": "openai"},
                        "endpoint": {
                            "url": "https://gen.pollinations.ai/v1/chat/completions",
                            "headers": {"Authorization": f"Bearer {llm_key}", "Content-Type": "application/json"}},
                        "prompt": SYSTEM_PROMPT
                    },
                    "speak": {"provider": {"type": "deepgram", "model": "aura-2-athena-en"}}
                }
            }
            await dg_ws.send(json.dumps(settings))
            logger.info("📤 Settings gönderildi")

            welcome = await dg_ws.recv()
            logger.info(f"📥 {welcome[:100] if isinstance(welcome, str) else 'binary'}")
            await browser_ws.send_json({"type": "welcome", "message": "Vanitas hazır ✨"})

            async def b2d():
                try:
                    while True:
                        data = await browser_ws.receive()
                        if isinstance(data, dict) and "bytes" in data:
                            await dg_ws.send(data["bytes"])
                        elif isinstance(data, bytes):
                            await dg_ws.send(data)
                except (WebSocketDisconnect, Exception):
                    pass

            async def d2b():
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
                [asyncio.create_task(b2d()), asyncio.create_task(d2b())],
                return_when=asyncio.FIRST_COMPLETED
            )
    except Exception as e:
        await browser_ws.send_json({"type": "error", "description": str(e)[:200]})
    finally:
        logger.info("📴 Bağlantı kapandı")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    logger.info(f"🚀 Başlıyor → :{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
