#!/usr/bin/env python3
"""Gmail unread check — no_agent script for cron delivery.
Uses Himalaya IMAP. Only shows emails from last 48h (avoids re-listing old ones)."""
import subprocess, sys
from datetime import datetime, timezone, timedelta

def run_himalaya(args, timeout=15):
    try:
        r = subprocess.run(["himalaya"] + args, capture_output=True, text=True, timeout=timeout)
        return r.stdout, r.returncode
    except Exception as e:
        return str(e), 1

out, rc = run_himalaya(["envelope", "list", "-f", "INBOX", "--page-size", "50"])
if rc != 0:
    sys.exit(1)

lines = out.strip().split('\n')

# Parse from bottom (newest first in himalaya)
# Format: | ID | FLAGS | SUBJECT | FROM | DATE |
cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
priority_keywords = ["edu.tr", "apa.org", "prolific", "upwork", "monitor"]
recent_priority = []

for line in lines:
    if not line.startswith('|') or '|-----|' in line or '| ID  |' in line:
        continue
    parts = [p.strip() for p in line.split('|')]
    if len(parts) < 6:
        continue
    
    date_str = parts[5]
    subject = parts[3]
    sender = parts[4]
    
    # Parse date - himalaya shows in format like "2026-07-10 08:07+00:00"
    try:
        date_clean = date_str.split('+')[0].split('-')[0].strip()
        msg_date = datetime.strptime(date_str[:16], "%Y-%m-%d %H:%M")
        msg_date = msg_date.replace(tzinfo=timezone.utc)
    except:
        continue
    
    if msg_date < cutoff:
        continue
    
    combined = (sender + ' ' + subject).lower()
    if any(k in combined for k in priority_keywords):
        sender_name = sender.split('<')[0].strip().strip('"') or sender
        recent_priority.append({'from': sender_name, 'subject': subject, 'date': date_str[:16]})

if not recent_priority:
    # Empty output = silent (no delivery)
    sys.exit(0)

print(f"📬 Son 48 saatte {len(recent_priority)} öncelikli e-posta:")
print()
for m in recent_priority:
    print(f"⭐ {m['from']} — {m['subject']}")
    print(f"   🕐 {m['date']}")
