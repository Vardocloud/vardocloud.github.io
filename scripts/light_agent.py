#!/usr/bin/env python3
# Ekip — Light Agent Runner (direkt Pollinations API)
# Kullanım: python3 light_agent.py <agent> "<görev>"
# Örnek:    python3 light_agent.py kodcu "Palindrome fonksiyonu yaz"

import sys, requests, os
from pathlib import Path

AGENTS = {
    "kodcu":    "minimax",
    "analist":  "glm",
    "yazar":    "gpt-5.4-mini",
    "yardimci": "gemma",
}

AGENT_DIR = Path.home() / ".hermes" / "agents"

def run(agent_name, task):
    prompt_file = AGENT_DIR / f"{agent_name}.md"
    if not prompt_file.exists():
        print(f"❌ Agent bulunamadı: {agent_name}")
        sys.exit(1)

    model = AGENTS[agent_name]
    system_prompt = prompt_file.read_text().strip()

    resp = requests.post(
        "http://127.0.0.1:19999/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task}
            ]
        },
        timeout=120
    )

    if resp.status_code == 200:
        content = resp.json()["choices"][0]["message"]["content"]
        print(content)
    else:
        print(f"❌ HTTP {resp.status_code}: {resp.text[:200]}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Kullanım: light_agent.py <agent> <görev>")
        print(f"Ajanlar: {', '.join(AGENTS.keys())}")
        sys.exit(1)
    run(sys.argv[1], " ".join(sys.argv[2:]))
