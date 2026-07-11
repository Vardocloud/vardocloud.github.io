#!/usr/bin/env python3
"""Cron Health Check v2 — Temiz, tekrarsız, zaman bilinçli rapor."""
import json, os, sys
from datetime import datetime, timezone, timedelta

CRON_JSON = os.path.expanduser("~/.hermes/cron/jobs.json")
STATE_FILE = os.path.expanduser("~/.hermes/data/cron_health_state.json")
ERROR_THRESHOLD = timedelta(hours=24)  # eski hataları geçmiş say

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def parse_ts(ts_str):
    if not ts_str: return None
    try: return datetime.fromisoformat(ts_str)
    except: return None

def age_str(ts):
    now = datetime.now(timezone.utc)
    if not ts: return "?"
    diff = now - ts
    if diff.days > 0: return f"{diff.days}g once"
    if diff.seconds >= 3600: return f"{diff.seconds//3600}s {diff.seconds%3600//60}dk once"
    if diff.seconds >= 60: return f"{diff.seconds//60}dk once"
    return f"{diff.seconds}s once"

def short_error(err):
    """Traceback'i kısalt, sadece anlamlı son satırı göster."""
    if not err: return ""
    # Önce stderr kısmını ayıkla (varsa)
    if "stderr:" in err:
        err = err.split("stderr:")[1].split("stdout:")[0] if "stdout:" in err else err.split("stderr:")[1]
    elif "stdout:" in err:
        # stderr yoksa, stdout'tan önceki hata kısmı
        err = err.split("stdout:")[0]
    lines = err.strip().split("\n")
    # Traceback satırlarını atla
    meaningful = [l for l in lines if not l.startswith("  File") and not l.startswith("Traceback") and l.strip() and not l.startswith("def ") and not l.startswith("import ")]
    if meaningful:
        return meaningful[-1][:200]
    return lines[-1][:200]

def format_job_entry(job, now):
    """Her job için temiz bir satır."""
    name = job.get("name", job.get("id", "?"))
    status = job.get("last_status", "")
    last_error = job.get("last_error", "") or ""
    last_run = parse_ts(job.get("last_run_at"))
    enabled = job.get("enabled", True)
    state = job.get("state", "")
    delivery_err = job.get("last_delivery_error", "") or ""

    if not enabled or state == "paused":
        return None  # paused job'ları gösterme

    if status != "error" and not delivery_err:
        return None  # sadece hatalıları göster

    age = age_str(last_run)
    is_old = last_run and (now - last_run) > ERROR_THRESHOLD

    lines = []
    # Kısa hata mesajı
    if status == "error" and last_error:
        err_short = short_error(last_error)
        lines.append(f"  └ {err_short}")
    if delivery_err and delivery_err != "None":
        lines.append(f"  └ Teslimat: {delivery_err[:200]}")

    return {
        "name": name,
        "age": age,
        "is_old": is_old,
        "lines": lines,
        "last_error_hash": hash(last_error[:500]) if last_error else 0,
    }

def main():
    now = datetime.now(timezone.utc)
    jobs = load_json(CRON_JSON).get("jobs", [])
    prev_state = load_json(STATE_FILE)

    prev_hashes = set(prev_state.get("error_hashes", []))
    current_hashes = []

    fresh_errors = []
    old_errors = []
    repeated_count = 0

    for j in jobs:
        entry = format_job_entry(j, now)
        if not entry:
            continue

        # Deduplication: aynı hata önceki çalışmada da var mı?
        is_repeat = entry["last_error_hash"] in prev_hashes
        current_hashes.append(entry["last_error_hash"])

        if is_repeat:
            repeated_count += 1
            # Repeatleri kısa göster
            prefix = "🔄" if not entry["is_old"] else "⏳"
            short = f"{prefix} **{entry['name']}** — {short_error(j.get('last_error',''))[:120]} ({entry['age']})"
            old_errors.append(short)
        else:
            if entry["is_old"]:
                entry["lines"].insert(0, "  ⏰ 24s+ eski hata")
            fresh_errors.append(entry)

    # State kaydet (deduplication için)
    save_json(STATE_FILE, {
        "error_hashes": current_hashes,
        "last_check": now.isoformat(),
    })

    # ─── ÇIKTI ──────────────────────────────────────────────
    total = len(jobs)
    ok_count = sum(1 for j in jobs if j.get("last_status") == "ok" and j.get("enabled", True) and j.get("state") != "paused")

    output = []
    output.append(f"**🩺 Cron Sağlık** — {len(fresh_errors)} yeni, {repeated_count} tekrar | {ok_count}/{total} çalışıyor")
    output.append("")

    # Yeni/ilk kez görülen hatalar (öncelikli)
    if fresh_errors:
        output.append("**🔴 Yeni Hatalar**")
        for e in fresh_errors:
            output.append(f"• **{e['name']}** — {e['age']}")
            for l in e["lines"]:
                output.append(f"  {l}")
        output.append("")

    # Tekrar eden/geçmiş hatalar (daha sade)
    if old_errors:
        output.append("**🔁 Tekrarlanan / Geçmiş Hatalar**")
        for line in old_errors:
            output.append(f"  {line}")
        output.append("")

    # Özet satır
    paused = sum(1 for j in jobs if j.get("state") == "paused")
    if paused:
        output.append(f"⏸️ {paused} job paused (bilinçli durdurma)")

    final = "\n".join(output)
    if not final.strip():
        print("[SILENT]")
        return

    print(final)

if __name__ == "__main__":
    main()
