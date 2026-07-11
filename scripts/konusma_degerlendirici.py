#!/usr/bin/env python3
"""Konuşma Değerlendirici — Vanitas günlük sohbet kalite kontrolü.
Cron job (no_agent=true) olarak çalışır. stdout'a yazdığı özet direkt Edel'e iletilir.

v2 — httpx + BWS key + clean error handling + timeout cron uyumlu
Cron no_agent script'lerde built-in timeout 120sn, bu yüzden script içi timeout 110sn.
"""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta

import httpx

DB = os.path.expanduser("~/.hermes/state.db")
KEY_FILE = "/tmp/.or_key"
PROMPT_FILE = os.path.expanduser(
    "~/.hermes/skills/sohbet/references/konusma-degerlendirme-prompt.md"
)
OUTPUT_FILE = os.path.expanduser(
    "~/.hermes/skills/sohbet/references/ogrenme.md"
)

API_URL = "https://api.literouter.com/v1/chat/completions"
MODEL = "deepseek-v3.2:free"
# Cron no_agent script timeout default 120sn — altında kal
TIMEOUT = 110


def get_key():
    """API anahtarını sırayla dene: BWS → env var → /tmp/.or_key."""
    # 1. BWS (Bitwarden Secrets Manager)
    bws_bin = os.path.expanduser("~/.hermes/bin/bws")
    if os.path.exists(bws_bin):
        try:
            result = subprocess.run(
                [bws_bin, "secret", "list"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                secrets = json.loads(result.stdout)
                for s in secrets:
                    if s.get("key") == "LITEROUTER_API_KEY":
                        return s["value"]
        except Exception:
            pass

    # 2. Environment variable
    env_key = os.environ.get("LITEROUTER_API_KEY")
    if env_key:
        return env_key

    # 3. Fallback: /tmp/.or_key
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE) as f:
            return f.read().strip()

    raise FileNotFoundError(
        f"API key bulunamadı. BWS'de LITEROUTER_API_KEY yok, "
        f"LITEROUTER_API_KEY env var tanımlı değil, "
        f"{KEY_FILE} mevcut değil."
    )


def get_recent_conversations(hours=24):
    """Son N saatteki Edel-Vanitas konuşmalarını çek."""
    conn = sqlite3.connect(DB)
    since = (datetime.now() - timedelta(hours=hours)).timestamp()

    rows = conn.execute(
        """
        SELECT m.role, m.content, m.timestamp
        FROM messages m
        JOIN sessions s ON m.session_id = s.id
        WHERE m.timestamp > ?
          AND m.role IN ('user', 'assistant')
          AND s.source = 'telegram'
        ORDER BY m.timestamp DESC
        LIMIT 100
    """,
        (since,),
    ).fetchall()
    conn.close()

    if not rows:
        return None

    rows.reverse()
    pairs = []
    current_user = None

    for role, content, ts in rows:
        if role == "user":
            current_user = content[:200]
        elif role == "assistant" and current_user:
            pairs.append(
                {"edel": current_user, "vanitas": content[:300], "time": ts}
            )
            current_user = None

    return pairs[-20:] if pairs else None


def clean_json_response(content: str) -> str:
    """Markdown kod bloklarını temizle, JSON dışındaki metinleri kırp."""
    content = content.strip()
    # ```json ... ``` veya ``` ... ``` bloklarını temizle
    if content.startswith("```"):
        lines = content.split("\n")
        # İlk satırı (```json) ve son satırı (```) at
        start = 1 if len(lines) > 1 else 0
        end = -1 if len(lines) > 2 else len(lines)
        content = "\n".join(lines[start:end])
    content = content.strip()
    # Bazen "Here is the JSON:" gibi metin öncesi olabilir, ilk { veya [ konumuna git
    brace_idx = content.find("{")
    bracket_idx = content.find("[")
    json_start = -1
    if brace_idx >= 0 and bracket_idx >= 0:
        json_start = min(brace_idx, bracket_idx)
    elif brace_idx >= 0:
        json_start = brace_idx
    elif bracket_idx >= 0:
        json_start = bracket_idx
    if json_start > 0:
        content = content[json_start:]

    # Sondaki } veya ] sonrasını kırp
    last_brace = content.rfind("}")
    last_bracket = content.rfind("]")
    json_end = max(last_brace, last_bracket)
    if json_end > 0:
        content = content[: json_end + 1]

    return content.strip()


def call_literouter(system_prompt: str, user_content: str) -> str:
    """LiteRouter API'ye httpx ile çağrı. Tek deneme, cron timeout'u aşmamak için."""
    key = get_key()

    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
                + "\n\nSADECE JSON döndür. Markdown kodu (```json```) KULLANMA. Her konuşma için ayri degerlendirme yap, ortalama ve genel_ozet ekle.",
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
        "max_tokens": 4000,
        "temperature": 0.0,
    }

    with httpx.Client(timeout=httpx.Timeout(TIMEOUT)) as client:
        resp = client.post(
            API_URL,
            json=body,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "User-Agent": "vanitas/2.0",
            },
        )

    if resp.status_code != 200:
        raise RuntimeError(
            f"LiteRouter API {resp.status_code}: {resp.text[:500]}"
        )

    result = resp.json()
    msg = result.get("choices", [{}])[0].get("message", {})
    content = msg.get("content", "")

    if not content:
        # DeepSeek bazen reasoning/thinking modunda farklı yapı dönebilir
        content = msg.get("reasoning_content") or msg.get("thinking") or ""
        if not content:
            raise RuntimeError(
                "LiteRouter empty response: " + json.dumps(msg)[:1000]
            )

    return clean_json_response(content)


