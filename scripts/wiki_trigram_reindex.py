#!/usr/bin/env python3
"""wiki_trigram_reindex.py — Rebuild wiki_fts_trigram FTS5 index from wiki files.
   no_agent cron script (günlük).
   
   Creates a trigram tokenizer FTS5 table parallel to wiki_fts.
   Trigram handles Turkish morphology better than unicode61:
   - "taşıma" matches "taşı", "taşımak", "taşıma"
   - No wildcard hacks needed for Turkish words"""

import sqlite3, os, sys, time, re
from pathlib import Path

STATE_DB = Path.home() / ".hermes" / "state.db"
WIKI_DIR = Path.home() / "wiki"

def recreate_trigram_index():
    conn = sqlite3.connect(str(STATE_DB))
    c = conn.cursor()
    
    # Check if trigram table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_fts_trigram'")
    exists = c.fetchone() is not None
    
    if exists:
        # Drop and recreate
        c.execute("DROP TABLE IF EXISTS wiki_fts_trigram")
        conn.commit()
    
    # Create with trigram tokenizer — same schema as wiki_fts
    c.execute("""
        CREATE VIRTUAL TABLE wiki_fts_trigram USING fts5(
            path,
            title,
            content,
            tags,
            file_hash,
            last_indexed,
            tokenize='trigram'
        )
    """)
    conn.commit()
    
    # Get all wiki files and index them
    md_files = sorted(WIKI_DIR.rglob("*.md"))
    indexed = 0
    errors = 0
    
    for fpath in md_files:
        rel_path = str(fpath.relative_to(WIKI_DIR.parent))
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            errors += 1
            continue
        
        # Extract title (first # heading or filename)
        title = ""
        for line in text.split("\n"):
            if line.startswith("# ") and not line.startswith("## "):
                title = line[2:].strip()
                break
        if not title:
            title = fpath.stem.replace("-", " ").title()
        
        # Extract tags from content (lines matching #tag)
        tags = " ".join(re.findall(r'(?<!\w)#(\w[\w-]*)', text))
        
        # File hash (simple mtime-based)
        file_hash = str(int(fpath.stat().st_mtime))
        last_indexed = time.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            c.execute(
                "INSERT INTO wiki_fts_trigram (path, title, content, tags, file_hash, last_indexed) VALUES (?, ?, ?, ?, ?, ?)",
                (rel_path, title, text, tags, file_hash, last_indexed)
            )
            indexed += 1
        except Exception as e:
            errors += 1
    
    conn.commit()
    conn.close()
    
    return indexed, errors

indexed, errors = recreate_trigram_index()
print(f"[DONE] wiki_fts_trigram: {indexed} dosya indekslendi, {errors} hata")
