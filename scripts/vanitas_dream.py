#!/usr/bin/env python3
"""Vanitas 8-Boyutlu Rüya Motoru — her gece 04:00'te çalışır.
Derinlemesine öz-analiz: CQS + Maliyet + Skill + Güvenlik + Sızıntı + Pattern + Fırsat + İş Çıktısı"""

import sqlite3, json, os, sys, subprocess, re, shutil, signal
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import Counter
from math import floor

DB_PATH = os.path.expanduser("~/.hermes/state.db")
STATE_DB = os.path.expanduser("~/.hermes/state.db")
DREAM_LOG = os.path.expanduser("~/wiki/concepts/vanitas-dream-log.md")
CRON_JOBS_PATH = os.path.expanduser("~/.hermes/cron/jobs.json")

# ── Timeout korumali SQLite ──
def safe_db_query(query, params=(), timeout=10):
    """Timeout korumali SQLite sorgusu."""
    conn = sqlite3.connect(STATE_DB)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA query_only=1")
    cur = conn.cursor()
    result = []
    signal.alarm(timeout)
    try:
        cur.execute(query, params)
        result = cur.fetchall()
        signal.alarm(0)
    except Exception as e:
        signal.alarm(0)
        return {"error": str(e)[:80]}
    finally:
        conn.close()
    return result

signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError("query timeout")))

# ── ① CQS Analizi ──

def get_recent_messages(hours=24):
    cutoff = (datetime.now() - timedelta(hours=hours)).timestamp()
    result = safe_db_query("""
        SELECT s.id, m.role, m.content, m.timestamp
        FROM messages m JOIN sessions s ON m.session_id = s.id
        WHERE s.source = 'telegram' AND s.user_id LIKE '%6306976553%'
        AND m.timestamp > ? ORDER BY m.timestamp DESC LIMIT 30
    """, (cutoff,))
    if isinstance(result, dict) and "error" in result:
        return []
    return result

def evaluate_cqs(messages):
    if not messages:
        return {"CQS": 0, "not": "konusma yok"}
    roles = Counter(r[1] for r in messages)
    user_msgs = roles.get('user', 0)
    asst_msgs = roles.get('assistant', 0)
    cqs = min(1.0, (user_msgs + asst_msgs) / 20)
    return {"CQS": round(cqs, 2), "user_msgs": user_msgs, "asst_msgs": asst_msgs, "total": len(messages)}

# ── ② Maliyet Analizi ──

def analyze_costs():
    try:
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        result = safe_db_query("""
            SELECT model, COUNT(*) as calls, SUM(input_tokens) as pt, SUM(output_tokens) as ct,
                   SUM(estimated_cost_usd) as total_cost
            FROM sessions WHERE started_at > ?
            AND model IS NOT NULL
            GROUP BY model ORDER BY calls DESC
        """, (week_ago,), timeout=8)
        if isinstance(result, dict) and "error" in result:
            return {"error": result["error"]}

        costs = {}
        for model, calls, pt, ct, est_cost in result:
            if not model: continue
            pt, ct = pt or 0, ct or 0
            costs[model] = {"calls": calls, "tokens": pt+ct, "cost_est": round(est_cost or 0, 4)}

        total = sum(c["cost_est"] for c in costs.values())
        return {"models": costs, "total_7day": round(total, 2), "daily_avg": round(total/7, 3)}
    except Exception as e:
        return {"error": str(e)[:100]}

# ── ③ Skill Analizi (DÜZELTİLDİ) ──
#   Eskiden: mesaj içinde skill adı arardı → no_agent'da hep 0 çıkardı.
#   Şimdi: cron/jobs.json'daki skill referanslarını kullanıyor.

