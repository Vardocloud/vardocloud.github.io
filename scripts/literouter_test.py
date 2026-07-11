#!/usr/bin/env python3
"""LiteRouter API test — modelleri listele ve test et"""
import os, json, urllib.request, urllib.error, ssl

# API key'i env'den oku
key = os.environ.get("LITEROUTER_API_KEY", "")
if not key:
    # .env dosyasını manuel parse et
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("LITEROUTER_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

if not key:
    print("❌ API key bulunamadı")
    exit(1)

print(f"🔑 Key: {key[:8]}...{key[-4:]} ({len(key)} chars)")

ssl_ctx = ssl.create_default_context()
BASE = "https://api.literouter.com/v1"

def api_call(endpoint, data=None):
    url = f"{BASE}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {key}",
        "User-Agent": "Vanitas/1.0"
    }
    if data:
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
    else:
        req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}

# 1. Model listesi
print("\n=== MODELS ===")
result = api_call("models")
if "error" in result:
    print(f"❌ {result['error']}")
    exit(1)

models = result.get("data", [])
print(f"Total: {len(models)} models")

free = sorted([m["id"] for m in models if ":free" in m.get("id", "")])
other = [m["id"] for m in models if ":free" not in m.get("id", "")]

print(f"\n🆓 FREE ({len(free)}):")
for m in free:
    print(f"  • {m}")

print(f"\n🔸 OTHER ({len(other)}):")
for m in other:
    print(f"  • {m}")

# 2. Chat test — deepseek:free
print("\n=== CHAT TEST (deepseek:free) ===")
result = api_call("chat/completions", {
    "model": "deepseek-v3.2:free",
    "messages": [{"role": "user", "content": "Reply in 2 words: hello"}],
    "max_tokens": 10
})
if "choices" in result:
    print(f"✅ {result['choices'][0]['message']['content']}")
elif "error" in result:
    print(f"❌ {result['error']}")

# 3. gpt-oss modellerini dene
print("\n=== GPT-OSS TEST ===")
oss_models = [m for m in models if "gpt-oss" in m.get("id", "").lower()]
if oss_models:
    for m in oss_models:
        mid = m["id"]
        print(f"  🔸 {mid}")
else:
    print("  Hiç gpt-oss modeli bulunamadı")

# 4. llama modellerini dene
print("\n=== LLAMA TEST ===")
llama_models = [m for m in models if "llama" in m.get("id", "").lower()]
if llama_models:
    for m in llama_models:
        mid = m["id"]
        print(f"  🔸 {mid}")
else:
    print("  Hiç llama modeli bulunamadı")
