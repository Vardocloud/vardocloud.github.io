import requests, time, os
from pathlib import Path

key = Path(os.path.expanduser("~/.hermes/.env")).read_text().split("\n")
key = [l.split("=",1)[1].strip().strip("\"'") for l in key if "POLLINATIONS_API_KEY" in l][0]

BASE = "http://127.0.0.1:19999/v1"
T = [{"type":"function","function":{"name":"run_cmd","description":"Run command","parameters":{"type":"object","properties":{"c":{"type":"string"}},"required":["c"]}}}]

def test(md, task, tools=None):
    body = {"model":md,"messages":[{"role":"system","content":"Be concise."},{"role":"user","content":task}],"max_tokens":80,"stream":False}
    if tools: body["tools"]=tools; body["tool_choice"]="auto"
    t0=time.time()
    r=requests.post(f"{BASE}/chat/completions",json=body,timeout=30)
    ms=int((time.time()-t0)*1000)
    if r.status_code==200:
        m=r.json()["choices"][0]["message"]
        return ms,(m.get("content")or"")[:90],bool(m.get("tool_calls"))
    return ms,"ERR",False

tasks = {
    "Kod":"Write Python to reverse linked list. Code only.",
    "Analiz":"REST vs GraphQL 1 sentence.",
    "Yaratici":"Haiku about AI.",
    "Mantik":"All A are B, some B are C, does it follow some A are C? yes/no",
}

for m in ["deepseek","mistral","openai-fast","qwen-coder"]:
    print(f"\n--- {m} ---")
    for tn, tp in tasks.items():
        ms,tx,_ = test(m,tp)
        print(f"  {tn}: {ms}ms | {tx[:75]}")
        time.sleep(0.3)
    ms,tx,tc = test(m,"Run date",T)
    print(f"  Tool: {'✅ TC' if tc else '❌ no'} {ms}ms")
    time.sleep(0.3)
print("\nDone")
