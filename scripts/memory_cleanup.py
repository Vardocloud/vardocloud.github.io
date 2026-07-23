#!/usr/bin/env python3
"""memory_cleanup.py — TTL-based MEMORY.md temizlik + long-tip wiki arşivi.
   no_agent cron script (haftada 1).
   
   Expired entry'leri: long → wiki/vanitas-memory arşivi, sonra sil.
   short/medium → direkt sil. MEMORY.md'den ve MEMORY_META.json'dan çıkar."""

import json, os, time, re, sys
from pathlib import Path
from datetime import datetime

HERMES = Path.home() / ".hermes"
META_PATH = HERMES / "memories" / "MEMORY_META.json"
MEMORY_MD = HERMES / "memories" / "MEMORY.md"
ARCHIVE_DIR = Path.home() / "wiki" / "vanitas-memory"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

now = time.time()

# ── 1. Read META ────────────────────────────────────────────────────
if not META_PATH.exists():
    print("[SILENT]")
    sys.exit(0)

with open(META_PATH) as f:
    data = json.load(f)
entries = data.get("entries", data)

# ── 2. Find expired entries ─────────────────────────────────────────
expired = []  # list of dicts: {id, entry, expiry_ts}
for eid, e in list(entries.items()):
    if not isinstance(e, dict):
        continue

    # Determine expiry timestamp
    if "expires_date" in e:
        try:
            expiry_ts = datetime.fromisoformat(e["expires_date"]).timestamp()
        except (ValueError, TypeError):
            expiry_ts = 0
    elif "added_ts" in e and "ttl_days" in e:
        expiry_ts = e["added_ts"] + (e["ttl_days"] * 86400)
    else:
        continue

    if expiry_ts > 0 and expiry_ts < now:
        expired.append({"id": eid, "entry": e, "expiry_ts": expiry_ts})

if not expired:
    print(f"[SILENT] {len(entries)} kayit, expired yok")
    sys.exit(0)

# ── 3. Process: archive long, collect previews for MEMORY.md cleanup ─
expired_ids = []
expired_previews = set()
archived_count = 0

for x in expired:
    eid = x["id"]
    e = x["entry"]
    expiry_ts = x["expiry_ts"]
    expired_ids.append(eid)

    entry_type = e.get("type", "unknown")
    target = e.get("target", "memory")
    preview = e.get("content_preview", "")[:80]
    added_ts = e.get("added_ts", 0)
    added_date = time.strftime("%Y-%m-%d", time.localtime(added_ts)) if added_ts else "unknown"

    # Collect preview fragments for line matching
    if preview:
        for p in [preview[:60], preview[:40], preview[:30]]:
            if p.strip():
                expired_previews.add(p.strip())

    if entry_type == "long":
        # Archive to wiki/vanitas-memory/
        safe_title = re.sub(r'[^a-z0-9]', '-', preview.lower()[:40])
        safe_title = re.sub(r'-+', '-', safe_title).strip('-')[:50]
        if not safe_title:
            safe_title = f"entry-{eid[:8]}"

        archive_path = ARCHIVE_DIR / f"{added_date}-{safe_title}.md"
        if not archive_path.exists():
            archive_path.write_text(
                f"# Memory Archive\n\n"
                f"- **Archived:** {time.strftime('%Y-%m-%d %H:%M', time.localtime(now))}\n"
                f"- **Expired:** {time.strftime('%Y-%m-%d %H:%M', time.localtime(expiry_ts))}\n"
                f"- **Source:** {target}\n"
                f"- **Preview:** {preview}\n"
            )
            archived_count += 1

# ── 4. Clean MEMORY.md — remove lines matching expired previews ──────
removed_count = 0
if MEMORY_MD.exists() and expired_previews:
    lines = MEMORY_MD.read_text().strip().split("\n")
    new_lines = []
    for line in lines:
        if any(ep in line for ep in expired_previews):
            removed_count += 1
        else:
            new_lines.append(line)

    MEMORY_MD.write_text("\n".join(new_lines).strip() + "\n" if new_lines else "")
    print(f"[CLEAN] MEMORY.md: {removed_count} expired satir temizlendi")

# ── 5. Remove from META ─────────────────────────────────────────────
for eid in expired_ids:
    del entries[eid]

# Save META
if isinstance(data.get("entries"), dict):
    data["entries"] = entries
else:
    data = entries  # old flat format

with open(META_PATH, "w") as f:
    json.dump(data, f, indent=2)

print(f"[DONE] {archived_count} arsivlendi, {len(expired)} silindi, {len(entries)} aktif kayit")
