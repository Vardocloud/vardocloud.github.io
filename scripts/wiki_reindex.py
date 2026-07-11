#!/usr/bin/env python3
"""
Wiki FTS5 Re-indexer — periodically re-indexes wiki directory
Run: python3 ~/.hermes/scripts/wiki_reindex.py
Schedule: daily at 04:00 or on-demand via /wiki-reindex

Uses file_hash to skip unchanged files — only new/modified files are reindexed.
"""
import sqlite3, os, re, hashlib, sys

WIKI_DIR = "/home/ubuntu/wiki"
DB_PATH = "/home/ubuntu/.hermes/state.db"

def run():
    db = sqlite3.connect(DB_PATH)

    # Ensure table exists
    db.executescript("""
        CREATE VIRTUAL TABLE IF NOT EXISTS wiki_fts USING fts5(
            path, title, content, tags, file_hash, last_indexed,
            tokenize='unicode61'
        );
    """)

    indexed = 0
    skipped = 0
    removed = 0
    errors = 0

    # Track which files exist on disk
    existing_paths = set()

    for root, dirs, files in os.walk(WIKI_DIR):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            fpath = os.path.join(root, fn)
            relpath = os.path.relpath(fpath, WIKI_DIR)
            existing_paths.add(relpath)

            try:
                raw = open(fpath, encoding="utf-8", errors="replace").read()
                title_match = re.match(r"^#\s+(.+)", raw)
                title = title_match.group(1).strip() if title_match else fn.replace(".md","")
                tags = " ".join(re.findall(r"(?:^|\s)#(\w+)", raw[:500]))[:200]
                fhash = hashlib.md5(raw.encode()).hexdigest()[:16]

                existing = db.execute("SELECT file_hash FROM wiki_fts WHERE path = ?", (relpath,)).fetchone()
                if existing and existing[0] == fhash:
                    skipped += 1
                    continue

                db.execute("DELETE FROM wiki_fts WHERE path = ?", (relpath,))
                db.execute("INSERT INTO wiki_fts (path, title, content, tags, file_hash, last_indexed) VALUES (?, ?, ?, ?, ?, datetime('now'))", (relpath, title, raw[:50000], tags, fhash))
                indexed += 1
            except Exception as e:
                errors += 1

    # Remove wiki_fts entries for files that no longer exist
    all_indexed = db.execute("SELECT path FROM wiki_fts").fetchall()
    for (path,) in all_indexed:
        if path not in existing_paths:
            db.execute("DELETE FROM wiki_fts WHERE path = ?", (path,))
            removed += 1

    db.commit()
    total = db.execute("SELECT COUNT(*) FROM wiki_fts").fetchone()[0]
    db.close()

    print("Wiki re-index: %d new, %d skipped, %d removed, %d errors. Total: %d" % (indexed, skipped, removed, errors, total))

if __name__ == "__main__":
    run()