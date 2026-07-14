#!/usr/bin/env python3
"""Evening pre-check: Fetch tomorrow's calendar events and create one-shot reminder + follow-up jobs.

Runs at 21:00 daily via Hermes cron.
For each event tomorrow:
  1. One-shot reminder job (event_time - 2 hours)
  2. One-shot post-event 5N1K follow-up job (event_end + 15 min)
If event is less than 2h away from now, reminder fires in 5 minutes.
"""

import json, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
JOBS_FILE = HERMES_HOME / "cron" / "jobs.json"
# Always point to the skill dir — NOT SCRIPT_DIR which resolves to ~/.hermes/cron/
GOOGLE_API = HERMES_HOME / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py"

def run_cmd(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r

def load_jobs():
    if JOBS_FILE.exists():
        with open(JOBS_FILE) as f:
            return json.load(f)
    return {"jobs": [], "updated_at": datetime.now(timezone.utc).isoformat()}

def save_jobs(data):
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    tmp = JOBS_FILE.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.rename(JOBS_FILE)

def create_oneshot(name, prompt, run_at, deliver="telegram", skills=None):
    data = load_jobs()
    data["jobs"] = [j for j in data["jobs"] if j.get("name") != name]
    job = {"id": name, "name": name, "prompt": prompt,
           "schedule": run_at.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "repeat": 1, "deliver": deliver, "enabled": True}
    if skills:
        job["skills"] = skills
    data["jobs"].append(job)
    save_jobs(data)
    print(f"Created: {name} @ {run_at.isoformat()}")

def main():
    tz = timezone(timedelta(hours=3))
    now = datetime.now(tz)
    tmr_start = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    tmr_end = tmr_start + timedelta(days=1)

    r = run_cmd([sys.executable, str(GOOGLE_API), "calendar", "list",
                 "--start", tmr_start.strftime("%Y-%m-%dT00:00:00%z"),
                 "--end", tmr_end.strftime("%Y-%m-%dT00:00:00%z"), "--max", "50"])
    if r.returncode != 0:
        sys.exit(1)

    try:
        events = json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit(0)

    if not events:
        print("No events tomorrow. Silent.")
        sys.exit(0)

    print(f"Found {len(events)} event(s)")
    for ev in events:
        summary = ev.get("summary", "(no title)")
        s_raw, e_raw = ev.get("start", ""), ev.get("end", "")
        location, description = ev.get("location", ""), ev.get("description", "")

        try:
            ev_start = datetime.fromisoformat(s_raw) if "T" in s_raw else datetime.strptime(s_raw, "%Y-%m-%d").replace(tzinfo=tz, hour=9)
            ev_end   = datetime.fromisoformat(e_raw) if "T" in e_raw else ev_start + timedelta(hours=1)
        except (ValueError, TypeError):
            print(f"Skipping unparseable: {summary}")
            continue

        safe = "".join(c if c.isalnum() else "-" for c in summary[:30]).strip("-")
        date_str = ev_start.strftime("%Y%m%d")

        # Reminder: event - 2h (min 5 min from now)
        rem_time = ev_start - timedelta(hours=2)
        if rem_time <= now:
            rem_time = now + timedelta(minutes=5)

        rem_prompt = (f"Hatirlatma: Yarin saat {ev_start.strftime('%H:%M')} '{summary}' etkinligin var."
                      + (f" Konum: {location}." if location else "")
                      + (f" Notlar: {description[:200]}." if description else "")
                      + " Wiki'den ilgili bilgileri kontrol et ve baglamsal bir mesaj gonder.")
        create_oneshot(f"reminder_{safe}_{date_str}", rem_prompt, rem_time, skills=["google-workspace", "llm-wiki"])

        # Follow-up: event_end + 15min
        fu_time = ev_end + timedelta(minutes=15)
        if fu_time <= now:
            fu_time = now + timedelta(minutes=5)

        fu_prompt = (f"'{summary}' etkinligi yeni bitti mi Edel? "
                     + (f"Konum: {location}. " if location else "")
                     + "Eger bittiyse, 5N1K ile konuyu derinlestir. "
                     + "Cikardigin bilgileri wiki'ye kaydet. "
                     + "Eger hala devam ediyorsa 'Tamam, bitince haber ver!' de ve 30dk sonra tekrar sor. "
                     + "Eger cevap alamazsan etkinlik onemine gore karar ver.")
        create_oneshot(f"followup_{safe}_{date_str}", fu_prompt, fu_time, skills=["google-workspace", "llm-wiki"])

        print(f"  {summary} | reminder={rem_time.isoformat()} | followup={fu_time.isoformat()}")

    print(f"Done. {len(events)} event(s) processed.")

if __name__ == "__main__":
    main()