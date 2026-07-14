#!/usr/bin/env python3
"""
wiki_to_notebooklm.py — Backfill wiki pages to NotebookLM.

Usage:
  python3 wiki_to_notebooklm.py --list           # List pending wiki pages not in NotebookLM
  python3 wiki_to_notebooklm.py --add <path>      # Add a specific wiki page
  python3 wiki_to_notebooklm.py --all             # Add all wiki pages not yet in NotebookLM
  python3 wiki_to_notebooklm.py --notebook <id>   # Specify notebook (default: Vanitas AI Araştırmaları)

Tracks processed pages in ~/.hermes/data/wiki_notebooklm_index.json
"""
import json
import os
import subprocess
import sys

DATA_DIR = os.path.expanduser("~/.hermes/data")
INDEX_FILE = os.path.join(DATA_DIR, "wiki_notebooklm_index.json")
WIKI_DIR = os.path.expanduser("~/wiki")
NLM_BIN = os.path.expanduser("~/.local/bin/nlm")

# Default notebook: Vanitas AI Araştırmaları
DEFAULT_NOTEBOOK = "e4944538-d981-4dab-adeb-7dbef4f8deec"

def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE) as f:
            return json.load(f)
    return {"notebook_id": DEFAULT_NOTEBOOK, "processed": []}

def save_index(index):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)

def find_wiki_pages():
    """Find all markdown files in the wiki skool and vanitas-memory dirs."""
    pages = []
    for root, dirs, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith(".md") and not f.startswith("index"):
                path = os.path.join(root, f)
                rel = os.path.relpath(path, WIKI_DIR)
                pages.append((rel, path))
    return sorted(pages)

def is_processed(index, rel_path):
    return rel_path in index["processed"]

def add_to_notebook(file_path, title=None, notebook_id=None):
    """Add a wiki page to NotebookLM."""
    nb = notebook_id or DEFAULT_NOTEBOOK
    
    # Generate title from filename if not provided
    if not title:
        basename = os.path.splitext(os.path.basename(file_path))[0]
        title = basename.replace("-", " ").replace("_", " ").title()
    
    cmd = [NLM_BIN, "source", "add", nb, "--file", file_path, 
           "--title", title, "--wait", "--wait-timeout", "120"]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def list_pending():
    index = load_index()
    pages = find_wiki_pages()
    
    pending = [(rel, path) for rel, path in pages if not is_processed(index, rel)]
    processed_count = sum(1 for rel, _ in pages if is_processed(index, rel))
    
    print(f"📊 NotebookLM: {DEFAULT_NOTEBOOK}")
    print(f"   Toplam wiki sayfası: {len(pages)}")
    print(f"   İşlenmiş: {processed_count}")
    print(f"   Bekleyen: {len(pending)}\n")
    
    for rel, path in pending:
        size = os.path.getsize(path)
        print(f"  ⏳ {rel} ({size} bytes)")
    
    return pending

def add_single(file_path, notebook_id=None):
    index = load_index()
    rel = os.path.relpath(file_path, WIKI_DIR)
    
    title = os.path.splitext(os.path.basename(file_path))[0]
    title = title.replace("-", " ").replace("_", " ").title()
    
    print(f"📤 Adding: {rel}")
    success, stdout, stderr = add_to_notebook(file_path, title, notebook_id)
    
    if success:
        if rel not in index["processed"]:
            index["processed"].append(rel)
        save_index(index)
        print(f"   ✅ SUCCESS: {stdout}")
    else:
        print(f"   ❌ FAILED: {stderr}")
    
    return success

def add_all(notebook_id=None):
    index = load_index()
    pages = find_wiki_pages()
    
    pending = [(rel, path) for rel, path in pages if not is_processed(index, rel)]
    
    if not pending:
        print("✅ Tüm wiki sayfaları zaten NotebookLM'de.")
        return True
    
    print(f"📤 Toplu backfill başlıyor: {len(pending)} sayfa\n")
    
    success_count = 0
    fail_count = 0
    
    for i, (rel, path) in enumerate(pending, 1):
        title = os.path.splitext(os.path.basename(path))[0]
        title = title.replace("-", " ").replace("_", " ").title()
        
        print(f"[{i}/{len(pending)}] {rel}")
        ok, stdout, stderr = add_to_notebook(path, title, notebook_id)
        
        if ok:
            index["processed"].append(rel)
            success_count += 1
            print(f"   ✅")
        else:
            fail_count += 1
            print(f"   ❌ {stderr[:100]}")
    
    save_index(index)
    print(f"\n📊 Sonuç: {success_count} başarılı, {fail_count} başarısız")
    return fail_count == 0

if __name__ == "__main__":
    if "--list" in sys.argv:
        list_pending()
    elif "--add" in sys.argv:
        idx = sys.argv.index("--add")
        if idx + 1 < len(sys.argv):
            add_single(sys.argv[idx + 1])
        else:
            print("❌ --add <path> gerekiyor")
    elif "--all" in sys.argv:
        nb = None
        if "--notebook" in sys.argv:
            idx = sys.argv.index("--notebook")
            nb = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        add_all(nb)
    else:
        list_pending()
