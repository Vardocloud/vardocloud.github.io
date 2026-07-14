# Interactive Session Mail Processing Pattern

When Edel manually asks to process mails (not cron), the flow differs from the automated EKİP pipeline.
This is a HUMAN-IN-THE-LOOP pattern — no subagent delegation, no batch classification tables.

## When to Use
- Edel says "Gmail'deki Skool/APA maillerini işle"
- Edel says "mailleri kontrol et, fikir çıkar"
- Any manual, on-demand mail processing request

## Flow (5 Steps)

### 1. Search & List
```bash
ALL_PROXY="" python3 google_api.py gmail search 'from:skool.com newer_than:14d' --max 25 \
  | python3 -c "import sys,json; [print(f'{m[\"id\"]} | {m.get(\"date\",\"\")[:25]} | {m.get(\"subject\",\"\")[:120]}') for m in json.load(sys.stdin)]"
```
- `--max` NOT `--max-results` — the latter causes exit code 1
- Use `newer_than:14d` for 2-week window, `newer_than:7d` for weekly
- Pipe through Python to extract id|date|subject for readability

### 2. Categorize by Subject Line
- **Content mails:** Actual posts, lessons, announcements with substance
- **Notification mails:** "X new notifications since..." → SKIP
- **Login codes:** "is your Skool log in code" → SKIP
- **Membership confirmations:** "membership approved" → SKIP
- Signal ratio should be ~30-40%; if it's 10% or lower, widen the search window

### 3. Get Bodies of Valuable Ones
```bash
ALL_PROXY="" python3 google_api.py gmail get EMAIL_ID \
  | python3 -c "
import sys, json, re
d = json.load(sys.stdin)
body = d.get('body','')
if isinstance(body, dict):
    body = body.get('text','') or body.get('html','') or str(body)
body = re.sub(r'<[^>]*>', ' ', body)
body = re.sub(r'\s+', ' ', body)
print(body[:3000])
"
```
- `print(body[:3000])` gives enough to understand content without flooding context
- The regex `re.sub(r'<[^>]*>', ' ', body)` strips HTML tags
- `re.sub(r'\s+', ' ', body)` normalizes whitespace
- **CRITICAL:** Use `python3 -c` with inline script, NOT `execute_code` — the latter is blocked in some contexts

### 4. Synthesize in Turkish Conversational Format
- Use emoji headers (🎙️ 👥 💰 🤖 📊)
- Group by source/creator (Skool Official, Nate Herk, Umut Aktu, Julian Goldie)
- For each item: WHAT it is + WHY it matters + HOW it applies to Edel's context
- Include concrete numbers when available (pricing, member counts, revenue)
- NO tables unless specifically requested — prefer inline key:value with emoji bullets
- End with an action question: "hangisine dalmak istersin?"

### 5. Archive to NotebookLM
- Target: **🧠 Vanitas Hafıza Arşivi** (`6c7f3daa-1640-4fad-9917-ec44bc432e58`)
- Use `source_type=text` with structured markdown content
- Include: date range, mail count, signal ratio, key insights with bullet hierarchy
- Format title: `Skool Mail Hasadı - [Ay Yıl] Hafta [X]`

### 6. Finalize: Mark Read + Archive (7 Haz 2026)
When Edel asks for "gelen kutusu temiz olsun" or "mailleri okundu işaretle ve arşivle":

**Mark as read:** `--remove-labels UNREAD` per mail, or batch via Python script.
**Archive:** `--remove-labels INBOX` per mail (Gmail archive = remove INBOX label, mail moves to All Mail).
**Combined (preferred):** `--remove-labels "UNREAD,INBOX"` in ONE call (see SKILL.md pitfall).

**Reusable cleanup script** (write to `/tmp/email_cleanup.py` and run via terminal):
```python
#!/usr/bin/env python3
"""Gmail cleanup — mark as read + archive processed emails."""
import json, subprocess, os
GAPI = os.path.expanduser("~/.hermes/skills/productivity/google-workspace/scripts/google_api.py")
env = os.environ.copy(); env["ALL_PROXY"] = ""

def gmail_search(query, max_results=100):
    r = subprocess.run(["python3", GAPI, "gmail", "search", query, "--max", str(max_results)],
                       capture_output=True, text=True, timeout=30, env=env)
    try: return json.loads(r.stdout)
    except: return []

def gmail_modify(msg_id, remove_labels):
    return subprocess.run(
        ["python3", GAPI, "gmail", "modify", msg_id, "--remove-labels", ",".join(remove_labels)],
        capture_output=True, text=True, timeout=15, env=env
    ).returncode == 0

# Step 1: All UNREAD → read
unread = gmail_search("is:unread", 50)
for m in unread: gmail_modify(m["id"], ["UNREAD"])

# Step 2: All in INBOX (within time window) → archive
recent = gmail_search("newer_than:7d in:inbox", 100)
inbox_ids = [m["id"] for m in recent]
for mid in inbox_ids: gmail_modify(mid, ["INBOX"])

# Step 3: Optional — also archive older inbox mails for "temiz kalsın"
# older = gmail_search("in:inbox", 200)
# for m in older: gmail_modify(m["id"], ["INBOX"])
```

**Verification step (CRITICAL — see `--max` pitfall in SKILL.md):**
```bash
# Use --max 100+ when verifying, never trust a small result count as "inbox clean"
ALL_PROXY="" python3 google_api.py gmail search "in:inbox" --max 100
# "No messages found." = clean ✅
# JSON array of N = N remaining ❌
```

## Anti-Patterns (from Edel corrections)
- ❌ "40 mail var, 22'si ATLA" — sayı dökme, her mailin ne olduğunu anlat
- ❌ Tablo formatında toplu sınıflandırma
- ❌ Subagent'a devretme — Edel senin analizini istiyor
- ❌ Skool bildirim mailini "bildirim" deyip atlama — içerik ipucu varsa kaynağa git
- ❌ "Bu senin için şu anlama geliyor" bağlamını kurmadan ham bilgi aktarma
