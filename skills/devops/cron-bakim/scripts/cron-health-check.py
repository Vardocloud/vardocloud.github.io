#!/usr/bin/env python3
"""Cron Health Check — no_agent watchdog for cron job failures.

Reads ~/.hermes/cron/jobs.json every run, detects errors and anomalies.
Only outputs if something is wrong (silent when healthy).
Delivered to Edel's channel as native Telegram message when issues found.

Usage: python3 ~/.hermes/scripts/cron-health-check.py
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

CRON_JSON = os.path.expanduser("~/.hermes/cron/jobs.json")
STALE_THRESHOLD_HOURS = 28

def load_jobs():
    with open(CRON_JSON) as f:
        data = json.load(f)
    return data.get("jobs", [])

def parse_timestamp(ts_str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str)
    except (ValueError, TypeError):
        return None

def format_age(ts):
    now = datetime.now(timezone.utc)
    diff = now - ts
    if diff.days > 0:
        return f"{diff.days}g {diff.seconds // 3600}s"
    elif diff.seconds >= 3600:
        return f"{diff.seconds // 3600}s {diff.seconds % 3600 // 60}dk"
    elif diff.seconds >= 60:
        return f"{diff.seconds // 60}dk"
    else:
        return f"{diff.seconds}s"

def check_jobs(jobs):
    alerts = []
    now = datetime.now(timezone.utc)

    for job in jobs:
        name = job.get("name", job.get("id", "???"))
        job_id = job.get("id", "")
        last_status = job.get("last_status")
        last_error = job.get("last_error")
        last_delivery_error = job.get("last_delivery_error")
        last_run_at = parse_timestamp(job.get("last_run_at"))
        enabled = job.get("enabled", True)
        state = job.get("state", "")

        if not enabled or state == "paused":
            continue

        if last_status == "error":
            age = format_age(last_run_at) if last_run_at else "bilinmiyor"
            error_detail = ""
            if last_error:
                error_detail = last_error[:300]
            alerts.append(f"🔴 **{name}** — `error` (son çalışma: {age})")
            if error_detail:
                alerts.append(f"   └ Hata: `{error_detail}`")

        if last_delivery_error and last_delivery_error != "None":
            age = format_age(last_run_at) if last_run_at else "bilinmiyor"
            alerts.append(f"🟡 **{name}** — teslimat hatası (son çalışma: {age})")
            alerts.append(f"   └ {last_delivery_error[:300]}")

        if last_run_at and enabled and state != "paused":
            stale_diff = now - last_run_at
            if stale_diff > timedelta(hours=STALE_THRESHOLD_HOURS):
                schedule = job.get("schedule", "")
                if schedule:
                    age = format_age(last_run_at)
                    alerts.append(f"🟠 **{name}** — {age}'dir çalışmamış (muhtemelen takılı kaldı)")
                    if last_status == "error":
                        alerts[-1] = alerts[-1].replace("🟠", "🔴").replace("takılı kaldı", "hatalı ve çalışmıyor")

    return alerts

def main():
    try:
        jobs = load_jobs()
    except FileNotFoundError:
        print("[SILENT]", flush=True)
        return
    except json.JSONDecodeError as e:
        print(f"🔴 Cron health check: jobs.json bozuk — {e}", flush=True)
        return

    alerts = check_jobs(jobs)

    if not alerts:
        print("[SILENT]", flush=True)
        return

    print("🩺 **Cron Sağlık Taraması**", flush=True)
    print(f"_{len(alerts)} sorun tespit edildi_", flush=True)
    print("", flush=True)
    for alert in alerts:
        print(alert, flush=True)

    total = len(jobs)
    healthy = sum(1 for j in jobs if j.get("last_status") == "ok" and j.get("enabled", True))
    print("", flush=True)
    print(f"📊 {healthy}/{total} job sağlıklı çalışıyor.", flush=True)

if __name__ == "__main__":
    main()