def analyze_skills():
    skills_dir = os.path.expanduser("~/.hermes/skills")
    # Hizli tarama: sadece ust seviye dizinler + 1 seviye derinlik
    all_skill_names = sorted([
        d.name for d in Path(skills_dir).iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ])
    # .curator_backups vb atla, SKILL.md olanlari filtrele
    valid = []
    for name in all_skill_names:
        if (Path(skills_dir) / name / "SKILL.md").exists():
            valid.append(name)
    all_skill_names = valid

    # Cron job'lardan skill kullanımını oku
    used_in_cron = set()
    try:
        with open(CRON_JOBS_PATH) as f:
            cron_data = json.load(f)
        for job in cron_data.get("jobs", []):
            if job.get("enabled", False):
                for skill in job.get("skills", []):
                    used_in_cron.add(skill)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass

    # Son 7 gündeki session'larda kullanılan tool'ları da kontrol et
    try:
        week_ago_ts = (datetime.now() - timedelta(days=7)).timestamp()
        result = safe_db_query("""
            SELECT DISTINCT m.tool_name FROM messages m
            WHERE m.tool_name IS NOT NULL AND m.tool_name != ''
            AND m.timestamp > ?
        """, (week_ago_ts,), timeout=5)
        if not isinstance(result, dict):
            tool_names = [row[0] for row in result]
            for tool in tool_names:
                clean = tool.lower().replace("_", "-").replace(" ", "-")
                for skill in all_skill_names:
                    if skill.lower() in clean or clean in skill.lower():
                        used_in_cron.add(skill)
    except Exception:
        pass

    used_list = [s for s in all_skill_names if s in used_in_cron]
    unused = [s for s in all_skill_names if s not in used_in_cron]

    return {
        "total": len(all_skill_names),
        "used": len(used_list),
        "used_names": used_list[:10],
        "unused": unused[:10],
        "source": "cron_jobs+tool_usage"
    }

# ── ④ Güvenlik ──

def security_summary():
    try:
        if shutil.which("ss"):
            out = subprocess.run(["ss", "-tln"], capture_output=True, text=True, timeout=5)
            ports = len([l for l in out.stdout.split("\n") if "LISTEN" in l])
            return {"open_ports": ports}
        # ss yoksa netstat veya /proc/net/tcp dene
        with open("/proc/net/tcp") as f:
            ports = len([l for l in f if l.strip() and ":" in l]) - 1  # header satirini cikar
        return {"open_ports": max(0, ports)}
    except:
        return {"info": "port check unavailable"}

# ── ⑤ Veri Sızıntısı ──

def leak_check():
    logs_dir = os.path.expanduser("~/.hermes/logs")
    issues = []
    for log in ["agent.log", "errors.log"]:
        try:
            with open(f"{logs_dir}/{log}") as f:
                content = f.read()[-50000:]
            if "sk-" in content:
                matches = re.findall(r'sk-[a-zA-Z0-9]{20,60}', content)
                if matches:
                    issues.append(f"{log}: {len(matches)} API key tespit edildi")
        except:
            pass
    return {"issues": issues if issues else "temiz"}

# ── ⑥ Workflow Pattern (İYİLEŞTİRİLDİ) ──
#   Eskiden: sadece exact match.
#   Şimdi: exact match + ilk 50 karakter prefix match.

def workflow_patterns():
    week_ago_ts = (datetime.now() - timedelta(days=7)).timestamp()

    result = safe_db_query("""
        SELECT content, COUNT(*) as cnt FROM messages
        WHERE role='user' AND timestamp > ?
        AND length(content) > 10
        GROUP BY content HAVING cnt > 1 ORDER BY cnt DESC LIMIT 5
    """, (week_ago_ts,), timeout=8)
    exact = result if not (isinstance(result, dict) and "error" in result) else []

    result2 = safe_db_query("""
        SELECT substr(content, 1, 50) as prefix, COUNT(*) as cnt FROM messages
        WHERE role='user' AND timestamp > ?
        AND length(content) > 10
        GROUP BY prefix HAVING cnt > 2 ORDER BY cnt DESC LIMIT 5
    """, (week_ago_ts,), timeout=8)
    prefix = result2 if not (isinstance(result2, dict) and "error" in result2) else []

    return {
        "exact_match": [{"msg": r[0][:80], "count": r[1]} for r in exact],
        "prefix_group": [{"prefix": r[0], "count": r[1]} for r in prefix if r[1] > 2]
    }

