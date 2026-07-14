#!/usr/bin/env python3
"""OpenCode Pollinations wrapper — silent opencode run output extracted from SQLite DB.

Usage: 
  OPENCODE_POLLINATIONS_API_KEY=*** python3 oc_wrapper.py analist "prompt"
  
Roles: kodcu (minimax), analist (glm), yazar (gpt-5.4-mini), yardimci (gemma)

The script inherits OPENCODE_POLLINATIONS_API_KEY from the calling environment.
If using a proxy that auto-injects the key, set any non-empty value.
"""
import sys, sqlite3, json, subprocess, time, os

DB = os.path.expanduser('~/.local/share/opencode/opencode.db')
MODEL_MAP = {
    'kodcu': 'minimax',
    'analist': 'glm',
    'yazar': 'gpt-5.4-mini',
    'yardimci': 'gemma',
}

def get_last_session_id():
    db = sqlite3.connect(DB)
    row = db.execute("SELECT id FROM session ORDER BY time_created DESC LIMIT 1").fetchone()
    return row[0] if row else None

def get_response(session_id):
    db = sqlite3.connect(DB)
    parts = db.execute("""
        SELECT p.data FROM part p 
        JOIN message m ON p.message_id = m.id 
        WHERE m.session_id=? AND json_extract(m.data, '$.role')='assistant'
        ORDER BY p.rowid
    """, (session_id,)).fetchall()
    
    texts = []
    for (data,) in parts:
        d = json.loads(data)
        if d.get('type') == 'text' and d.get('text'):
            texts.append(d['text'].strip())
    return '\n'.join(texts)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: oc_wrapper.py <rol> <prompt>")
        print(f"Roles: {list(MODEL_MAP.keys())}")
        sys.exit(1)
    
    rol = sys.argv[1]
    prompt = ' '.join(sys.argv[2:])
    model = MODEL_MAP.get(rol, 'minimax')
    
    sid_before = get_last_session_id()
    
    subprocess.run(
        ['opencode', 'run', '-m', f'pollinations/{model}', prompt],
        capture_output=True, text=True, timeout=120
    )
    
    time.sleep(2)  # DB write delay
    
    sid_after = get_last_session_id()
    if sid_after and sid_after != sid_before:
        response = get_response(sid_after)
        if response:
            print(response)
        else:
            print(f"[{rol}/{model}] No text in response (session: {sid_after[:20]}...)")
    else:
        print(f"[{rol}/{model}] No session created. Check OPENCODE_POLLINATIONS_API_KEY.")