def eval_conversation(conversations):
    """LiteRouter (DeepSeek V3.2) ile değerlendir."""
    with open(PROMPT_FILE) as f:
        system_prompt = f.read()

    # Son 5 konuşmayı değerlendir
    sample = conversations[-5:]
    convo_text = "\n---\n".join(
        [
            f"Edel: {c['edel']}\nVanitas: {c['vanitas']}"
            for c in sample
        ]
    )

    user_content = (
        f"Su konusmalari degerlendir, HER BIRI icin M/T/A/B/R/D puanla (1-10), "
        f"sonra ORTALAMA ve OZET ver:\n\n{convo_text}\n\n"
        f'JSON: {{"konusmalar":[{{"puanlar":{{...}},"ozet":"..."}}],'
        f'"ortalama":{{"M":X,"T":X,"A":X,"B":X,"R":X,"D":X}},"genel_ozet":"..."}}'
    )

    return call_literouter(system_prompt, user_content)


def write_report(raw_json):
    """Raporu ogrenme.md'ye ekle."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {now} — Konuşma Değerlendirme\n\n```json\n{raw_json}\n```\n"

    with open(OUTPUT_FILE, "a") as f:
        f.write(entry)


def parse_and_print(result: str):
    """JSON sonucu ayrıştır ve özet çıktı üret."""
    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        print(f"📊 Ham sonuç (JSON ayrıştırılamadı):\n{result[:500]}")
        return

    avg = data.get("ortalama", {})
    if avg:
        toplam = sum(v for v in avg.values() if isinstance(v, (int, float)))
        emoji = "🟢" if toplam >= 40 else ("🟡" if toplam >= 25 else "🔴")
        print(f"🧠 Günlük Sohbet Raporu\n")
        print(f"{emoji} Ortalama: {toplam}/60")
        print(
            f"   M:{avg.get('M','?')} T:{avg.get('T','?')} "
            f"A:{avg.get('A','?')} B:{avg.get('B','?')} "
            f"R:{avg.get('R','?')} D:{avg.get('D','?')}"
        )
    else:
        print("📊 Ortalama verisi bulunamadı.")

    ozet = data.get("genel_ozet", "")
    if ozet:
        print(f"\n📝 {ozet}")


# === MAIN ===
def main():
    convs = get_recent_conversations()
    if not convs:
        print("📭 Son 24 saatte değerlendirilecek konuşma bulunamadı.")
        return

    try:
        result = eval_conversation(convs)
        write_report(result)
        parse_and_print(result)
    except FileNotFoundError as e:
        print(f"🔴 API anahtarı hatası: {e}")
        sys.exit(5)
    except httpx.TimeoutException:
        print(
            f"🔴 LiteRouter API {TIMEOUT}s zaman aşımı. "
            f"Model ({MODEL}) yoğun olabilir."
        )
        sys.exit(4)
    except httpx.HTTPStatusError as e:
        print(f"🔴 LiteRouter HTTP {e.response.status_code}: {e.response.text[:300]}")
        sys.exit(3)
    except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
        print(f"🔴 LiteRouter bağlantı hatası: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"⚠️ Konuşma değerlendirme hatası: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