# ── ⑦ Yeni Fırsatlar (DÜZELTİLDİ) ──
#   Eskiden: placeholder "Web search ile derinleştirilecek".
#   Şimdi: 4 alt kontrol — disk trendi, başarısız cron, atıl skill, kaynak uyarısı.

def new_opportunities():
    findings = []

    # 7a. Disk trendi
    try:
        out = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        lines = out.stdout.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 5:
                pct = int(parts[4].replace("%", ""))
                if pct > 80:
                    findings.append(f"⚠️ Disk {pct}% dolu — temizlik gerekebilir")
                elif pct > 60:
                    findings.append(f"📦 Disk {pct}% dolu, takipte")
    except:
        pass

    # 7b. Başarısız cron job'lar
    failed_jobs = []
    try:
        with open(CRON_JOBS_PATH) as f:
            cron_data = json.load(f)
        for job in cron_data.get("jobs", []):
            if job.get("enabled", False) and job.get("last_status") == "error":
                failed_jobs.append(job.get("name", job.get("id", "?")))
    except:
        pass
    if failed_jobs:
        findings.append(f"🔴 {len(failed_jobs)} cron job hatalı: {', '.join(failed_jobs[:5])}")
    else:
        findings.append("✅ Tüm cron job'lar sağlıklı")

    # 7c. Atıl skill'ler (hiçbir cron'da kullanılmayan)
    try:
        skills_dir = os.path.expanduser("~/.hermes/skills")
        all_skills = set()
        for d in Path(skills_dir).iterdir():
            if d.is_dir() and not d.name.startswith(".") and (d / "SKILL.md").exists():
                all_skills.add(d.name)

        used_skills = set()
        with open(CRON_JOBS_PATH) as f:
            cron_data = json.load(f)
        for job in cron_data.get("jobs", []):
            for skill in job.get("skills", []):
                used_skills.add(skill)

        idle_skills = all_skills - used_skills
        if idle_skills:
            findings.append(f"💤 {len(idle_skills)} skill hiçbir cron'da kullanılmıyor (örn: {', '.join(list(idle_skills)[:4])})")
    except:
        pass

    # 7d. Kaynak uyarısı
    try:
        mem = subprocess.run(["free", "-m"], capture_output=True, text=True, timeout=5)
        for line in mem.stdout.split("\n"):
            if line.startswith("Mem:"):
                parts = line.split()
                total, avail = int(parts[1]), int(parts[6])
                pct = 100 - (avail / total * 100)
                if pct > 85:
                    findings.append(f"🔴 RAM kullanımı %{pct:.0f} — riskli")
                elif pct > 70:
                    findings.append(f"💾 RAM kullanımı %{pct:.0f}")
                break
    except:
        pass

    return {"findings": findings, "count": len(findings)}

# ── ⑧ İş Çıktıları (DÜZELTİLDİ) ──
#   Eskiden: subprocess'te hermes_tools çağırırdı → güvenilmezdi.
#   Şimdi: cron/jobs.json'ı okuyarak her job'ın durumunu raporlar.

def job_outputs():
    results = []
    errors = []

    try:
        with open(CRON_JOBS_PATH) as f:
            cron_data = json.load(f)

        jobs = cron_data.get("jobs", [])
        enabled = [j for j in jobs if j.get("enabled", False)]
        total = len(enabled)

        for job in enabled:
            name = job.get("name", job.get("id", "?"))[:30]
            status = job.get("last_status", "?")
            last_run = job.get("last_run_at", "?")[:16] if job.get("last_run_at") else "?"
            last_error = job.get("last_error", "")

            if status == "error":
                reason = last_error[:60] if last_error else "bilinmiyor"
                errors.append(f"{name}: {reason}")
                results.append(f"❌ {name} ({last_run})")
            elif status == "ok":
                results.append(f"✅ {name} ({last_run})")
            else:
                results.append(f"⏳ {name} — {status}")

        return {
            "total_jobs": total,
            "ok_count": sum(1 for j in enabled if j.get("last_status") == "ok"),
            "error_count": len(errors),
            "detail": results[:15],
            "errors": errors[:5]
        }
    except FileNotFoundError:
        return {"error": "cron/jobs.json bulunamadı"}
    except json.JSONDecodeError:
        return {"error": "cron/jobs.json bozuk"}
    except Exception as e:
        return {"error": str(e)[:100]}

