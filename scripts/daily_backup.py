#!/usr/bin/env python3
"""Daily GitHub backup for ~/.hermes — no_agent cron script.
   Full + Incremental state.db (conversations) backup.
   
   Her gün 02:00'de çalışır:
   - Full messages + sessions dump (gzip) → son 7 gün korunur
   - Incremental messages (sadece yeni) → sonsuz korunur
   - Git push to vardocloud.github.io
   
   GERİ YÜKLEME:
   1. En son full backup'ı al:   gunzip -k state/full/msgs_YYYY-MM-DD.sql.gz
   2. Tüm incremental'ları uygula: gunzip state/incr/msgs_YYYY-MM-DD.sql.gz (tarih sırasıyla)
   3. SQLite'e yükle: sqlite3 state.db < msgs_YYYY-MM-DD.sql
   4. FTS index'leri rebuild et: sqlite3 state.db < rebuild_fts.sql
   5. Tam konuşma geçmişi geri gelir."""

import json, os, subprocess, sys, gzip, shutil, time
from datetime import date, timedelta
from pathlib import Path

HERMES = Path.home() / ".hermes"
BWS = HERMES / "bin" / "bws"
TOKEN_ID = "c601ddd0-cb11-46ae-a5ab-b48400d7bc11"
STATE_DB = HERMES / "state.db"
BACKUP_DIR = HERMES / "backups" / "state"
FULL_DIR = BACKUP_DIR / "full"
INCR_DIR = BACKUP_DIR / "incr"
FULL_DIR.mkdir(parents=True, exist_ok=True)
INCR_DIR.mkdir(parents=True, exist_ok=True)
TRACKER = BACKUP_DIR / ".last_msg_id"
RETENTION_DAYS = 14

os.chdir(str(HERMES))

# ── 0. state.db FULL backup (SADECE Pazar) ─────────────────────────
today = date.today().isoformat()
is_sunday = date.today().weekday() == 6  # 6 = Sunday

if STATE_DB.exists() and is_sunday:
    try:
        # Full messages dump — 600s timeout, haftada 1 kere
        msgs_path = FULL_DIR / f"msgs_{today}.sql"
        with open(msgs_path, "w") as f:
            subprocess.run(
                ["sqlite3", str(STATE_DB)],
                input=".mode insert messages\n.output stdout\nBEGIN TRANSACTION;\nSELECT * FROM messages ORDER BY id;\nCOMMIT;\n",
                stdout=f, timeout=600, text=True
            )

        # Full sessions dump
        sess_path = FULL_DIR / f"sessions_{today}.sql"
        with open(sess_path, "w") as f:
            subprocess.run(
                ["sqlite3", str(STATE_DB)],
                input=".mode insert sessions\n.output stdout\nBEGIN TRANSACTION;\nSELECT * FROM sessions ORDER BY id;\nCOMMIT;\n",
                stdout=f, timeout=120, text=True
            )

        # Compress both
        for p in [msgs_path, sess_path]:
            with open(p, "rb") as f_in:
                with gzip.open(str(p) + ".gz", "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            p.unlink()  # remove uncompressed

        msgs_size = (FULL_DIR / f"msgs_{today}.sql.gz").stat().st_size / 1024 / 1024
        sess_size = (FULL_DIR / f"sessions_{today}.sql.gz").stat().st_size / 1024 / 1024
        print(f"[FULL] {today}: msgs={msgs_size:.0f}MB sess={sess_size:.0f}MB")

        # Rotate old full backups (keep last RETENTION_DAYS)
        cutoff = date.today() - timedelta(days=RETENTION_DAYS)
        for f in FULL_DIR.glob("msgs_*.sql.gz"):
            fdate_str = f.stem.replace("msgs_", "").replace(".sql", "")
            try:
                fdate = date.fromisoformat(fdate_str)
                if fdate < cutoff:
                    f.unlink()
                    # Also remove corresponding sessions file
                    sess_file = FULL_DIR / f"sessions_{fdate_str}.sql.gz"
                    if sess_file.exists():
                        sess_file.unlink()
                    print(f"[ROTATE] Removed {fdate_str}")
            except ValueError:
                pass

    except Exception as e:
        print(f"[FULL] HATA: {e}")

# ── 1. state.db INCREMENTAL backup ─────────────────────────────────
if STATE_DB.exists():
    last_id = 0
    if TRACKER.exists():
        last_id = int(TRACKER.read_text().strip())

    try:
        result = subprocess.run(
            ["sqlite3", str(STATE_DB), "SELECT COALESCE(MAX(id),0) FROM messages"],
            capture_output=True, text=True, timeout=30
        )
        max_id = int(result.stdout.strip())

        if max_id > last_id:
            dump_path = INCR_DIR / f"msgs_{today}.sql"
            with open(dump_path, "w") as f:
                subprocess.run(
                    ["sqlite3", str(STATE_DB)],
                    input=f".mode insert messages\n.output stdout\nBEGIN TRANSACTION;\nSELECT * FROM messages WHERE id > {last_id};\nCOMMIT;\n",
                    stdout=f, timeout=120, text=True
                )

            with open(dump_path, "rb") as f_in:
                with gzip.open(str(dump_path) + ".gz", "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            dump_path.unlink()

            new_count = max_id - last_id
            print(f"[INCR] {new_count} yeni mesaj (id {last_id+1} -> {max_id})")
            TRACKER.write_text(str(max_id))
        else:
            print("[INCR] Yeni mesaj yok")
    except Exception as e:
        print(f"[INCR] HATA: {e}")

# ── 2. Git backup ──────────────────────────────────────────────────
# Get token from BWS
result = subprocess.run([str(BWS), "secret", "get", TOKEN_ID],
                        capture_output=True, text=True, timeout=15)
token = json.loads(result.stdout)["value"]

cred_path = Path.home() / ".git-credentials"
cred_path.write_text(f"https://isimgorulsunn%40gmail.com:{token}@github.com\n")
cred_path.chmod(0o600)

subprocess.run(["git", "config", "user.name", "Vanitas Backup"], capture_output=True)
subprocess.run(["git", "config", "user.email", "isimgorulsunn@gmail.com"], capture_output=True)
subprocess.run(["git", "config", "credential.helper", "store"], capture_output=True)

# Add all backup dirs + normal files
for d in ["backups/", "skills/", "scripts/", "wiki/", "config.yaml",
          ".gitignore", "AGENTS.md", "MEMORY.md", "SOUL.md", "CONTEXT.md"]:
    p = HERMES / d
    if p.exists():
        subprocess.run(["git", "add", d], capture_output=True, timeout=180)

# Check if anything changed
diff = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
if diff.returncode == 0:
    print("[SILENT]")
    sys.exit(0)

# Commit and push
today = date.today().isoformat()
subprocess.run(["git", "commit", "-m", f"Daily backup - {today}"], capture_output=True, timeout=120)
push = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, timeout=120)
print(push.stdout.strip()[-200:] if push.stdout else "Push OK")
