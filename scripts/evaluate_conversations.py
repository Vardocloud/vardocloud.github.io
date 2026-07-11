#!/usr/bin/env python3
"""Vanitas ogrenme gunlugu — DeepSeek Flash ile gunluk degerlendirme.
Cron tarafindan her gun 03:00'te calistirilir."""
import sqlite3, json, os, sys
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = os.path.expanduser("~/.hermes/sessions.db")
OGREME_PATH = os.path.expanduser("~/.hermes/skills/sohbet/references/ogrenme.md")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

def get_recent_messages(hours=24):
    """Son N saatteki Edel mesajlarini getir"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
    
    cur.execute("""
        SELECT s.session_id, s.title, m.role, m.content, m.timestamp
        FROM messages m
        JOIN sessions s ON m.session_id = s.session_id
        WHERE s.platform = 'telegram'
        AND s.chat_id LIKE '%6306976553%'
        AND m.timestamp > ?
        ORDER BY m.timestamp DESC
        LIMIT 30
    """, (cutoff,))
    
    rows = cur.fetchall()
    conn.close()
    return rows

def build_evaluation_prompt(messages):
    """CQS degerlendirmesi icin prompt olustur"""
    convo = "\n".join([f"[{r[1]}] {r[2]}: {r[3][:200]}" for r in messages[:12]])
    
    return f"""Asagidaki Vanitas-Edel konusmasini CQS ile degerlendir:

{convo}

Su kriterlere gore puanla (her biri 0-1):
S1: Moderator gibi mi? (dinle → tut → sor)
S2: Tek soru mu sorulmus?
S3: Acik uclu soru mu?
S4: Baglam var mi?
S5: Arastirma referansi var mi?
S6: Dogal akis var mi?

E1: Edel detayli cevap verdi mi?
E2: Edel takip sorusu sordu mu?
E3: Edel kisisel bilgi paylasti mi?
E4: 3+ tur surdu mu?

F: Edel'in emoji/sozle geri bildirimi (👍=0.8, "guzel"=1.0, "yapma"=0.0)

JSON formatinda don:
{{"S": {{"S1": X, "S2": X, "S3": X, "S4": X, "S5": X, "S6": X}}, "E": {{"E1": X, "E2": X, "E3": X, "E4": X}}, "F": X, "CQS": X, "ogrenilen": "tek cumle"}}

SADECE JSON don, baska bir sey yazma."""

def call_deepseek(prompt):
    """DeepSeek Flash API cagrisi"""
    import requests
    resp = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
        json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 500},
        timeout=30
    )
    return resp.json()["choices"][0]["message"]["content"]

def update_ogrenme(eval_json):
    """ogrenme.md dosyasini guncelle"""
    try:
        data = json.loads(eval_json.strip().removeprefix("```json").removesuffix("```"))
    except:
        return False
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    s = data["S"]
    s_total = sum(s.values())
    e = data["E"]
    e_total = sum(e.values())
    f = data.get("F", None)
    cqs = data.get("CQS", round((s_total/6 + e_total/4) / 2, 2))
    ogrenilen = data.get("ogrenilen", "")
    
    new_section = f"""## Son Değerlendirme

**Tarih:** {now}
**Pencere:** son 12 mesaj
**CQS:** {cqs} (S:{s_total}/6, E:{e_total}/4, F:{f if f else 'none'})
**Model:** DeepSeek Flash (cron)

### S (Öz-değerlendirme): {s_total}/6
{s_to_md(s)}

### E (Edel Etkileşimi): {e_total}/4
{e_to_md(e)}

### F (Geri Bildirim): {f if f else 'none'}

### Öğrenilen
- {ogrenilen}
"""
    
    with open(OGREME_PATH) as f:
        content = f.read()
    
    # Replace old degerlendirme
    old_start = content.find("## Son Değerlendirme")
    old_end = content.find("---", old_start)
    
    content = content[:old_start] + new_section + "\n---\n" + content[old_end+4:]
    content = content.replace("*Son güncelleme:*", f"*Son güncelleme: {now} — otomatik (cron)*")
    
    with open(OGREME_PATH, 'w') as f:
        f.write(content)
    
    return True

def s_to_md(s):
    labels = {"S1": "Moderator", "S2": "Tek soru", "S3": "Açık uçlu", "S4": "Bağlam", "S5": "Araştırma ref.", "S6": "Doğal akış"}
    lines = []
    for k, v in s.items():
        icon = "✅" if v >= 0.7 else "❌"
        lines.append(f"- {icon} {labels.get(k, k)}")
    return "\n".join(lines)

def e_to_md(e):
    labels = {"E1": "Detaylı cevap", "E2": "Takip sorusu", "E3": "Kişisel bilgi", "E4": "3+ tur"}
    lines = []
    for k, v in e.items():
        icon = "✅" if v >= 0.7 else "❌"
        lines.append(f"- {icon} {labels.get(k, k)}")
    return "\n".join(lines)

if __name__ == "__main__":
    messages = get_recent_messages()
    if not messages:
        print("Son 24 saatte değerlendirilecek konuşma yok.")
        sys.exit(0)
    
    prompt = build_evaluation_prompt(messages)
    
    if DEEPSEEK_API_KEY:
        result = call_deepseek(prompt)
    else:
        print("DEEPSEEK_API_KEY bulunamadi. .env dosyasini kontrol et.")
        sys.exit(1)
    
    if update_ogrenme(result):
        print(f"✅ Değerlendirme tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    else:
        print("❌ Değerlendirme yazilamadi.")
