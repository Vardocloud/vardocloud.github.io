#!/usr/bin/env python3
"""
Gunluk Sentez — Daily Self-Learning Engine

Orchestrates daily knowledge synthesis:
1. Discover unprocessed raw content (transcripts, articles, papers, skool/)
2. Collect today's wiki changes (news/, skool/ outputs from other jobs)
3. NVIDIA DeepSeek V4 Flash cross-reference + wiki writing + memory archive

Runs: Daily at 23:00
Model: deepseek-ai/deepseek-v4-flash (NVIDIA)
Deliver: local (no message to Edel)
"""

import json
import os
import sys
import re
import datetime
from pathlib import Path
from openai import OpenAI

# --- Configuration ----------------------------------------------------------

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "/home/ubuntu/.hermes"))
WIKI_HOME = Path(os.environ.get("WIKI_PATH", "/home/ubuntu/wiki"))
STATE_FILE = HERMES_HOME / "data" / "sentez_state.json"
OGREME_DIR = WIKI_HOME / "ogrenme"
MEMORY_DIR = WIKI_HOME / "vanitas-memory"
LOG_FILE = WIKI_HOME / "log.md"
SCHEMA_FILE = WIKI_HOME / "SCHEMA.md"

# NVIDIA DeepSeek V4 Flash — fast and reliable
_KEY = os.environ.get("NVIDIA_API_KEY", "")
API_BASE = "https://integrate.api.nvidia.com/v1"
API_MODEL = "mistralai/mistral-small-4-119b-2603"

# Directories to scan for new unprocessed content
WATCH_DIRS = [
    WIKI_HOME / "raw" / "transcripts",
    WIKI_HOME / "raw" / "articles",
    WIKI_HOME / "raw" / "papers",
]

# Today's job output directories (created by Bundle, APA, Skool)
TODAY_WATCH = [
    WIKI_HOME / "news",
    WIKI_HOME / "skool",
]

# --- State Management --------------------------------------------------------

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "last_run": None,
        "processed_files": {},
        "total_runs": 0,
        "notebooklm_runs": 0,
    }

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

# --- Content Discovery -------------------------------------------------------

def discover_new_content(state):
    new_files = []
    for watch_dir in WATCH_DIRS:
        if not watch_dir.exists():
            continue
        for fpath in watch_dir.rglob("*"):
            if not fpath.is_file() or fpath.suffix not in (".md", ".txt", ".pdf"):
                continue
            rel_path = str(fpath.relative_to(WIKI_HOME))
            if rel_path not in state["processed_files"]:
                new_files.append(fpath)
    return new_files

def collect_today_changes():
    today = datetime.date.today()
    files = []
    for watch_dir in TODAY_WATCH:
        if not watch_dir.exists():
            continue
        for fpath in watch_dir.rglob("*"):
            if not fpath.is_file() or fpath.suffix not in (".md", ".txt", ".json"):
                continue
            mtime = datetime.datetime.fromtimestamp(fpath.stat().st_mtime).date()
            if mtime == today:
                files.append(fpath)
    return files

def read_recent_ogrenme(days=7):
    entries = []
    for i in range(days):
        d = datetime.date.today() - datetime.timedelta(days=i)
        fpath = OGREME_DIR / f"{d.isoformat()}.md"
        if fpath.exists():
            entries.append(f"=== {d.isoformat()} ===")
            entries.append(fpath.read_text()[:2000])
    return "\n\n".join(entries)

# --- NVIDIA API Call --------------------------------------------------------

def call_model(sys_prompt, user_content):
    """Call NVIDIA DeepSeek V4 Flash with timeout."""
    import httpx
    client = OpenAI(
        api_key=_KEY,
        base_url=API_BASE,
        timeout=httpx.Timeout(85.0, connect=20.0),
    )
    resp = client.chat.completions.create(
        model=API_MODEL,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.7,
        max_tokens=8192,
    )
    return resp.choices[0].message.content

