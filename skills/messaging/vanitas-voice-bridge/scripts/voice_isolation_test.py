#!/usr/bin/env python3
"""Server-side isolation test. Sends Turkish PCM to ws://127.0.0.1:8765.
If server responds -> frontend problem. If silent -> pipeline problem.
Prereq: pip install edge-tts websockets; ffmpeg installed
"""
import asyncio, json, websockets, time, os

URL = "ws://127.0.0.1:8765?language=tr&voice=Grace"
PCM = "/tmp/test_speech.pcm"

async def gen():
    import edge_tts
    c = edge_tts.Communicate("Merhaba Vanitas, nasilsin bugun?", "tr-TR-EmelNeural")
    await c.save("/tmp/test_speech.mp3")
    os.system("ffmpeg -y -i /tmp/test_speech.mp3 -acodec pcm_s16le -ac 1 -ar 16000 -f s16le /tmp/test_speech.pcm 2>/dev/null")

async def run():
    if not os.path.exists(PCM): await gen()
    with open(PCM,"rb") as f: pcm = f.read()
    print(f"PCM: {len(pcm)}b ({len(pcm)/32000:.1f}s)")
    ws = await websockets.connect(URL, max_size=None)
    try: await asyncio.wait_for(ws.recv(), timeout=5)
    except: pass
    for _ in range(10): await ws.send(b'\x00\x00'*1600); await asyncio.sleep(0.05)
    r = {"stt":[],"llm":[],"tts":0}
    for i in range(0,len(pcm),3200):
        await ws.send(pcm[i:i+3200])
        try:
            m = await asyncio.wait_for(ws.recv(), timeout=0.01)
            if isinstance(m,bytes): r["tts"]+=len(m)
            else:
                d=json.loads(m)
                t=d.get("final_text","") or d.get("non_final_text","")
                if "transcription" in d.get("type","") and t: r["stt"].append(t)
                if "llm" in d.get("type",""): r["llm"].append(d.get("text",""))
        except: pass
        await asyncio.sleep(0.02)
    for _ in range(20):
        await ws.send(b'\x00\x00'*1600); await asyncio.sleep(0.1)
        try:
            m = await asyncio.wait_for(ws.recv(), timeout=0.05)
            if isinstance(m,bytes): r["tts"]+=len(m)
        except: pass
    s=time.time()
    while time.time()-s<10:
        try:
            m=await asyncio.wait_for(ws.recv(),timeout=2)
            if isinstance(m,bytes): r["tts"]+=len(m)
        except: break
    await ws.close()
    print(f"STT:{len(r['stt'])} LLM:{len(r['llm'])} TTS:{r['tts']}b")
    for t in r["stt"][-3:]: print(f"  -> '{t}'")
    print("SERVER OK - frontend problem" if r["stt"] or r["tts"]>0 else "SERVER SILENT - pipeline problem")

if __name__=="__main__": asyncio.run(run())