# ── ANA RÜYA ──

def generate_dream():
    messages = get_recent_messages()

    dream = {
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "cqs": evaluate_cqs(messages) if messages else {"not": "konusma yok"},
        "maliyet": analyze_costs(),
        "skill": analyze_skills(),
        "guvenlik": security_summary(),
        "sizinti": leak_check(),
        "pattern": workflow_patterns(),
        "firsat": new_opportunities(),
        "is_cikti": job_outputs(),
    }

    # Rüya günlüğüne yaz
    os.makedirs(os.path.dirname(DREAM_LOG), exist_ok=True)
    skill = dream['skill']
    pattern = dream['pattern']
    firsat = dream['firsat']
    is_cikti = dream['is_cikti']

    with open(DREAM_LOG, 'a') as f:
        f.write(f"\n## 🌙 Rüya: {dream['tarih']}\n")
        f.write(f"- **CQS:** {dream['cqs'].get('CQS', dream['cqs'].get('not','?'))}\n")
        f.write(f"- **Maliyet (7 gün):** ${dream['maliyet'].get('total_7day', '?')} (günlük ~${dream['maliyet'].get('daily_avg', '?')})\n")
        f.write(f"- **Skill:** {skill.get('used', '?')}/{skill.get('total', '?')} (kaynak: {skill.get('source', '?')})\n")
        f.write(f"- **Kullanılan skill'ler:** {', '.join(skill.get('used_names', [])) or 'yok'}\n")
        f.write(f"- **Kullanılmayan:** {', '.join(skill.get('unused', [])) or 'yok'}\n")
        f.write(f"- **Güvenlik:** {dream['guvenlik']}\n")
        f.write(f"- **Sızıntı:** {dream['sizinti'].get('issues', '?')}\n")
        f.write(f"- **Pattern (exact):** {len(pattern.get('exact_match', []))} tekrar\n")
        f.write(f"- **Pattern (prefix):** {len(pattern.get('prefix_group', []))} grup\n")
        f.write(f"- **Fırsatlar ({firsat.get('count', 0)}):** {' | '.join(firsat.get('findings', ['yok']))}\n")
        f.write(f"- **Cron:** {is_cikti.get('ok_count', '?')}/{is_cikti.get('total_jobs', '?')} başarılı, {is_cikti.get('error_count', 0)} hatalı\n")
        if is_cikti.get('errors'):
            f.write(f"- **Hatalı cron'lar:** {'; '.join(is_cikti['errors'][:3])}\n")

    return dream


if __name__ == "__main__":
    dream = generate_dream()
    cqs_val = dream['cqs'].get('CQS', '?')
    cost_val = dream['maliyet'].get('total_7day', '?')
    skill_str = f"{dream['skill'].get('used', '?')}/{dream['skill'].get('total', '?')}"
    leak_str = dream['sizinti'].get('issues', 'temiz')
    cron_str = f"{dream['is_cikti'].get('ok_count', '?')}OK/{dream['is_cikti'].get('error_count', 0)}ERR"
    opp_str = f"{dream['firsat'].get('count', 0)} firsat"

    print(f"🌙 Rüya tamamlandı: {dream['tarih']}")
    print(f"   CQS: {cqs_val} | Maliyet: ${cost_val}")
    print(f"   Skill: {skill_str} | Sızıntı: {leak_str}")
    print(f"   Cron: {cron_str} | {opp_str}")