def build_synthesis_prompt(date_str, new_content, today_files_content, recent_ogrenme, schema):
    today_files_text = "\n".join(today_files_content) if today_files_content else "None"
    return f"""Today is {date_str}.

## SOURCES

### A. New Raw Content (unprocessed)
{new_content if new_content else "None -- no new raw content today."}

### B. Today's Job Outputs
{today_files_text}

### C. Recent Learning History (last 7 days, truncated)
{recent_ogrenme}

### D. Wiki Schema (conventions reference)
{schema}

## INSTRUCTIONS

You MUST produce EXACTLY THREE sections separated by "=== SEPARATOR ===".

### Section 1: WIKI_INGEST (only if new content exists in A)
For each new piece of raw content, apply the Ingest procedure:
Format:
WIKI_INGEST
- source: [filename]
- entities: [[entity1]], [[entity2]]
- concepts: [[concept1]]
- pages_to_create: [page names and paths]
- pages_to_update: [page names and paths]
- cross_references: [[page1]] <-> [[page2]]
=== SEPARATOR ===

### Section 2: DAILY_NOTE
Today's learning note for ogrenme/{date_str}.md
Write in Turkish language -- this is for Edel's wiki.
Format:
DAILY_NOTE
## <AGENDA>
## <PSYCHOLOGY>
## <TECH/AI>
## <ECONOMY> (if applicable)
## <CROSS-REFERENCES> (min 3-5, use [[wikilink]] syntax)
## <CONVERSATION SEEDS> (min 3)
=== SEPARATOR ===

### Section 3: MEMORY_ENTRIES
Top 3-5 most important learnings, formatted for vanitas-memory/.
Each entry with YAML frontmatter.
MEMORY_ENTRIES
---
title: [brief title]
created: {date_str}
type: lighthouse-archive
tags: [tag1, tag2]
---
[1-2 sentence learning description]
---
"""

def parse_response(response):
    sections = {"wiki_ingest": None, "daily_note": None, "memory_entries": None}
    current_section = None
    lines = []
    for line in response.split("\n"):
        stripped = line.strip()
        if stripped == "WIKI_INGEST":
            current_section = "wiki_ingest"
            lines = []
        elif stripped == "DAILY_NOTE":
            if current_section and lines:
                sections[current_section] = "\n".join(lines)
            current_section = "daily_note"
            lines = []
        elif stripped == "MEMORY_ENTRIES":
            if current_section and lines:
                sections[current_section] = "\n".join(lines)
            current_section = "memory_entries"
            lines = []
        elif stripped == "=== SEPARATOR ===":
            if current_section and lines:
                sections[current_section] = "\n".join(lines)
            current_section = None
            lines = []
        else:
            lines.append(line)
    if current_section and lines:
        sections[current_section] = "\n".join(lines)
    return sections

# --- Wiki Writing ------------------------------------------------------------

def write_ogrenme(content, date_str):
    OGREME_DIR.mkdir(parents=True, exist_ok=True)
    fpath = OGREME_DIR / f"{date_str}.md"
    if content and content.startswith("DAILY_NOTE"):
        content = content[len("DAILY_NOTE"):].strip()
    fpath.write_text(f"# Daily Synthesis -- {date_str}\n\n{content}\n")
    return fpath

def write_memory(entries, date_str):
    if not entries:
        return []
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    raw_blocks = entries.split("\n---\n")
    for i, block in enumerate(raw_blocks):
        block = block.strip()
        if not block:
            continue
        if not block.startswith("---"):
            block = "---\n" + block
        elif not block.startswith("---\n"):
            block = "---\n" + block[3:]
        title_line = ""
        for l in block.split("\n"):
            if l.startswith("title:"):
                title_line = l.replace("title:", "").strip().strip('"').strip("'")
                break
        safe_title = re.sub(r'[^a-z0-9]+', '-', title_line.lower())[:40] if title_line else "synthesis"
        fname = f"{date_str}-{safe_title}-{i}.md"
        fpath = MEMORY_DIR / fname
        if not block.endswith("\n"):
            block += "\n"
        fpath.write_text(block)
        written.append(fpath)
    return written

def update_log(entries, date_str):
    summary_items = []
    if entries.get("daily_note"):
        summary_items.append(f"Created ogrenme/{date_str}.md -- daily synthesis")
    if entries.get("wiki_ingest"):
        for line in entries["wiki_ingest"].split("\n"):
            if line.strip().startswith("- pages_to_create") or line.strip().startswith("- pages_to_update"):
                summary_items.append(line.strip())
    if entries.get("memory_entries"):
        count = entries["memory_entries"].count("---")
        summary_items.append(f"Wrote {count} memory entries to vanitas-memory/")
    log_entry = f"\n## {date_str} | synthesis | Daily Self-Learning\n"
    for item in summary_items:
        log_entry += f"- {item}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    return log_entry

# --- Main --------------------------------------------------------------------

def main():
    date_str = datetime.date.today().isoformat()
    state = load_state()
    print(f"=== Gunluk Sentez -- {date_str} ===")

    print("\n[Phase 1] Scanning for new raw content...")
    new_files = discover_new_content(state)
    new_content_summary = ""
    if new_files:
        print(f"  Found {len(new_files)} new file(s):")
        for f in new_files:
            rel = str(f.relative_to(WIKI_HOME))
            print(f"    - {rel}")
            content = f.read_text(errors="replace")[:15000]
            new_content_summary += f"\n### {rel}\n{content}\n"
    else:
        print("  No new raw content found.")

    print("\n[Phase 2] Collecting today's job outputs...")
    today_files = collect_today_changes()
    today_content = []
    for f in today_files:
        rel = str(f.relative_to(WIKI_HOME))
        content = f.read_text(errors="replace")[:3000]
        today_content.append(f"=== {rel} ===\n{content}")
        print(f"    - {rel}")
    if not today_files:
        print("  No files modified today.")

    print("\n[Phase 3] Reading recent context...")
    recent = read_recent_ogrenme(days=7)
    schema = SCHEMA_FILE.read_text() if SCHEMA_FILE.exists() else ""

    print(f"\n[Phase 4] Calling {API_MODEL}...")
    prompt = build_synthesis_prompt(
        date_str, new_content_summary, today_content, recent, schema
    )
    try:
        response = call_model(
            sys_prompt=f"You are Vanitas's daily synthesis engine. Today's date is {date_str}. Output THREE sections: WIKI_INGEST, DAILY_NOTE, MEMORY_ENTRIES separated by ---. Write DAILY_NOTE in Turkish. NEVER send anything to Edel (deliver=local).",
            user_content=prompt,
        )
    except Exception as e:
        print(f"  ERROR: API call failed: {e}")
        sys.exit(1)
    print(f"  Response length: {len(response)} chars")

    debug_dir = Path("/tmp/sentez_debug")
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / f"{date_str}.txt").write_text(response)

    print("\n[Phase 5] Parsing response...")
    sections = parse_response(response)
    if sections["daily_note"]:
        fpath = write_ogrenme(sections["daily_note"], date_str)
        print(f"  Wrote: {fpath}")
    if sections["memory_entries"]:
        paths = write_memory(sections["memory_entries"], date_str)
        for p in paths:
            print(f"  Memory: {p}")
    if sections["wiki_ingest"]:
        log_entry = update_log(sections, date_str)
        print(f"  Log: {log_entry.strip()}")
    else:
        update_log(sections, date_str)

    print("\n[Phase 6] Updating state...")
    state["last_run"] = datetime.datetime.now().isoformat()
    state["total_runs"] = state.get("total_runs", 0) + 1
    if new_files:
        for f in new_files:
            rel = str(f.relative_to(WIKI_HOME))
            state["processed_files"][rel] = datetime.datetime.now().isoformat()
    save_state(state)
    print(f"\n=== Complete: {date_str} ===")

if __name__ == "__main__":
    main()
